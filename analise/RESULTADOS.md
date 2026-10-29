# Verificação do "Relatório Pericial Independente" — 2º turno 2026

Fonte: Boletins de Urna (BWeb) do 2º turno, `dados/tse/2026/boletim_urna/2turno/`, conferidos com os hashes SHA-512 publicados pelo TSE. Cargo: Presidente.

## Totais (conferem com o relatório)

- Seções: 499.205
- Comparecimento: 128.236.074
- Lula (13): 64.256.232 (51.79% dos válidos)
- Flávio Bolsonaro (22): 59.826.041
- Margem: 4.430.191
- Eleitores liberados sem biometria (QT_ELEI_BIOM_SEM_HABILITACAO): 8.632.488 (6.73% do comparecimento)

## Réplica exata das tabelas do relatório (Cap. 1 e 2)

O relatório usa o relógio local da urna e as faixas até 17:00:59, 17:01–17:15:59, 17:16–18:59:59 e 19:00–19:59:59. Com esse corte, todos os números dele se reproduzem:

### 2026 (Lula × Flávio Bolsonaro)

| faixa         | secoes   | comparecimento   | lula       | adversario   | pct_estados_oeste   | % Lula   | saldo Lula   |
|:--------------|:---------|:-----------------|:-----------|:-------------|:--------------------|:---------|:-------------|
| até 17:00:59  | 150.771  | 37.630.420       | 17.369.159 | 19.116.798   | 21.2                | 47.61    | -1.747.639   |
| 17:01–17:15   | 339.593  | 88.071.750       | 45.525.188 | 39.627.772   | 0.0                 | 53.46    | 5.897.416    |
| 17:16–18:59   | 2.472    | 674.799          | 372.470    | 279.102      | 0.4                 | 57.16    | 93.368       |
| 19:00–19:59   | 6.333    | 1.856.306        | 987.956    | 801.108      | 0.0                 | 55.22    | 186.848      |
| 20h ou depois | 9        | 1.968            | 1.014      | 908          | 0.0                 | 52.76    | 106          |

### 2022 (Lula × Jair Bolsonaro, grupo de controle)

| faixa         | secoes   | comparecimento   | lula       | adversario   | pct_estados_oeste   | % Lula   | saldo Lula   |
|:--------------|:---------|:-----------------|:-----------|:-------------|:--------------------|:---------|:-------------|
| até 17:00:59  | 195.818  | 49.926.557       | 23.374.900 | 24.414.955   | 15.1                | 48.91    | -1.040.055   |
| 17:01–17:15   | 274.561  | 73.883.315       | 36.731.439 | 33.607.908   | 0.0                 | 52.22    | 3.123.531    |
| 17:16–18:59   | 1.585    | 434.753          | 235.306    | 179.999      | 0.1                 | 56.66    | 55.307       |
| 19:00–19:59   | 15       | 2.908            | 1.762      | 1.003        | 0.0                 | 63.73    | 759          |
| 20h ou depois | 5        | 1.023            | 597        | 407          | 0.0                 | 59.46    | 190          |

O mesmo corte aplicado a 2022 mostra o mesmo padrão de "duas eleições": o candidato 22 vence nas urnas que fecham até 17:00:59 e Lula vence nas que fecham depois. A explicação é a composição dos grupos, não o horário. O primeiro grupo concentra as urnas dos estados a oeste (relógio local 15h/16h, onde o candidato 22 é forte) e as seções menores, sem fila. A faixa 17:01–17:15 não é prorrogação: é o fechamento normal de quem ainda estava na fila às 17h, e reúne 68% das seções do país.

## Cap. 1 e 2 — horário de encerramento

`DT_ENCERRAMENTO` é gravado no **relógio local da urna**. AC, AM, MT, MS, RO e RR estão 1 ou 2 horas atrás de Brasília. Por isso as urnas desses estados aparecem "fechando antes das 17h", mas na verdade fecharam às 17h de Brasília.

### Relógio local (como está no arquivo)

