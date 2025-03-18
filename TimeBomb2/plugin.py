###
# Copyright (c) 2010, quantumlemur
# Copyright (c) 2020, oddluck <oddluck@riseup.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import time
import string
import random
import math
import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircdb as ircdb
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.schedule as schedule
import supybot.callbacks as callbacks
import supybot.registry as registry
import supybot.conf as conf


class TimeBomb(callbacks.Plugin):
    """
    Mais um plugin bomba-relógio.
    """

    threaded = True

    def __init__(self, irc):
        self.__parent = super(TimeBomb, self)
        self.__parent.__init__(irc)
        self.rng = random.Random()
        self.rng.seed()
        self.bombs = {}
        self.lastBomb = ""
        self.talktimes = {}

    def doPrivmsg(self, irc, msg):
        self.talktimes[msg.nick] = time.time()

    def doJoin(self, irc, msg):
        if self.registryValue("joinIsActivity", msg.args[0]):
            self.talktimes[msg.nick] = time.time()

    class Bomb:
        def __init__(
            self,
            irc,
            victim,
            wires,
            detonateTime,
            goodWire,
            channel,
            sender,
            showArt,
            showCorrectWire,
            debug,
        ):
            self.victim = victim
            self.detonateTime = detonateTime
            self.wires = wires
            self.goodWire = goodWire
            self.active = True
            self.channel = channel
            self.sender = sender
            self.irc = irc
            self.showArt = showArt
            self.showCorrectWire = showCorrectWire
            self.debug = debug
            self.thrown = False
            self.rethrown = False
            self.responded = False
            self.rng = random.Random()
            self.rng.seed()

            def get(group):
                v = group.getSpecific(channel=channel)
                return v()

            try:
                self.command_char = get(conf.supybot.reply.whenAddressedBy.chars)[0]
            except:
                self.command_char = ""
            if self.debug:
                self.irc.reply("Acabei de criar uma bomba em {}.".format(channel))

            def detonate():
                self.detonate(irc)

            schedule.addEvent(
                detonate,
                time.time() + self.detonateTime,
                "{}_bomb".format(self.channel),
            )
            s = (
                "enfia uma bomba nas calças de {}. O temporizador está definido"
                " para {} segundos! Há {} fios. Eles são: {}.".format(
                    self.victim,
                    self.detonateTime,
                    len(wires),
                    utils.str.commaAndify(wires),
                )
            )
            self.irc.queueMsg(ircmsgs.action(self.channel, s))
            self.irc.queueMsg(
                ircmsgs.privmsg(
                    self.channel,
                    "{}, tenta deasrmar a bomba usando o comando: '{}cutwire"
                    " \x02côr\x02'".format(self.victim, self.command_char),
                )
            )

            if self.victim == irc.nick:
                time.sleep(1)
                cutWire = self.rng.choice(self.wires)
                self.irc.queueMsg(
                    ircmsgs.privmsg(self.channel, "$cutwire {}".format(cutWire))
                )
                time.sleep(1)
                self.cutwire(self.irc, cutWire)

        def defuse(self):
            if not self.active:
                return

            self.active = False
            self.thrown = False
            schedule.removeEvent("{}_bomb".format(self.channel))

        def cutwire(self, irc, cutWire):
            self.cutWire = cutWire
            self.responded = True
            specialWires = False

            if self.rng.randint(1, len(self.wires)) == 1:
                specialWires = True

            if self.cutWire.lower() == "potato" and specialWires:
                self.irc.queueMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "{} transformou a bomba numa batata! Isto tornou-a praticamente"
                        " inofensiva e ligeiramente {}.".format(
                            self.victim, self.goodWire
                        ),
                    )
                )
                self.defuse()
            elif self.cutWire.lower() == "pizza" and specialWires:
                self.irc.queueMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "{} transformou a bomba numa pizza! As suas calças ficaram"
                        " estragadas com a pizza enfiada nelas, mas pelo menos"
                        " não explodiram.".format(self.victim),
                    )
                )
                self.defuse()
            elif self.goodWire.lower() == self.cutWire.lower():
                self.irc.queueMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "{} cortou o fio {}! Isto desarmou a bomba!".format(
                            self.victim, self.cutWire
                        ),
                    )
                )

                if self.victim.lower() != self.sender.lower():
                    self.irc.queueMsg(
                        ircmsgs.privmsg(
                            self.channel,
                            "{} rapidamente rearma a bomba e atira-a de volta"
                            " a {} com apenas alguns segundos no relógio!"
                            " {} tenta desactivar a bomba com o comando '{}cutwire \x02côr\x02'".format(
                                self.victim, self.sender, self.sender,self.command_char
                            ),
                        )
                    )
                    tmp = self.victim
                    self.victim = self.sender
                    self.sender = tmp
                    self.thrown = True
                    self.rethrown = True
                    schedule.rescheduleEvent(
                        "{}_bomb".format(self.channel), time.time() + 10
                    )

                    if self.victim == irc.nick:
                        self.defuse()
                else:
                    self.defuse()
            else:
                schedule.removeEvent("{}_bomb".format(self.channel))
                self.detonate(irc)

        def duck(self, irc, ducker):
            if self.thrown and ircutils.nickEqual(self.victim, ducker):
                self.irc.queueMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "{} baixa-se! A bomba falha e explode inofensivamente"
                        " a alguns metros de distância.".format(self.victim),
                    )
                )
                self.defuse()

        def detonate(self, irc):
            self.active = False
            self.thrown = False
            if self.showCorrectWire:
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "Devias ter ido para o fio {}!".format(self.goodWire),
                    )
                )

            if self.showArt:
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "\x031,1.....\x0315,1_.\x0314,1-^^---....,\x0315,1,-_\x031,1.......",
                    )
                )
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "\x031,1.\x0315,1_--\x0314,1,.';,`.,';,.;;`;,.\x0315,1--_\x031,1...",
                    )
                )
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "\x0315,1<,.\x0314,1;'`\".,;`..,;`*.,';`.\x0315,1;'>)\x031,1.",
                    )
                )
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "\x0315,1I.:;\x0314,1.,`;~,`.;'`,.;'`,..\x0315,1';`I\x031,1.",
                    )
                )
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "\x031,1.\x0315,1\\_.\x0314,1`'`..`';.,`';,`';,\x0315,1_../\x031,1..",
                    )
                )
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "\x031,1....\x0315,1```\x0314,1--. . , ;"
                        " .--\x0315,1'''\x031,1.....",
                    )
                )
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "\x031,1..........\x034,1I\x031,1.\x038,1I\x037,1I\x031,1.\x038,1I\x034,1I\x031,1...........",
                    )
                )
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "\x031,1..........\x034,1I\x031,1.\x037,1I\x038,1I\x031,1.\x037,1I\x034,1I\x031,1...........",
                    )
                )
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "\x031,1.......,\x034,1-=\x034,1II\x037,1..I\x034,1.I=-,\x031,1........",
                    )
                )
                self.irc.sendMsg(
                    ircmsgs.privmsg(
                        self.channel,
                        "\x031,1.......\x034,1`-=\x037,1#$\x038,1%&\x037,1%$#\x034,1=-'\x031,1........",
                    )
                )
            else:
                self.irc.sendMsg(ircmsgs.privmsg(self.channel, "KABOOM!"))
            if self.showCorrectWire:
                self.irc.queueMsg(
                    ircmsgs.kick(
                        self.channel,
                        self.victim,
                        "BOOM! Devias ter ido para o fio {}!".format(
                            self.goodWire
                        ),
                    )
                )
            else:
                self.irc.queueMsg(ircmsgs.kick(self.channel, self.victim, "BOOM!"))

            def reinvite():
                if self.victim not in irc.state.channels[self.channel].users:
                    self.irc.queueMsg(ircmsgs.invite(self.victim, self.channel))

            if not self.responded:
                schedule.addEvent(reinvite, time.time() + 5)

    def _canBomb(self, irc, channel, sender, victim, replyError):
        if sender.lower() in self.registryValue("exclusions", channel):
            if replyError:
                irc.reply(
                    "Não podes bombardear ninguém porque estás excluído de ser bombardeado."
                )
            return False

        if sender not in irc.state.channels[channel].users:
            if replyError:
                irc.error(
                    format(
                        "É preciso estar em {} para fazer uma bomba-relógio ali.".format(channel),
                        Raise=True,
                    )
                )
            return False
        bombHistoryOrig = self.registryValue("bombHistory", channel)
        bombHistory = []
        senderHostmask = irc.state.nickToHostmask(sender)
        (nick, user, host) = ircutils.splitHostmask(senderHostmask)
        senderMask = ("{}@{}".format(user, host)).lower()
        victim = victim.lower()
        now = int(time.time())
        storeTime = self.registryValue("rateLimitTime", channel)
        victimCount = 0
        senderCount = 0
        totalCount = 0

        for bstr in bombHistoryOrig:
            b = bstr.split("#")
            if len(b) < 3 or int(b[0]) + storeTime < now:
                continue
            totalCount += 1

            if b[1] == senderMask:
                senderCount += 1

            if b[2] == victim:
                victimCount += 1
            bombHistory.append(bstr)
        self.setRegistryValue("bombHistory", bombHistory, channel)

        if (
            totalCount
            > storeTime * self.registryValue("rateLimitTotal", channel) / 3600
        ):
            if replyError:
                irc.reply(
                    "Desculpa, mas enfiei tantas bombas-relógio em tantas calças"
                    " que fiquei temporariamente sem explosivos. Terás que esperar."
                )
            return False

        if (
            senderCount
            > storeTime * self.registryValue("rateLimitSender", channel) / 3600
        ):

            if replyError:
                irc.reply(
                    "Já fizeste uma bomba-relógio a muita gente recentemente,"
                    " deixa outra pessoa tentar."
                )
            return False

        if (
            victimCount
            > storeTime * self.registryValue("rateLimitVictim", channel) / 3600
        ):
            if replyError:
                irc.reply(
                    "Esse utilizador tem sido alvo de muitas bombas-relógio nos"
                    " últimos tempos, tenta escolher outra pessoa."
                )
            return False
        return True

    def _logBomb(self, irc, channel, sender, victim):
        bombHistory = self.registryValue("bombHistory", channel)
        senderHostmask = irc.state.nickToHostmask(sender)
        (nick, user, host) = ircutils.splitHostmask(senderHostmask)
        senderMask = ("{}@{}".format(user, host)).lower()
        victim = victim.lower()
        bombHistory.append("{}#{}#{}".format(int(time.time()), senderMask, victim))
        self.setRegistryValue("bombHistory", bombHistory, channel)

    def bombsenabled(self, irc, msg, args, channel, value):
        """[<canal>] <True|False>
        Define o valor do valor de configuração allowBombs para o canal. Restrito a utilizadores com a capacidade timebombadmin.
        """
        statusDescription = "are currently"
        if value:
            # tmp = ircdb.channels.getChannel(channel).defaultAllow - problems with multithreading?
            # ircdb.channels.getChannel(channel).defaultAllow = False
            hasCap = ircdb.checkCapability(msg.prefix, "timebombadmin")
            if (
                channel == "#powder" or channel == "#powder-dev"
            ) and not ircdb.checkCapability(msg.prefix, "admin"):
                irc.error("Para tal, é necessária a capacidade de admin.")
                return
            # ircdb.channels.getChannel(channel).defaultAllow = tmp

            if hasCap:
                oldValue = self.registryValue("allowBombs", channel)
                try:
                    conf.supybot.plugins.TimeBomb.allowBombs.get(channel).set(value)
                except registry.InvalidRegistryValue:
                    irc.error("O valor deve ser True ou False.")
                    return
                if self.registryValue("allowBombs", channel) == oldValue:
                    statusDescription = "já foram"
                else:
                    statusDescription = "foram agora"
            else:
                irc.error("Para tal, é necessária a capacidade timebombadmin.")
                return

        if self.registryValue("allowBombs", channel):
            irc.reply("Bombas-relógio {} activadas em {}.".format(statusDescription, channel))
        else:
            irc.reply("Bombas-relógio {} desactivadas em {}.".format(statusDescription, channel))

    bombsenabled = wrap(bombsenabled, ["channel", optional("somethingWithoutSpaces")])

    def duck(self, irc, msg, args, channel):
        """[<canal>]
        BAIXA-TE! (Vais querer fazer isto se alguém te atirar uma bomba).
        """
        channel = ircutils.toLower(channel)
        try:
            if (
                not self.bombs[channel].active
                or not self.bombs[channel].rethrown
                or not ircutils.nickEqual(self.bombs[channel].victim, msg.nick)
            ):
                return
        except KeyError:
            return
        self.bombs[channel].duck(irc, msg.nick)
        irc.noReply()

    duck = wrap(duck, ["channel"])

    def randombomb(self, irc, msg, args, channel, nicks):
        """[<canal>]
        Bombardeia uma pessoa ao acaso no canal.
        """
        channel = ircutils.toLower(channel)
        if not self.registryValue("allowBombs", channel):
            irc.reply(
                "As bombas-relógio não são permitidas neste canal. Define"
                " plugins.TimeBomb.allowBombs como True se as quiseres."
            )
            return
        try:
            if self.bombs[channel].active:
                irc.reply(
                    "Já existe uma bomba ativa, nas calças de {}!".format(
                        self.bombs[channel].victim
                    )
                )
                return
        except KeyError:
            pass

        if not self._canBomb(irc, channel, msg.nick, "", True):
            return

        if self.registryValue("bombActiveUsers", channel):
            if len(nicks) == 0:
                nicks = list(irc.state.channels[channel].users)
                items = iter(list(self.talktimes.items()))
                nicks = []
                count = 0

                while count < len(self.talktimes):
                    try:
                        item = next(items)
                        if (
                            time.time() - item[1]
                            < self.registryValue("idleTime", channel) * 60
                            and item[0] in irc.state.channels[channel].users
                            and self._canBomb(irc, channel, msg.nick, item[0], False)
                        ):
                            nicks.append(item[0])
                    except StopIteration:
                        irc.reply(
                            "Aconteceu uma coisa engraçada... Recebi uma exceção"
                            " StopIteration."
                        )
                    count += 1
                if len(nicks) == 1 and nicks[0] == msg.nick:
                    nicks = []
            if len(nicks) == 0:
                irc.reply(
                    "Bem, ninguém falou na última hora, por isso acho que vou"
                    " escolher alguém ao acaso."
                )
                nicks = list(irc.state.channels[channel].users)
            elif len(nicks) == 2:
                irc.reply(
                    "Bem, ultimamente têm sido só vocês os dois a falar, por"
                    " isso vou bombardear alguém ao acaso."
                )
                nicks = list(irc.state.channels[channel].users)
        elif len(nicks) == 0:
            nicks = list(irc.state.channels[channel].users)

        if irc.nick in nicks and not self.registryValue("allowSelfBombs", channel):
            nicks.remove(irc.nick)
        eligibleNicks = []

        for victim in nicks:
            if not (
                victim == self.lastBomb
                or victim.lower() in self.registryValue("randomExclusions", channel)
                or victim.lower() in self.registryValue("exclusions", channel)
            ) and self._canBomb(irc, channel, msg.nick, victim, False):
                eligibleNicks.append(victim)

        if len(eligibleNicks) == 0:
            irc.reply(
                "Não consegui encontrar ninguém adequado para bombardear."
                " Talvez toda a gente aqui esteja excluída de ser bombardeada ou"
                " tenha sido bombardeada demasiado recentemente."
            )
            return
        #####
        # irc.reply('These people are eligible: {}'.format(utils.str.commaAndify(eligibleNicks)))
        victim = self.rng.choice(eligibleNicks)
        self.lastBomb = victim
        detonateTime = self.rng.randint(
            self.registryValue("minRandombombTime", channel),
            self.registryValue("maxRandombombTime", channel),
        )
        wireCount = self.rng.randint(
            self.registryValue("minWires", channel),
            self.registryValue("maxWires", channel),
        )

        if wireCount < 12:
            colors = self.registryValue("shortcolors")
        else:
            colors = self.registryValue("colors")

        wires = self.rng.sample(colors, wireCount)
        goodWire = self.rng.choice(wires)
        self.log.info("Bomba-relógio: O fio seguro é {}".format(goodWire))
        self._logBomb(irc, channel, msg.nick, victim)
        self.bombs[channel] = self.Bomb(
            irc,
            victim,
            wires,
            detonateTime,
            goodWire,
            channel,
            msg.nick,
            self.registryValue("showArt", channel),
            self.registryValue("showCorrectWire", channel),
            self.registryValue("debug"),
        )

        try:
            irc.noReply()
        except AttributeError:
            pass

    randombomb = wrap(randombomb, ["channel", any("NickInChannel")])

    def timebomb(self, irc, msg, args, channel, victim):
        """[<canal>] <nick>
        Coloca uma bomba nas calças de <nick>.
        """
        channel = ircutils.toLower(channel)
        if not self.registryValue("allowBombs", channel):
            irc.reply(
                "As bombas-relógio não são permitidas neste canal. Define"
                " plugins.TimeBomb.allowBombs como true se as quiseres."
            )
            return
        try:
            if self.bombs[channel].active:
                irc.reply(
                    "Já existe uma bomba ativa, nas calças de {}!".format(
                        self.bombs[channel].victim
                    )
                )
                return
        except KeyError:
            pass

        if victim.lower() == irc.nick.lower() and not self.registryValue(
            "allowSelfBombs", channel
        ):
            irc.reply(
                "Esperas mesmo que eu me bombardeie? Enfiar explosivos nas minhas"
                " calças não é propriamente a minha ideia de diversão."
            )
            return
        victim = victim.lower()
        found = False

        for nick in list(irc.state.channels[channel].users):
            if victim == nick.lower():
                victim = nick
                found = True
        if not found:
            irc.reply("Erro: nick não encontrado.")
            return
        for nick in self.registryValue("exclusions", channel):
            if nick.lower() == victim.lower():
                irc.reply("Erro: este nick não pode ser bombardeado.")
                return

        # not (victim == msg.nick and victim == 'mniip') and
        if not ircdb.checkCapability(msg.prefix, "admin") and not self._canBomb(
            irc, channel, msg.nick, victim, True
        ):
            return

        detonateTime = self.rng.randint(
            self.registryValue("minTime", channel),
            self.registryValue("maxTime", channel),
        )
        wireCount = self.rng.randint(
            self.registryValue("minWires", channel),
            self.registryValue("maxWires", channel),
        )
        # if victim.lower() == 'halite' or (victim == msg.nick and victim == 'mniip'):
        #    wireCount = self.rng.randint(11,20)
        if wireCount < 12:
            colors = self.registryValue("shortcolors")
        else:
            colors = self.registryValue("colors")

        wires = self.rng.sample(colors, wireCount)
        goodWire = self.rng.choice(wires)
        self.log.info("Bomba-relógio: O fio seguro é {}.".format(goodWire))

        if self.registryValue("debug"):
            irc.reply("I'm about to create a bomb in {}.".format(channel))

        # if not (victim == msg.nick and victim == 'mniip'):
        self._logBomb(irc, channel, msg.nick, victim)
        self.bombs[channel] = self.Bomb(
            irc,
            victim,
            wires,
            detonateTime,
            goodWire,
            channel,
            msg.nick,
            self.registryValue("showArt", channel),
            self.registryValue("showCorrectWire", channel),
            self.registryValue("debug"),
        )
        if self.registryValue("debug"):
            irc.reply(
                "This message means that I got past the bomb creation line in the"
                " timebomb command."
            )

    timebomb = wrap(
        timebomb,
        ["channel", ("checkChannelCapability", "timebombs"), "somethingWithoutSpaces"],
    )

    def cutwire(self, irc, msg, args, channel, cutWire):
        """[<canal>] <côr>
        Cortará o fio fornecido se for bombardeado.
        """
        channel = ircutils.toLower(channel)
        try:
            if not self.bombs[channel].active or self.bombs[channel].rethrown:
                return

            if not ircutils.nickEqual(
                self.bombs[channel].victim, msg.nick
            ) and not ircdb.checkCapability(msg.prefix, "admin"):
                irc.reply("Não pode cortar o fio da bomba de outra pessoa!")
                return
            self.bombs[channel].cutwire(irc, cutWire)
        except KeyError:
            pass
        irc.noReply()

    cutwire = wrap(cutwire, ["channel", "something"])

    def detonate(self, irc, msg, args, channel):
        """[<canal>]
        Detona a bomba ativa.
        """
        channel = ircutils.toLower(channel)
        try:
            if self.bombs[channel].active:
                schedule.rescheduleEvent("{}_bomb".format(channel), time.time())
        except KeyError:
            if self.registryValue("debug"):
                irc.reply('Tentei detonar uma bomba em "{}"'.format(channel))
                irc.reply(
                    "Lista de bombas: {}".format(", ".join(list(self.bombs.keys())))
                )
        irc.noReply()

    detonate = wrap(detonate, ["channel", ("checkChannelCapability", "op")])

    def defuse(self, irc, msg, args, channel):
        """[<canal>]
        Desativa a bomba ativa (apenas operadores de canal).
        """
        channel = ircutils.toLower(channel)
        try:
            if self.bombs[channel].active:
                if ircutils.nickEqual(self.bombs[channel].victim, msg.nick) and not (
                    ircutils.nickEqual(
                        self.bombs[channel].victim, self.bombs[channel].sender
                    )
                    or ircdb.checkCapability(msg.prefix, "admin")
                ):
                    irc.reply(
                        "Não podes desarmar uma bomba que está nas tuas próprias"
                        " calças, só tens de cortar um fio e esperar pelo melhor."
                    )
                    return
                self.bombs[channel].defuse()
                irc.reply("Bomba desarmada.")
            else:
                irc.error("There is no active bomb.")
        except KeyError:
            pass
            irc.error("Não há nenhuma bomba ativa")

    defuse = wrap(defuse, ["channel", ("checkChannelCapability", "op")])


Class = TimeBomb
