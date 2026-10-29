# Auditoria independente da eleição presidencial de 2026

Português · [English](README.en.md)

Conferência, só com dados públicos do TSE, do resultado da eleição para Presidente de 2026 (1º turno em 04/10,
2º turno em 25/10, Lula × Flávio Bolsonaro). Tudo pode ser refeito: os dados estão no repositório (ou se baixam
com um comando) e cada número sai de um script que pode ser lido e rodado. Se você achar um erro, abra uma issue
com o script e o resultado.

O relatório formal, com escopo, metodologia, achados e parecer, está em
[`docs/RELATORIO_DE_AUDITORIA.md`](docs/RELATORIO_DE_AUDITORIA.md).

## Sumário

1. [Introdução](#1-introdução)
2. [As hipóteses, uma por uma](#2-as-hipóteses-uma-por-uma)
3. [Conclusão](#3-conclusão)
4. [Extra: como o voto mudou do 1º para o 2º turno](#4-extra-como-o-voto-mudou-do-1º-para-o-2º-turno)
- [Apêndice A. Glossário](#apêndice-a-glossário)
- [Apêndice B. De onde veio cada dado](#apêndice-b-de-onde-veio-cada-dado)
- [Apêndice C. Problemas nos dados](#apêndice-c-problemas-nos-dados)
- [Apêndice D. Como rodar tudo](#apêndice-d-como-rodar-tudo)
- [Apêndice E. Mapa do repositório](#apêndice-e-mapa-do-repositório)

---

## 1. Introdução

### Por que esta auditoria

Lula venceu o 2º turno por 4.430.191 votos (51,79% a 48,21%). Logo depois circularam afirmações de fraude que
usavam os próprios dados do TSE: que as urnas fechadas mais tarde teriam virado a eleição, que milhões de eleitores
liberados sem digital decidiram o resultado, que os dados ficaram escondidos por dias. Afirmações feitas com dados
públicos podem ser conferidas com os mesmos dados, e é isso que este trabalho faz.

O método é simples de explicar. Onde dá para contar, conto: somo os boletins de urna, reconto os votos gravados por
cada urna, cruzo arquivos entre si. Onde a pergunta é sobre padrões, comparo cada grupo suspeito com um controle: a
mesma seção no 1º turno, a eleição de 2022 e seções vizinhas da mesma cidade. E para cada suspeita calculo quanto da
margem ela poderia explicar no pior cenário que os dados permitem.

### Resultado oficial

| 1º turno, 04/10/2026 | Votos | % dos válidos |
|---|---|---|
| Flávio Bolsonaro (22) | 56.104.503 | 47,03% |
| Lula (13) | 53.879.538 | 45,16% |
| Augusto Cury (70) | 3.448.569 | 2,89% |
| Renan Santos (14) | 2.675.887 | 2,24% |
| Ronaldo Caiado (55) | 2.605.148 | 2,18% |
| Demais 7 candidatos | 587.143 | 0,49% |
| Válidos | 119.300.788 | |
| Brancos / nulos | 2.300.798 / 3.674.249 (inclui 5.246 nulos técnicos) | |
| Comparecimento | 125.275.835 (78,92% dos aptos) | |

| 2º turno, 25/10/2026 | Votos | % dos válidos |
|---|---|---|
| Lula (13) | 64.256.232 | 51,79% |
| Flávio Bolsonaro (22) | 59.826.041 | 48,21% |
| Margem | 4.430.191 | |
| Brancos / nulos | 1.430.496 / 2.723.305 | |
| Comparecimento | 128.236.074 (80,78% dos aptos) | |

### As hipóteses testadas

Cada hipótese abaixo é uma forma de o resultado estar errado ou ter sido alterado. A seção 2 testa uma por uma.

| | Hipótese | Veredito |
|---|---|---|
| H1 | O resultado oficial não é a soma dos boletins de urna. | Refutada |
| H2 | Os boletins não correspondem ao que as urnas gravaram. | Refutada |
| H3 | Foram usadas urnas diferentes das previstas. | Refutada em 99,4% das seções; 17 seções sem explicação nos dados |
| H4 | Houve "duas eleições": Flávio venceu até as 17h e a virada veio depois. | Refutada |
| H5 | As seções que ficaram abertas até as 19h receberam votos a mais. | Refutada; o fechamento às 19h aconteceu |
| H6 | Os 8,6 milhões de eleitores liberados sem digital decidiram a eleição. | Sem sinal disso |
| H7 | Seções com 100% para Lula indicam fraude. | Refutada |
| H8 | A Lei de Benford mostra números inventados. | Sem sinal (teste fraco) |
| H9 | O 2º turno destoa do 1º, seção por seção. | Refutada |
| H10 | Os dados ficaram "trancados" por 72 horas para serem alterados. | Procede em parte quanto ao acesso; refutada quanto à alteração |

### O que mudaria a conclusão

Eu concluiria que houve alteração se aparecesse qualquer um destes sinais: uma UF cuja soma de boletins não batesse
com o resultado oficial; um registro digital do voto diferente do boletim da mesma urna; um log com voto fora do
horário ou com liberações diferentes do boletim; um grupo de seções que se desviasse a favor de um candidato, em
relação ao próprio 1º turno, em todas as formas do modelo, inclusive comparando seções da mesma cidade; boletins de
papel diferentes dos arquivos; assinaturas digitais inválidas. Nenhum dos quatro primeiros apareceu. Os dois
últimos não foram testados.

---

## 2. As hipóteses, uma por uma

### H1. O resultado oficial é a soma dos boletins?

Antes de tudo, conferi os arquivos: o SHA-512 de cada arquivo baixado bate com o `.sha512` publicado pelo TSE em 112
de 112. Isso prova que o download está íntegro, mas o hash vem do mesmo servidor dos dados.

Depois, `analise/totalizacao.py` soma seções, aptos, comparecimento, brancos, nulos e votos de cada candidato em
todos os boletins, por UF e no Brasil, e compara com o PDF oficial do TSE. Votos, brancos, nulos e comparecimento
batem exatamente em 29 de 29 regiões (27 UFs, exterior e Brasil), nos dois turnos. Contando também seções e aptos,
batem 27 de 29: a diferença são 1 ou 2 seções do exterior sem nenhum votante (apêndice C, problema 10). O resultado
do 2º turno foi assinado às 23h28 de 25/10.

Cada boletim também foi conferido sozinho (`analise/consistencia.py`, 499.205 boletins):

| Regra | Violações |
|---|---|
| aptos = comparecimento + abstenções | 0 |
| comparecimento ≤ aptos | 0 |
| soma de todos os votos = comparecimento | 0 |
| liberados ≤ comparecimento | 0 |
| abertura < encerramento ≤ impressão do BU | 0 (fora as 27 seções de cédula, sem horário) |
| urna abriu no dia da eleição | 0 |
| comparecimento de Presidente menor que o de Governador | 0 (quem vota em trânsito só vota para Presidente) |
| BU recebido pelo TSE antes de impresso pela urna | 8 seções, no máximo 52 segundos (relógio da urna adiantado) |
| urna preparada no dia da eleição | 5 (urnas substituídas antes da abertura, que abriram atrasadas) |

Veredito: refutada. Detalhes em [`TOTALIZACAO.md`](analise/TOTALIZACAO.md) e
[`CONSISTENCIA.md`](analise/CONSISTENCIA.md).

### H2. Os boletins correspondem ao que as urnas gravaram?

Cada urna grava, além do boletim, o registro digital do voto (RDV): cada voto digitado, embaralhado. Escrevi um
leitor desse formato (ASN.1/DER), contei os votos de Presidente um a um em todas as urnas do país e comparei com a
planilha do TSE (`analise/recontagem_rdv.py` e `recontagem_rdv_nacional.py`). Cada RDV foi lido direto do pacote
oficial, baixando só aquele arquivo.

| Recontagem pelo RDV | Resultado |
|---|---|
| Seções com urna eletrônica recontadas (Brasil e exterior) | 499.178 |
| RDV idêntico à planilha (Lula, Flávio, brancos e nulos) | 499.178 de 499.178 |
| Lula / Flávio somando os RDVs | 64.255.787 / 59.825.688 |
| Diferença para o oficial | 445 / 353, exatamente os votos das 27 seções do exterior apuradas em cédula, cujo arquivo o leitor não interpreta |

Em AC, RR e AP (5.703 urnas) li o pacote inteiro: o boletim digital (`bu.dat`), o código de carga, a imagem do
boletim (`imgbu.dat`, o texto que a urna manda imprimir, que vem no mesmo pacote) e o log de cada urna. Tudo bate
com a planilha em 5.703 de 5.703, e nenhum voto foi registrado depois do fechamento.

O RDV é gravado pela mesma urna que gera o boletim, então isso mostra que nada mudou entre a urna e a totalização.
Não mostra que o software da urna é honesto (seção 3).

Veredito: refutada. Detalhes em [`RECONTAGEM_RDV_NACIONAL.md`](analise/RECONTAGEM_RDV_NACIONAL.md),
[`RECONTAGEM_RDV.md`](analise/RECONTAGEM_RDV.md), [`LOGS.md`](analise/LOGS.md) e
[`IMAGEM_BU.md`](analise/IMAGEM_BU.md).

### H3. As urnas usadas eram as previstas?

Na véspera, o TSE gera uma lista de qual urna e qual software ("carga") vai em cada seção, mais as urnas reserva
(contingência). `analise/correspondencia.py` compara cada boletim com essa lista, gerada em 24/10 às 12:31:

| Categoria | Seções | Votos | Saldo de Lula |
|---|---|---|---|
| 1. urna e carga exatamente as previstas | 496.138 | 127.447.547 | +4.401.710 |
| 2. urna prevista, carga diferente da lista | 9 | 2.467 | −55 |
| 3. urna de contingência da lista, com a carga da lista | 2.641 | 686.899 | +21.744 |
| 4. urna de contingência da lista, recarregada | 258 | 63.989 | +1.902 |
| 5. urna fora das listas, carregada depois que a lista foi gerada | 45 | 12.032 | +1.968 |
| 6. urna fora das listas, mesmo cartão de carga da urna prevista | 59 | 15.027 | +2.230 |
| 7. urna fora das listas, sem explicação nos dados | 16 | 4.275 | −19 |
| 8. seção fora da lista: exterior, apurada em cédula | 27 | 831 | +92 |
| 9. seção fora da lista, urna de contingência da lista | 11 | 2.719 | +558 |
| 10. seção fora da lista, urna fora das listas | 1 | 288 | +61 |

A maior parte das trocas usou urna de contingência que estava na lista. As categorias 2, 4, 5, 6 e 9 têm
explicação provável nos próprios dados, mas precisam de confirmação nas atas. As categorias 7 e 10 somam 17 seções e
4.563 votos sem nenhuma explicação, com saldo de +42 para Lula. A divisão entre as categorias 5 e 7 depende da hora
de carga comparada com a hora em que a lista foi gerada, então um erro de relógio pode mover algumas seções de uma
para a outra.

Veredito: refutada em 99,4% das seções. As 17 restantes não mudam nada (4.563 votos) e se esclarecem com as atas
(lista em [`secoes_para_documentar.csv`](analise/secoes_para_documentar.csv)).

### H4. Houve "duas eleições", antes e depois das 17h?

A afirmação: nas urnas fechadas até 17h Flávio venceu com 52,39%, e a virada só veio depois.

Os números saem exatos quando se usa o horário como a urna grava: até 17:00:59, 150.771 seções e Flávio com 52,39%;
de 17:01 a 17:15, 339.593 seções e 53,46% para Lula (`analise/suspeitas.py`). O problema é que a urna grava a hora
local. Urnas do Acre, do Amazonas e do Centro-Oeste que fecharam às 17h de Brasília aparecem como 15h ou 16h e caem
no grupo "antes das 17h". A prova principal está em [`FUSO.md`](analise/FUSO.md): as urnas abrem às 06h no Acre, às
07h no Norte e no Centro-Oeste e às 08h no resto, ou seja, todas às 8h de Brasília.

Três coisas mostram que o grupo "até 17h" é geografia:

1. O mesmo corte dá "duas eleições" também em 2022 (Bolsonaro +1,0 milhão "até 17h", e Lula vira depois):

![O mesmo corte em 2026 e 2022](docs/graficos/01_duas_eleicoes_2026_vs_2022.png)

2. Os estados a oeste são 21% das seções do grupo e 83% da vantagem de Flávio nele. Comparando só seções do mesmo
   estado, a diferença cai de −5,9 para −1,4 p.p.; do mesmo município, para −0,2 p.p. E as mesmas seções já
   votavam assim no 1º turno (−5,95 p.p.):

![Decomposição do grupo até 17h](docs/graficos/02_grupo_ate_17h_decomposicao.png)

3. Fechar entre 17:01 e 17:15 é o normal: quem está na fila às 17h vota, e a urna fecha depois do último eleitor.
   Essa faixa tem 68% das seções do país.

Veredito: refutada.

### H5. As seções abertas até as 19h receberam votos a mais?

Aqui há um fato real. No 2º turno, 6.352 seções (em horário de Brasília) fecharam às 19h ou pouco depois, 1.993
delas no minuto 19:00 exato. Um pico num minuto só indica um horário-limite marcado; fila daria fechamentos
espalhados. Elas ficam em 1.131 locais de votação, sobretudo em capitais (Rio 1.978 seções, São Paulo 1.481,
Salvador 730). Isso não aparece no 1º turno nem em 2022.

![Fechamentos minuto a minuto](docs/graficos/03_horario_fechamento_por_minuto.png)

Mas o horário extra quase não teve votos. Li o log de cada uma das 6.352 urnas direto do servidor do TSE: só 4.492
de 1.861.259 votos (0,24%) foram computados depois das 17h, e 3.885 urnas não tiveram nenhum voto depois das 17h15.
O total de votos no log bate com o boletim em 100% das urnas.

![Votos depois das 17h](docs/graficos/04_votos_depois_das_17h_nas_secoes_tardias.png)

Essas seções também votaram como as outras. Comparadas com seções do mesmo local de votação que fecharam às 17h, a
diferença é de −0,06 p.p. na % de Lula e +0,03 p.p. no comparecimento (nos 313 locais em que todas as seções
fecharam às 19h não há vizinha para comparar). Comparadas com o próprio 1º turno, Lula subiu 3,25 p.p. nelas e 3,20
p.p. nas demais seções das mesmas cidades, e nenhuma das seis formas do modelo de H9 dá desvio a favor de Lula
distinguível de zero. O limite superior de 95% na forma mais desfavorável é de 18.771 votos (0,4% da margem).

Mesmo anulando todas essas seções, Lula venceria por 4.244.467 votos. No Rio, que tem mais seções tardias, Flávio
venceu nelas (45,8% para Lula). A afirmação de que "mais de 2 milhões de eleitores" votaram nessas seções conta os
aptos: pelo relógio local eram 2,30 milhões de aptos e 1,86 milhão de votantes.

Veredito: refutada. Por que esses locais ficaram abertos até as 19h os dados não dizem; isso está nos atos dos
TREs. Detalhes em [`LOGS_TARDIAS.md`](analise/LOGS_TARDIAS.md) e [`RESULTADOS.md`](analise/RESULTADOS.md).

### H6. Os eleitores liberados sem digital decidiram a eleição?

Quando a digital do eleitor falha 4 vezes, a urna pede um dado pessoal e depois a digital do mesário. O número
confere: 8.632.488 liberações assim no 2º turno (6,73% do comparecimento). Compará-lo com a margem só faria sentido
se esses eleitores tivessem votado em bloco num candidato. Testei isso de quatro formas.

1. Pior caso aritmético. Se em cada seção todo liberado tivesse votado em Lula e fosse retirado, Flávio venceria
   por 4,19 milhões. É o cenário extremo, sem nenhum teste por trás.

2. Inclinação: quanto a % de Lula muda quando a taxa de liberação muda. Daí sai uma estimativa de como votaram os
   liberados:

| Comparando… | % de Lula entre os liberados (estimativa) | Margem sem os liberados (limite de 95%) |
|---|---|---|
| o país todo | 79% | −2,80 mi |
| dentro do estado | 68% | −0,22 mi |
| dentro do município | 54% | +2,55 mi |

   Liberação e voto em Lula são, os dois, maiores no Nordeste e no interior. Comparar o país todo atribui à
   liberação um efeito que é da geografia (a falácia ecológica). Entre seções da mesma cidade, os liberados votam
   quase como os demais. O exterior fica fora desta conta, porque lá não há biometria.

3. Contra o 1º turno. Dado como a própria seção votou no 1º turno, mais liberação vem com menos Lula do que o
   esperado (−0,32 p.p. a cada 10 p.p. de liberação, EP 0,03), e o aumento da liberação entre os turnos não tem
   efeito (−0,02 p.p., margem de erro ±0,03). Se a liberação tivesse sido usada para pôr votos em Lula, o sinal
   seria o contrário.

4. Estabilidade. A taxa de cada seção se repete entre os turnos (correlação 0,82), vai de 4,1% (RR) a 9,0% (PI) e
   é alta tanto onde Lula venceu (PI 9,0%, RN 8,1%, BA 7,5%) quanto onde Flávio venceu com folga (RS 8,45%, SC
   7,5%, RJ 7,5%). Parece uma característica da seção, provavelmente ligada à idade do eleitorado e ao estado dos
   leitores biométricos.

![Liberação manual por estado](docs/graficos/09_biometria_por_estado.png)

Também li o log de 10.809 urnas, eleitor a eleitor: as seções das 19h, 1.500 vizinhas e uma amostra aleatória de
3.000 seções. Em 100% delas as liberações no log batem com o boletim. A taxa é maior de manhã e cai ao longo do dia,
e nas seções abertas até as 19h só 245 eleitores foram liberados depois das 17h (0,006% da margem, mesmo que todos
fossem de Lula). Liberações usadas para encher urnas no fim do dia deixariam o padrão oposto.

| Grupo | Votos | % manual no dia | Votos depois das 17h | Liberações manuais depois das 17h |
|---|---|---|---|---|
| Amostra aleatória do Brasil | 771.027 | 6,84% | 193 | 20 |
| Seções que fecharam às 19h | 1.861.259 | 6,35% | 4.492 | 245 |
| Vizinhas que fecharam até 17h15 | 435.553 | 6,66% | 172 | 17 |

![Liberação manual por hora](docs/graficos/10_liberacao_manual_por_hora_logs.png)

Em 16 seções um único mesário liberou 50 ou mais eleitores (máximo de 165, no Rio); vale conferir esses casos nas atas.

Veredito: sem sinal de que a liberação tenha favorecido Lula. Os cenários 1 e 2 inverteriam o resultado, mas exigem
voto em bloco dos liberados, e os testes 3 e 4 não mostram sinal disso. Como os dados são por seção, não dá para
saber como cada eleitor votou.
Detalhes em [`BIOMETRIA.md`](analise/BIOMETRIA.md).

### H7. Seções com 100% para Lula indicam fraude?

| Eleição | 100% Lula | 100% adversário | >90% Lula | >90% adversário |
|---|---|---|---|---|
| 2º turno 2026 | 106 | 4 | 6.816 | 378 |
| 1º turno 2026 | 81 | 8 | 6.005 | 713 |
| 2º turno 2022 | 143 | 4 | 9.433 | 213 |

As contagens que circularam (106 contra 4) estão certas. Mas 75% das seções com mais de 90% para Lula estão em MA,
BA, PI, PE e CE, onde ele teve entre 69% e 76%, e 2022 tem o mesmo desenho (143 contra 4).

Veredito: refutada. É voto regional.

### H8. A Lei de Benford mostra números inventados?

| Teste | Resultado |
|---|---|
| 1º dígito | Lula e Flávio "falham" do mesmo jeito (dígito 1 em ~61%). É o esperado: o voto de um candidato numa seção fica entre 100 e 199 em 61% dos casos. O teste não serve para votos por seção (Deckert, Myagkov & Ordeshook, 2011). |
| 2º dígito | Média real de 3,86 (Lula) e 3,97 (Flávio). Numa eleição honesta simulada para Lula com o mesmo tamanho de seção, 3,87. |
| Último dígito (Beber & Scacco) | Uniforme para os dois (qui-quadrado 5,0 e 12,4; limite 16,9). |

Veredito: sem sinal. Testes de dígitos detectam pouca coisa e são um complemento fraco aos testes de contagem.

### H9. O 2º turno destoa do 1º, seção por seção?

A mesma seção, com os mesmos eleitores, votou duas vezes em três semanas. Se urnas tivessem sido manipuladas no 2º
turno, essas seções sairiam do padrão que o 1º turno indicava.

`analise/primeiro_turno.py` usa o 1º turno de cada seção (votos de Lula, de Flávio, dos outros candidatos,
brancos, nulos e abstenção) para prever quanto Lula teria nela no 2º turno. Depois compara o previsto com o real. Para
não depender de uma escolha só, fiz a conta de seis jeitos (comparando o país todo, só dentro de cada estado ou só
dentro de cada cidade, com variações de fórmula). O 1º turno prevê bem o 2º: a previsão erra, em média, uns 2 pontos
por seção, e explica 93% das diferenças entre seções da mesma cidade.

![Previsto × real](docs/graficos/05_previsto_vs_real.png)

![Desvio por grupo](docs/graficos/06_desvio_por_grupo.png)

Nenhum grupo suspeito se desvia a favor de Lula. Nas seções das 19h, a diferença entre o real e o previsto fica entre
−0,12 e +0,18 ponto, pequena demais para se distinguir do acaso em qualquer dos seis jeitos. As seções com muita
liberação manual (20% ou mais) ficam abaixo do previsto para Lula em todas as formas (−0,19 a −0,58 p.p.), um desvio pequeno a favor de Flávio, de 3 a 10 mil
votos, que deve vir do perfil dessas seções.

Há 573 seções muito fora do padrão (erro mais de 4 vezes maior que o típico), divididas entre os dois lados; somando só os desvios a favor
de Lula, dá 8.044 votos, e o efeito líquido é de 3.233. O corte em 4 vezes serve para listar casos, não para
testar: com 2 vezes são 22.983 seções e efeito líquido de 52.685 votos a favor de Lula (1,2% da margem). Lista em
[`secoes_fora_do_padrao_1t_2t.csv`](analise/secoes_fora_do_padrao_1t_2t.csv).

Este teste não pega tudo. Uma manipulação igual em todas as seções passaria por ele: se tivesse acontecido depois da
urna, apareceria na soma oficial e na recontagem do RDV (H1 e H2); se tivesse acontecido dentro da urna, RDV, boletim
e log sairiam coerentes entre si, e só a auditoria do software poderia pegá-la. Ele também não vê manipulação que
tenha ocorrido igual no 1º turno.

Veredito: refutada. Detalhes em [`PRIMEIRO_TURNO.md`](analise/PRIMEIRO_TURNO.md).

### H10. Os dados ficaram "trancados" por 72 horas?

| Evento | Quando |
|---|---|
| Resultado oficial assinado (totalização) | 25/10, 23h28 |
| Planilha BWeb gerada | 26/10, 07h42 |
| BWeb no servidor (`Last-Modified`) | 26/10, por volta das 09h00 de Brasília; o arquivo do exterior, às 16h49 |
| Arquivos originais das urnas no servidor | 26/10, entre 15h26 e 17h01 de Brasília |
| BWeb listada no catálogo do portal | 27/10, por volta das 19h no relógio do catálogo |

Os arquivos estavam no servidor cerca de 1 dia depois da eleição, mas só apareceram no catálogo, que é onde as
pessoas procuram, cerca de 2 dias depois, e em 29/10 já tinham saído dele de novo.

Veredito: procede em parte. A crítica de que os dados demoraram a ficar acessíveis tem fundamento. A de que estavam
escondidos para serem alterados não encontra apoio: os arquivos batem com o resultado assinado às 23h28 do dia 25. A
conferência de fora seria com os boletins de papel afixados nas seções, que não foram comparados aqui.

---

## 3. Conclusão

Os dados públicos do TSE não mostram sinal de que o resultado do 2º turno tenha sido fabricado ou alterado. O
resultado oficial é a soma exata dos boletins, os boletins batem voto a voto com o que cada urna gravou, e nenhum
grupo de seções suspeito se afasta a favor de Lula do que o próprio 1º turno indicava. Quase todos os números das
suspeitas se reproduzem; o erro está na leitura: relógio local tomado por Brasília, regiões misturadas, aptos contados
como votantes e grandezas que não se comparam.

Quanto cada suspeita poderia pesar, no cenário considerado:

| Suspeita | Votos | % da margem |
|---|---|---|
| Anular todas as seções que fecharam às 19h | 185.724 | 4,2% |
| Seções das 19h: limite de 95% do desvio em relação ao 1º turno | 18.771 | 0,4% |
| Seções muito fora do padrão 1º → 2º turno (só desvios a favor de Lula) | 8.044 | 0,2% |
| Seções com urna sem explicação nos dados (todos os votos) | 4.563 | 0,1% |
| Seções das 19h: todos os votos dados depois das 17h | 4.492 | 0,1% |
| Liberação manual, limite de 95% comparando dentro do município | margem cairia para 2,55 mi | 42% |
| Liberação manual, pior caso aritmético (todo liberado votou em Lula) | margem viraria −4,19 mi | 195% |

![Quanto da margem cada suspeita poderia explicar](docs/graficos/08_suspeitas_vs_margem.png)

A liberação manual é a única suspeita com cenários que invertem o resultado, e todos eles supõem que os liberados
votaram em bloco ou que a geografia não explica a relação. Os testes contra o 1º turno (H6, itens 3 e 4) não mostram
sinal de nenhuma das duas coisas.

Continua em aberto, e não foi testado:

- As assinaturas digitais dos arquivos das urnas (`*.vsc`) não foram verificadas criptograficamente. Elas provariam
  que os arquivos foram gerados por urnas oficiais. É a principal limitação técnica.
- Nenhum boletim de papel foi comparado com os arquivos. Tudo aqui compara arquivos publicados pelo TSE entre si; a
  conferência de fora seria com boletins fotografados por fiscais de partido.
- Nenhuma análise de dados prova que o software da urna é honesto. Isso cabe aos testes públicos de segurança e à
  fiscalização. O que os dados mostram é que boletim, RDV, logs e resultado oficial contam a mesma história.
- Logs foram lidos para todas as urnas de AC, RR e AP, para as 6.352 seções das 19h, para dois sorteios de seções
  vizinhas e para uma amostra aleatória de 3.000 seções (11.382 urnas distintas somando as duas leituras), não para todas. As leituras
  remotas foram feitas por download parcial, sem hash do pacote inteiro, e conferidas contra a planilha.
- Por que cerca de 1.100 locais ficaram abertos até as 19h e o que explica as 17 urnas sem registro só os atos dos
  TREs e as atas dizem.
- Afirmações políticas e jurídicas não estão nos dados de votação.

---

## 4. Extra: como o voto mudou do 1º para o 2º turno

A forma mais direta de ver quem ganhou terreno é olhar só a disputa entre os dois: a % de Lula entre os votos de
Lula e de Flávio. No país ela foi de 49,0% no 1º turno para 51,8% no 2º, uma virada de 2,8 pontos.

![Lula ganhou terreno sobre Flávio em todos os estados](docs/graficos/12_mapa_estados_disputa.png)

Lula avançou em todos os 27 estados. O avanço foi maior no Sudeste e no Centro-Oeste (Rio +4,3 p.p., São Paulo +3,8,
Goiás +3,7) e menor no Nordeste, onde ele já era muito forte no 1º turno e tinha menos espaço para crescer (Piauí
+1,2, Bahia +1,4).

![Onde Lula e Flávio ganharam terreno, por município](docs/graficos/11_mapa_municipios_disputa.png)

Por município o desenho se repete: Lula ganhou terreno em 5.411 dos 5.571, com mediana de +2,4 p.p. Dos 160 em que
Flávio avançou (em azul), 123 estão no Nordeste, sobretudo na Bahia (86) e no Piauí (21), onde Lula já tinha
votações muito altas. O vermelho mais forte aparece em São Paulo, Goiás, Minas e Rio. A conta é por município e não
mostra para onde foi cada eleitor.

De onde veio essa virada? Do 1º para o 2º turno, Lula foi de 45,2% para 51,8% dos válidos (+6,6 p.p.) e Flávio de
47,0% para 48,2% (+1,2). Os dois crescem quase por construção, porque no 1º turno havia outros candidatos: dos 7,8
pontos que eles somavam, 6,6 foram para Lula e 1,2 para Flávio.

![Crescimento de Lula e de Flávio do 1º para o 2º turno, por estado](docs/graficos/13_mapa_estados_validos.png)

Lula cresceu em votos válidos em todos os estados, de +4,5 p.p. em Rondônia a +9,3 em Goiás. Flávio cresceu pouco e
caiu em sete estados do Nordeste. Em Goiás os dois cresceram mais que no resto do país (Lula +9,3, Flávio +6,1),
porque ali Ronaldo Caiado teve 12,3% dos válidos no 1º turno. Comparecimento e resultado por UF:
[`PRIMEIRO_TURNO.md`](analise/PRIMEIRO_TURNO.md), seção 9.

---

## Apêndice A. Glossário

| Termo | O que significa |
|---|---|
| Seção | Uma "mesa" de votação: uma sala, uma urna, algumas centenas de eleitores. O Brasil tem cerca de 499 mil. |
| Local de votação | O prédio (geralmente uma escola) onde ficam várias seções. |
| BU (Boletim de Urna) | O resultado que a urna imprime e grava no fim da votação, com o total de cada candidato. |
| BWeb | A planilha do TSE com o conteúdo de todos os BUs. |
| RDV (Registro Digital do Voto) | Arquivo da urna com cada voto digitado, embaralhado (sem dizer quem votou). Permite recontar. |
| Log da urna | Diário automático da urna, com a hora de cada evento (eleitor liberado, voto computado, erro…). |
| Aptos / comparecimento | Quem podia votar / quem votou. |
| % Lula | Neste trabalho, salvo aviso: votos de Lula ÷ (Lula + Flávio). |
| Margem | Votos de Lula − votos de Flávio: 4.430.191. |
| Saldo | Votos de Lula − votos de Flávio dentro de um grupo de seções. |
| Liberação manual | Quando a digital do eleitor falha 4 vezes e o mesário libera por outro caminho. É o número chamado de "sem biometria" (8,6 milhões). Não confundir com quem não tem biometria cadastrada (outra linha do BU). |
| Urna de contingência | Urna reserva, preparada antes, que substitui uma urna com defeito. |
| Hash SHA-512 | Uma espécie de impressão digital do arquivo: se um byte muda, o hash muda. |
| Horário local × Brasília | A urna grava a hora no fuso do lugar. No Acre, 17h de Brasília aparece como 15h. |
| p.p. (pontos percentuais) | Diferença entre porcentagens: de 50% para 52% são 2 p.p. |
| Resíduo / desvio | Diferença entre o resultado real de uma seção e o que se esperava dela a partir do 1º turno. |
| Comparar "dentro do município" | Comparar só seções da mesma cidade, para que diferenças entre regiões não atrapalhem. |
| Margem de erro de 95% / EP | Faixa onde o valor verdadeiro provavelmente está. EP = erro-padrão; ±1,96 EP dá a margem de 95%. |

## Apêndice B. De onde veio cada dado

Os dados da eleição vêm do Portal de Dados Abertos do TSE (<https://dadosabertos.tse.jus.br>) e do servidor de
arquivos do TSE (`cdn.tse.jus.br`); a malha dos mapas vem do IBGE. Tudo baixado em 29/10/2026.

| # | Dado | Conteúdo | Origem | No repositório | Tamanho | Conferência |
|---|---|---|---|---|---|---|
| A | BUs do 2º turno 2026 (BWeb, todos os cargos) | Todas as seções: votos, horários, liberações | [Resultados 2026 – Boletim de Urna](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna) | `dados/tse/2026/boletim_urna/2turno/` | 138 MB | `.sha512` oficial, 28/28 |
| B | BUs do 1º turno 2026 (todos os cargos) | Idem, 1º turno | mesmo link | só os `.sha512` (os .zip têm 4,8 GB) | — | `.sha512` oficial, 28/28 |
| C | Só as linhas de Presidente, 1º e 2º turno 2026 e 2º turno 2022 | Copiadas byte a byte de A, B e E | `scripts/extrair_presidente.py` | `dados/tse/2026/presidente/`, `dados/tse/2022/presidente/` | 406 MB | `MANIFESTO.csv` liga cada arquivo ao .zip oficial e ao hash do TSE |
| D | Correspondências esperadas, 2º turno | Urna e carga previstas por seção e urnas de contingência, geradas em 24/10/2026 às 12:31 | [Correspondências esperadas](https://dadosabertos.tse.jus.br/dataset/resultados-2026-correspondencias-esperadas-e-efetivadas-2-turno) | `dados/tse/2026/correspondencias/2turno/` | 36 MB | `.sha512` oficial, 28/28 |
| E | BUs do 2º turno 2022 | Comparação com a eleição anterior | [Resultados 2022 – Boletim de Urna](https://dadosabertos.tse.jus.br/dataset/resultados-2022-boletim-de-urna) | `dados/tse/2022/boletim_urna/2turno/` | 67 MB | `.sha512` oficial, 28/28 |
| F | Arquivos originais das urnas de AC, RR e AP | Por urna: BU digital, imagem do BU, RDV, log, assinatura | [Arquivos transmitidos para totalização](https://dadosabertos.tse.jus.br/dataset/resultados-2026-arquivos-transmitidos-para-totalizacao) | `dados/tse/2026/arquivos_urna/2turno/partes/` (pedaços de 90 MB) | 1,2 GB | sem hash oficial; `MANIFESTO.csv` próprio |
| G | RDV e logs das demais UFs | Lidos direto do servidor, baixando só o trecho necessário | mesmo link de F | resultados em `dados/derivados/` | — | conferidos contra a BWeb |
| H | Resultado oficial (Relatório Resultado da Totalização) | PDF assinado, Brasil e cada UF, 1º e 2º turnos | `cdn.tse.jus.br/.../Relatorio_Resultado_Totalizacao_2026_BR.zip` | `dados/tse/2026/totalizacao/` | 0,5 MB | sem hash oficial |
| I | Tabelas prontas | Uma linha por seção, logs das seções tardias, recontagem RDV, locais de votação | geradas pelos scripts | `dados/derivados/` | ~40 MB | regeneráveis |
| J | Malha municipal e estadual do IBGE | Polígonos e lista de municípios, só para os mapas | [API de malhas do IBGE](https://servicodados.ibge.gov.br/api/docs/malhas?versao=3) | `dados/ibge/` | 0,9 MB | `MANIFESTO.csv` próprio (URL, data, SHA-512) |

Também guardei o que o servidor informa sobre a data dos arquivos (`SERVIDOR.csv`) e quando o catálogo do portal os
listou (`CATALOGO.csv`), em `dados/tse/2026/boletim_urna/2turno/`.

## Apêndice C. Problemas nos dados

| # | Problema | Como resolvi |
|---|---|---|
| 1 | O horário de fechamento está no relógio local da urna. No Acre e no oeste do Amazonas, 17h de Brasília aparece como 15h; em MT, MS, RO, RR e no resto do AM, como 16h; em Fernando de Noronha, como 18h. | Converti por município. A prova está em [`FUSO.md`](analise/FUSO.md): as urnas abrem às 06h no AC, 07h no Norte/Centro-Oeste e 08h no resto, todas às 8h de Brasília. Dois sinais são compatíveis com isso: nenhum boletim chegou ao TSE antes das 17h05 de Brasília, e o log mostra o operador digitando a hora à mão na preparação. O exterior ficou fora da conversão. |
| 2 | O BU do 2º turno de Roraima não aparecia no catálogo, só o `.sha512`. | Baixei pela URL direta. Hash conferido. |
| 3 | Os BUs do 2º turno sumiram do catálogo entre a 1ª e a 2ª consulta (29/10). Os arquivos continuam no servidor, iguais. | Registrado em `CATALOGO.csv`. Não sei o motivo. |
| 4 | Os arquivos originais das urnas do 2º turno não estão no catálogo e não têm hash oficial. | Baixei pela URL padrão e registrei tamanho, SHA-512, data e ETag em `MANIFESTO.csv`. |
| 5 | O GitHub não aceita arquivos acima de 100 MB. | Pacotes das urnas em partes de 90 MB (`scripts/remontar_arquivos_urna.py` junta e confere). Do 1º turno, versionei só as linhas de Presidente. |
| 6 | Em 2022 o campo de biometria tem outro nome e o código do cargo vem entre aspas. | O leitor aceita os dois formatos. |
| 7 | O código de carga vem partido em duas colunas no BU, e a lista prévia perde zeros à esquerda. | Juntei e completei para 24 dígitos. |
| 8 | O leia-me diz que o log é 7z, mas é zip. Urnas substituídas trazem o log anterior dentro de outro zip. | O leitor abre os dois níveis. |
| 9 | O resultado oficial só existe em PDF. | Extraído com `pdftotext`. |
| 10 | Seções do exterior sem eleitores presentes não têm linhas de Presidente na BWeb (2 no 2º turno, 1 no 1º); no 2º turno aparecem só com cargo "-1". | Explica 499.205 seções com voto contra 499.207 em funcionamento no oficial. |
| 11 | 29 seções do exterior não têm horário porque foram apuradas em cédula (Sistema de Apuração): 27 com votos e as 2 sem votantes do problema 10. | O relatório oficial confirma: "29 seções apuradas pelo SA". |
| 12 | No 1º turno, o nº 28 teve 5.246 votos que não aparecem no resultado oficial. | São exatamente os 5.246 "votos nulos técnicos" do oficial (registro anulado). |

## Apêndice D. Como rodar tudo

Precisa de Python 3 e `pdftotext` (pacote `poppler-utils`).

```bash
git clone https://github.com/JardaCoder/independent-audit-brazil-elections-2026.git
cd independent-audit-brazil-elections-2026
pip install pandas numpy tabulate matplotlib geopandas   # geopandas só para os mapas

python3 scripts/remontar_arquivos_urna.py  # junta os pacotes das urnas de AC, RR e AP

cd analise
python3 totalizacao.py                  # H1  soma dos BUs × resultado oficial
python3 consistencia.py                 # H1  regras em cada BU
python3 recontagem_rdv.py AC RR AP      # H2  recontagem voto a voto (local)
python3 imagem_bu.py AC RR AP           # H2  imagem do BU × planilha
python3 logs_urna.py AC RR AP           # H2  log da urna × BU
python3 correspondencia.py              # H3  urnas usadas × previstas
python3 fuso.py                         # H4  prova de que a urna grava o horário local
python3 suspeitas.py                    # H4–H8 horário, seções das 19h, liberação, unânimes, Benford
python3 biometria.py                    # H6  liberação manual (usa cache; --refazer lê logs do servidor, ~30 min)
python3 primeiro_turno.py               # H9  1º × 2º turno
python3 graficos.py                     # gráficos e mapas em docs/graficos/

# Leem direto do servidor do TSE (demoram):
python3 logs_tardias.py --refazer       # H5  logs das 6.352 seções das 19h (~20 min)
python3 recontagem_rdv_nacional.py      # H2  RDV de todas as seções do país (~2 h)
```

Para baixar outros dados: `python3 scripts/baixar_dados_tse.py` lista os conjuntos.
Para refazer a extração de Presidente a partir dos .zip oficiais: `python3 scripts/extrair_presidente.py`.

## Apêndice E. Mapa do repositório

```
README.md                          este arquivo
docs/RELATORIO_DE_AUDITORIA.md     relatório formal: escopo, metodologia, achados, limitações e parecer
docs/graficos/                     gráficos e mapas deste README
analise/
  TOTALIZACAO.md, CONSISTENCIA.md  soma dos BUs × oficial e regras por BU (H1)
  RECONTAGEM_RDV_NACIONAL.md       recontagem voto a voto, Brasil (H2)
  RECONTAGEM_RDV.md, IMAGEM_BU.md, LOGS.md   AC/RR/AP: BU digital, imagem do BU e logs × planilha (H2)
  CORRESPONDENCIA.md               urnas usadas × previstas (H3)
  FUSO.md                          prova de que a urna grava o horário local (H4)
  RESULTADOS.md                    horário, seções das 19h, liberação, unânimes, Benford (H4 a H8)
  LOGS_TARDIAS.md                  votos depois das 17h nas seções das 19h (H5)
  BIOMETRIA.md                     liberação manual: por estado, município, hora e mesário (H6)
  PRIMEIRO_TURNO.md                1º × 2º turno (H9)
  secoes_para_documentar.csv       seções com urna/carga fora da lista
  secoes_fora_do_padrao_1t_2t.csv  seções muito fora do padrão entre turnos
  carregar.py                      lê os dados; fuso por município; faixas de horário
  estatistica.py                   modelos, comparações e margem de erro
  *.py                             um script por verificação (ver apêndice D)
scripts/
  baixar_dados_tse.py              baixa dados do TSE e confere o hash
  extrair_presidente.py            separa as linhas de Presidente dos .zip oficiais
  remontar_arquivos_urna.py        junta e confere as partes dos pacotes das urnas
dados/
  tse/2026/boletim_urna/2turno/    BWeb 2º turno (todos os cargos) + SERVIDOR.csv + CATALOGO.csv
  tse/2026/boletim_urna/1turno/    só os .sha512 (os .zip: baixar)
  tse/2026/presidente/             linhas de Presidente, 1º e 2º turno, + MANIFESTO.csv
  tse/2026/correspondencias/       urnas previstas por seção
  tse/2026/arquivos_urna/2turno/   arquivos originais das urnas AC/RR/AP (partes + MANIFESTO.csv)
  tse/2026/totalizacao/            resultado oficial (PDF)
  tse/2022/                        2º turno 2022 (comparação)
  derivados/                       tabelas prontas geradas pelos scripts
  ibge/                            malhas do IBGE para os mapas + MANIFESTO.csv
```

---

Trabalho independente, sem vínculo com o TSE, partidos ou candidatos.
