###
# Copyright (c) 2012, Matthias Meusburger
# Copyright (c) 2020, oddluck <oddluck@riseup.net>
# Copyright (c) 2025, PeGaSuS <droider.pc@gmail.com>
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

import supybot.conf as conf
import supybot.registry as registry


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn

    conf.registerPlugin("DuckHuntPT", True)


DuckHuntPT = conf.registerPlugin("DuckHuntPT")
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Quote, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))
conf.registerChannelValue(
    DuckHuntPT,
    "autoRestart",
    registry.Boolean(
        False, """Uma nova caçada começa automaticamente quando a anterior termina?"""
    ),
)

conf.registerChannelValue(
    DuckHuntPT, "ducks", registry.Integer(5, """Número de patos durante uma caçada?""")
)

conf.registerChannelValue(
    DuckHuntPT,
    "minthrottle",
    registry.Integer(
        30,
        """O período mínimo de tempo antes de um novo pato poder ser lançado (em segundos)""",
    ),
)

conf.registerChannelValue(
    DuckHuntPT,
    "maxthrottle",
    registry.Integer(
        300,
        """O período máximo de tempo antes de um novo pato poder ser lançado (em segundos)""",
    ),
)

conf.registerChannelValue(
    DuckHuntPT,
    "reloadTime",
    registry.Integer(
        5, """O tempo que demora a recarregar a espingarda depois de ter disparado (em segundos)"""
    ),
)

conf.registerChannelValue(
    DuckHuntPT,
    "missProbability",
    registry.Probability(0.2, """A probabilidade de não acertar no pato"""),
)

conf.registerChannelValue(
    DuckHuntPT,
    "kickMode",
    registry.Boolean(
        True,
        """Se alguém disparar quando não há pato, deve ser kickado do canal? (para isso é necessário que o bot seja op no canal)""",
    ),
)

conf.registerChannelValue(
    DuckHuntPT,
    "autoFriday",
    registry.Boolean(
        True, """É necessário lançar automaticamente mais patos na sexta-feira?"""
    ),
)


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
