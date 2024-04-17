###
# Copyright (c) 2010, quantumlemur
# Copyright (c) 2020, oddluck <oddluck@riseup.net>
# Copyright (c) 2024, PeGaSuS <pegasus@computer4u.com>
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

    conf.registerPlugin("TimeBomb", True)


TimeBomb = conf.registerPlugin("TimeBomb")
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(TimeBomb, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))
conf.registerGlobalValue(
    TimeBomb,
    "colors",
    registry.SpaceSeparatedListOfStrings(
        [
            "Branco",
            "Preto",
            "Vermelho",
            "Azul",
            "Amarelo",
            "Verde",
            "Laranja",
            "Rosa",
            "Roxo",
            "Castanho",
            "Cinza",
            "Bege",
            "Dourado",
            "Prateado",
            "Turquesa",
            "Ciano",
            "Indigo",
            "Magenta",
            "Coral",
            "Borgonha",
            "Creme",
            "Melancia",
            "Caramelo",
            "Safira",
            "Esmeralda",
            "Acafrao",
            "Rubi",
            "Lilas",
            "Pessego",
            "Orquidea",
            "Jade",
            "Taupe",
            "Coralina",
            "Lavanda",
            "Menta",
            "Terracota",
            "Oliva",
            "Celeste",
            "Marinho",
            "Khaki",
            "Ametista",
            "Topazio",
            "Turmalina",
            "Coralino",
            "Avela",
            "Salva",
            "Neon",
            "Fuchsia",
        ],
        """O conjunto de cores possíveis dos fios da bomba-relógio""",
    ),
)


conf.registerGlobalValue(
    TimeBomb,
    "shortcolors",
    registry.SpaceSeparatedListOfStrings(
        [
            "vermelho",
            "laranja",
            "amarelo",
            "verde",
            "azul",
            "roxo",
            "rosa",
            "preto",
            "castanho",
            "cinza",
            "branco",
        ],
        """O conjunto de cores possíveis dos fios da bomba-relógio quando há poucos
                fios""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "randomExclusions",
    registry.SpaceSeparatedListOfStrings(
        [],
        """Uma lista de nicks que devem ser excluídos de serem
            bombardeados aleatoriamente""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "exclusions",
    registry.SpaceSeparatedListOfStrings(
        [],
        """Uma lista de nicks que devem ser completamente excluídos de 
            serem bombardeados""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "allowBombs",
    registry.Boolean(
        False,
        """Determina se bombas-relógio são permitidas 
            no canal.""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "bombHistory",
    registry.SpaceSeparatedListOfStrings(
        [], """Data e hora, remetentes e vítimas de bombas anteriores no canal"""
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "rateLimitTime",
    registry.Integer(
        1800,
        """Tempo em segundos durante o qual as bombas anteriores são lembradas e contabilizadas para o limite de taxa""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "rateLimitSender",
    registry.Float(
        5.0, """Média de bombas/hora permitidas no passado rateLimitTime de cada host"""
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "rateLimitVictim",
    registry.Float(
        3.0,
        """Média de bombaas/hora permitido no passado rateLimitTime visando um nick específico""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "rateLimitTotal",
    registry.Float(9.0, """Média total de bombas/hora permitidas no passado rateLimitTime"""),
)

conf.registerChannelValue(
    TimeBomb,
    "minWires",
    registry.PositiveInteger(
        2,
        """Determina o número mínimo de fios que uma 
            bomba-relógio terá.""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "maxWires",
    registry.PositiveInteger(
        4,
        """Determina o número máximo de fios que uma 
            bomba-relógio terá.""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "minTime",
    registry.PositiveInteger(
        45,
        """Determina o tempo mínimo de um cronómetro de 
            uma bomba-relógio, em segundos.""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "maxTime",
    registry.PositiveInteger(
        70,
        """Determina o tempo máximo de um cronómetro de
            uma bomba-relógio, em segundos.""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "minRandombombTime",
    registry.PositiveInteger(
        60,
        """Determina o tempo mínimo de um cronômetro de uma 
            bomba aleatória, que em geral deve ser maior que o tempo 
            mínimo de bomba direcionado, para permitir que alguém que 
            não esteja prestando atenção responda.""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "maxRandombombTime",
    registry.PositiveInteger(
        120,
        """Determina o tempo máximo de um cronómetro de uma 
            bomba aleatória, que em geral deve ser maior que o tempo
            máximo da bomba direcionada, para permitir que alguém que
            não esteja prestando atenção responda.""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "showArt",
    registry.Boolean(
        False,
        """Determina se uma bomba artística ASCII deve ser
            mostrada na detonação ou uma simples mensagem.""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "bombActiveUsers",
    registry.Boolean(
        True,
        """Determina se apenas utlizadores ativos devem 
            ser bombardeados aleatoriamente""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "joinIsActivity",
    registry.Boolean(
        False,
        """Determina se as entradas no canal devem contar
            como atividade para bombas aleatórias""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "allowSelfBombs",
    registry.Boolean(False, """Permitir que o bot se bombardeie a si mesmo?"""),
)

conf.registerChannelValue(
    TimeBomb,
    "idleTime",
    registry.PositiveInteger(
        30,
        """O número de minutos antes que alguém seja contado como 
            inativo para bombas aleatórias, se a verificação de 
            inatividade estiver habilitada.""",
    ),
)

conf.registerChannelValue(
    TimeBomb,
    "showCorrectWire",
    registry.Boolean(
        False,
        """Determina se o fio correto será mostrado 
            quando uma bomba detonar.""",
    ),
)

conf.registerGlobalValue(
    TimeBomb,
    "debug",
    registry.Boolean(
        False,
        """Determina se as informações de depuração serão 
            mostradas.""",
    ),
)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