| janela          | secoes   | comparecimento   | lula       | flavio     | % Lula   | saldo Lula   |
|:----------------|:---------|:-----------------|:-----------|:-----------|:---------|:-------------|
| até 17h00       | 32.025   | 7.619.112        | 2.990.292  | 4.433.690  | 40.28    | -1.443.398   |
| 17h00 a 17h15   | 458.091  | 118.015.011      | 59.864.997 | 54.284.154 | 52.44    | 5.580.843    |
| 17h15 a 18h59   | 2.720    | 742.846          | 411.528    | 305.828    | 57.37    | 105.700      |
| 19h00 ou depois | 6.342    | 1.858.274        | 988.970    | 802.016    | 55.22    | 186.954      |

Seções no grupo "até 17h00" (relógio local), por UF: MT 8.278, AM 8.156, MS 7.106, RO 4.697, AC 2.269, RR 1.519.

### Convertido para horário de Brasília

| janela          | secoes   | comparecimento   | lula       | flavio     | % Lula   | saldo Lula   |
|:----------------|:---------|:-----------------|:-----------|:-----------|:---------|:-------------|
| até 17h00       | 556      | 140.507          | 94.120     | 40.850     | 69.73    | 53.270       |
| 17h00 a 17h15   | 489.462  | 125.469.798      | 62.749.380 | 58.665.623 | 51.68    | 4.083.757    |
| 17h15 a 18h59   | 2.808    | 763.679          | 422.468    | 315.120    | 57.28    | 107.348      |
| 19h00 ou depois | 6.352    | 1.861.259        | 989.819    | 804.095    | 55.18    | 185.724      |

- Considerando só as seções que fecharam até 17h15 (Brasília), Lula ainda vence por **4.137.027** votos.
- As 6.342 seções que fecharam às 19h ou depois deram a Lula um saldo de 186.954 votos, ou 4.2% da margem final.
- O "grupo que fechou até 17h" em que Flávio vence é efeito de fuso horário: são as urnas de AC, AM, MT, MS, RO e RR, que fecharam às 15h ou 16h no relógio local, ou seja, 17h de Brasília. São estados em que Flávio vence. Não existe "eleição até as 17h" separada de uma "eleição depois das 17h".

### Seções encerradas às 19h ou depois, por UF

| SG_UF   | secoes   | lula    | flavio   | % Lula nas seções tardias   | % Lula no estado todo   |
|:--------|:---------|:--------|:---------|:----------------------------|:------------------------|
| RJ      | 2.805    | 370.026 | 437.760  | 45.81                       | 46.9                    |
| SP      | 1.571    | 233.402 | 172.816  | 57.46                       | 46.15                   |
| BA      | 936      | 201.695 | 77.225   | 72.31                       | 71.31                   |
| PE      | 657      | 125.972 | 65.779   | 65.7                        | 69.2                    |
| PB      | 275      | 42.964  | 38.777   | 52.56                       | 67.46                   |
| SE      | 51       | 8.775   | 4.657    | 65.33                       | 69.53                   |
| DF      | 17       | 1.718   | 1.994    | 46.28                       | 45.72                   |
| PA      | 8        | 1.218   | 995      | 55.04                       | 55.02                   |
| PI      | 7        | 1.136   | 406      | 73.67                       | 75.88                   |
| MA      | 3        | 519     | 104      | 83.31                       | 69.54                   |
| RN      | 3        | 527     | 346      | 60.37                       | 65.72                   |
| AL      | 2        | 362     | 154      | 70.16                       | 60.77                   |
| ES      | 2        | 167     | 338      | 33.07                       | 43.63                   |
| RS      | 2        | 239     | 251      | 48.78                       | 42.16                   |
| GO      | 1        | 79      | 216      | 26.78                       | 40.34                   |
| MG      | 1        | 78      | 18       | 81.25                       | 50.43                   |
| PR      | 1        | 93      | 180      | 34.07                       | 37.42                   |

Em SP, 1.481 das 1.571 seções tardias ficam na capital (SÃO PAULO). Ou seja, comparar com "o restante do estado" mistura a capital com o interior. No RJ, que tem mais seções tardias que qualquer outro estado, Flávio venceu nessas seções.

## Cap. 3 — biometria

