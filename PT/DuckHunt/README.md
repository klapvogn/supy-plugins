O clássico jogo IRC Duck Hunt.

Bifurcado de https://github.com/veggiematts/supybot-duckhunt

Requer Python3, Limnoria.

Python 3 e correções de pontuação. Plugin a funcionar.

\\\_o< ~ Jogo DuckHunt para supybot ~ >o_/
=======================================

Como jogar
-----------
* Utilize o comando "starthunt" para iniciar um jogo. 
* O bot lançará patos aleatoriamente. Sempre que um pato é lançado, a primeira pessoa a utilizar o comando "bang" ganha um ponto. 
* Usar o comando "bang" quando não há nenhum pato lançado custa um ponto. 
* A utilização do comando "bang" duas ou mais vezes durante o recarregamento custa um ponto. 
* Se um jogador disparar sobre todos os patos durante uma caçada, é perfeito! Este jogador ganha pontos de bónus extra. 
* As melhores pontuações de um canal são registadas e podem ser apresentadas com o comando "listscores". 
* Os disparos mais rápidos e mais longos são também registados e podem ser apresentados com o comando "listtimes". 
* O comando "launched" informa se existe um pato para disparar no momento.

Como instalar
--------------
Basta colocar o plugin DuckHunt no diretório de plugins da instalação do seu supybot e carregar o módulo.

Como configurar
----------------
Estão disponíveis várias variáveis ​​de configuração por canal (consulte o comando "channel" para saber mais sobre como configurar variáveis ​​de configuração por canal):
* autoRestart: Uma nova caçada começa automaticamente quando a anterior termina? 
* patos: Número de patos durante uma caçada? 
* minthrottle: O tempo mínimo antes de um novo pato poder ser lançado (em segundos)
* maxthrottle: O tempo máximo antes de um novo pato poder ser lançado (em segundos)
* reloadTime: O tempo que demora a recarregar a sua espingarda depois de disparar (em segundos)
*kickMode: Se alguém disparar quando não há pato, deve ser expulso do canal? (isto requer que o bot esteja op no canal)
* autoFriday: Precisamos de lançar mais patos automaticamente na sexta-feira? 
* missProbability: A probabilidade de perder o pato

Atualizar
------
Obtenha a versão mais recente em: https://github.com/TehPeGaSuS/supy-plugins
