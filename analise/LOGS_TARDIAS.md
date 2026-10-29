# Votos depois das 17h nas seções que fecharam às 19h (2º turno 2026)

Fonte: log de cada urna (`logd.dat`), lido direto do pacote oficial "arquivos transmitidos para totalização" do TSE por download parcial. O horário foi convertido para Brasília. Grupo de controle: amostra aleatória (semente 2026) de seções do **mesmo local de votação** que fecharam até 17h15.

Seções analisadas: 7.852 (0 com erro de leitura ou sem log).

## Quantos votos depois das 17h

| grupo                        | secoes   | comparecimento_BU   | votos_no_log   | apos_17h00   | apos_17h15   | apos_17h30   | apos_18h00   | apos_18h30   | % dos votos após 17h   | % dos votos após 17h15   |
|:-----------------------------|:---------|:--------------------|:---------------|:-------------|:-------------|:-------------|:-------------|:-------------|:-----------------------|:-------------------------|
| fechou 19h ou depois         | 6.352    | 1.861.259           | 1.861.259      | 4.492        | 3.329        | 2.907        | 1.860        | 671          | 0.24                   | 0.18                     |
| vizinha que fechou até 17h15 | 1.500    | 432.813             | 432.813        | 155          | 0            | 0            | 0            | 0            | 0.04                   | 0.0                      |

- Log = comparecimento do BU: 7.852 de 7.852 seções.
- Seções tardias **sem nenhum voto** depois das 17h15: 3.885 de 6.352.
- Votos dados depois das 17h00 nas seções tardias: **4.492** de 1.861.259 (0.24%). Mesmo que **todos** fossem ilegítimos e todos de Lula, o efeito máximo sobre a margem de 4.430.191 seria de 4.492 votos (0.10%).
- Votos entre 17h00 e 17h15 são normais: é quem estava na fila às 17h. As vizinhas de controle também os têm.
- Seções tardias com mais de 10% dos votos depois das 17h15: 0.

## Seções tardias por fração de votos dados depois das 17h15

| faixa   |   secoes |   votos_apos_17h15 |   lula |   flavio |   % Lula |
|:--------|---------:|-------------------:|-------:|---------:|---------:|
| 0       |     3885 |                  0 | 590531 |   485190 |    54.9  |
| até 2%  |     2465 |               3299 | 398923 |   318823 |    55.58 |
| 5–10%   |        2 |                 30 |    365 |       82 |    81.66 |

## Votos depois das 17h nas seções tardias, por janela de 15 minutos (Brasília)

|       |   votos |
|:------|--------:|
| 17h00 |    1163 |
| 17h15 |     422 |
| 17h30 |     503 |
| 17h45 |     544 |
| 18h00 |     611 |
| 18h15 |     578 |
| 18h30 |     435 |
| 18h45 |     225 |
| 19h00 |      11 |

## Por UF (seções tardias)

| SG_UF   |   secoes |   votos |   apos_17h15 |    % |
|:--------|---------:|--------:|-------------:|-----:|
| RJ      |     2805 |  837298 |         1413 | 0.17 |
| SP      |     1571 |  424443 |         1037 | 0.24 |
| BA      |      936 |  290085 |          510 | 0.18 |
| PE      |      657 |  197323 |          216 | 0.11 |
| PB      |      275 |   83750 |           92 | 0.11 |
| SE      |       51 |   13885 |           12 | 0.09 |
| DF      |       17 |    3842 |            2 | 0.05 |
| MT      |        9 |    2778 |            2 | 0.07 |
| PA      |        8 |    2285 |            4 | 0.18 |
| PI      |        7 |    1584 |            1 | 0.06 |
| RN      |        3 |     891 |            7 | 0.79 |
| MA      |        3 |     634 |           11 | 1.74 |
| AL      |        2 |     535 |           19 | 3.55 |
| RS      |        2 |     499 |            0 | 0    |
| ES      |        2 |     530 |            2 | 0.38 |
| AC      |        1 |     207 |            0 | 0    |
| GO      |        1 |     309 |            0 | 0    |
| MG      |        1 |      96 |            0 | 0    |
| PR      |        1 |     285 |            1 | 0.35 |