- Correlação (seção) entre % liberado sem biometria e % Lula: **0.068** no país; **0.012** comparando seções dentro do mesmo município. Na prática, nenhuma.

| % sem biometria na seção   | secoes   | lula       | flavio     | sem_biometria   | % Lula   |
|:---------------------------|:---------|:-----------|:-----------|:----------------|:---------|
| 0-2%                       | 19.118   | 2.468.276  | 2.264.179  | 65.416          | 52.16    |
| 2-5%                       | 157.893  | 20.729.348 | 19.877.339 | 1.565.408       | 51.05    |
| 5-10%                      | 237.829  | 30.521.272 | 28.758.874 | 4.336.218       | 51.49    |
| 10-20%                     | 80.331   | 10.061.133 | 8.584.117  | 2.454.737       | 53.96    |
| 20-30%                     | 3.686    | 433.883    | 313.052    | 174.933         | 58.09    |
| 30-50%                     | 251      | 28.656     | 19.818     | 17.324          | 59.12    |
| 50-100%                    | 97       | 13.664     | 8.662      | 18.452          | 61.2     |

- Taxa sem biometria: Nordeste 7.19%, resto do país 6.55%. A taxa é parecida em todo o país, inclusive onde Flávio venceu.
- Tirando todos os eleitores sem biometria, supondo que votaram como o resto da própria seção, Lula ainda venceria por **4.017.767** votos.
- Comparar 8,6 milhões com a margem de 4,4 milhões só faria sentido se esses votos fossem todos de um candidato. Os dados mostram que não são.
- O campo da BWeb corresponde à linha "Habilitação biográfica" do BU impresso: o eleitor tinha biometria cadastrada e a digital falhou 4 vezes. Pelos logs das urnas (LOGS.md), nesse caso a urna pede um dado pessoal do eleitor, recusa se ele não confere e depois exige a digital do mesário. Não é a "simples digitação do ano de nascimento" descrita no relatório. Digitar o ano de nascimento sozinho é o caminho de outro grupo, o dos eleitores sem biometria cadastrada, que o BU conta em outra linha.
- Em 2022 o campo mais próximo (QT_ELEITORES_BIOMETRIA_NH, "não habilitados por biometria"; nome e talvez definição diferentes) somou 10.011.346 eleitores, 4.7 vezes a margem daquele ano (2.139.645). A razão "quase o dobro da margem" de 2026 é menor que a de 2022.

## Cap. 4 — seções quase unânimes

- 100% dos válidos: Lula 106, Flávio 4. Acima de 90%: Lula 6816, Flávio 378.
- As seções com mais de 90% para Lula se concentram em MA (1549), BA (1345), PI (870), PE (667), CE (662). Lula teve 69.4% dos válidos no Nordeste como um todo. Quando a média regional é perto de 70%, a cauda acima de 90% fica toda de um lado. A distribuição não é "gaussiana em torno de 50%" porque o voto no Brasil é fortemente regional.

## Cap. 5 — Lei de Benford (o relatório não mostrou o resultado)

|    | Benford esperado %   | Lula %   | Flávio %   |
|:---|:---------------------|:---------|:-----------|
| 1  | 30.1                 | 60.8     | 61.9       |
| 2  | 17.6                 | 9.3      | 7.2        |
| 3  | 12.5                 | 0.9      | 2.8        |
| 4  | 9.7                  | 1.7      | 3.4        |
| 5  | 7.9                  | 2.8      | 3.9        |
| 6  | 6.7                  | 4.3      | 4.3        |
| 7  | 5.8                  | 5.6      | 4.9        |
| 8  | 5.1                  | 6.9      | 5.4        |
| 9  | 4.6                  | 7.7      | 6.1        |

Os dois candidatos "falham" do mesmo jeito. Isso é esperado: a seção tem um teto de cerca de 400 eleitores, então a contagem por seção cai quase sempre entre 100 e 199 e o dígito 1 domina. A literatura considera o 1º dígito de Benford inadequado para contagens por seção eleitoral (Deckert, Myagkov & Ordeshook, 2011). Esse teste não serve como evidência para nenhum dos lados.

