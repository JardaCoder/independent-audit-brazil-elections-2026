# Liberação manual de eleitores ("sem biometria") — análise dedicada

O que é: quando a digital do eleitor falha 4 vezes, a urna pede um dado pessoal e exige a digital do mesário para liberar o voto. O BWeb conta esses casos no campo `QT_ELEI_BIOM_SEM_HABILITACAO` (8.632.488 no 2º turno). Os testes de efeito no voto estão em `RESULTADOS.md` (seção 5) e `PRIMEIRO_TURNO.md` (seção 5).

## 1. Taxa de liberação manual por estado (todas as seções do Brasil; no exterior não há biometria)

Taxa = eleitores liberados manualmente ÷ comparecimento. "% Lula" = Lula ÷ (Lula + Flávio) no 2º turno.

| SG_UF   | liberados 2º turno   | taxa 1º turno (%)   | taxa 2º turno (%)   | variação (p.p.)   | % Lula 2º turno   | mediana por seção (%)   | seções com taxa ≥ 20%   |
|:--------|:---------------------|:--------------------|:--------------------|:------------------|:------------------|:------------------------|:------------------------|
| PI      | 201.641              | 8.65                | 9.0                 | 0.35              | 75.9              | 8.3                     | 378                     |
| RS      | 582.380              | 8.23                | 8.45                | 0.22              | 42.2              | 7.8                     | 743                     |
| RN      | 180.838              | 7.91                | 8.1                 | 0.19              | 65.7              | 7.6                     | 33                      |
| SC      | 357.632              | 7.56                | 7.51                | -0.05             | 30.6              | 7.0                     | 189                     |
| BA      | 702.255              | 7.29                | 7.45                | 0.16              | 71.3              | 6.7                     | 569                     |
| RJ      | 750.301              | 7.05                | 7.45                | 0.4               | 46.9              | 6.9                     | 199                     |
| PB      | 199.353              | 6.97                | 7.27                | 0.3               | 67.5              | 6.7                     | 49                      |
| MS      | 115.545              | 7.82                | 7.25                | -0.57             | 40.4              | 6.6                     | 91                      |
| CE      | 429.294              | 6.88                | 7.13                | 0.25              | 68.9              | 6.4                     | 400                     |
| PR      | 493.321              | 7.48                | 6.99                | -0.49             | 37.4              | 6.4                     | 183                     |
| SE      | 102.204              | 6.76                | 6.97                | 0.21              | 69.5              | 6.5                     | 24                      |
| AL      | 135.874              | 6.53                | 6.96                | 0.43              | 60.8              | 6.1                     | 128                     |
| MG      | 887.910              | 6.69                | 6.81                | 0.12              | 50.4              | 6.2                     | 447                     |
| Brasil  | 8.632.488            | 6.68                | 6.75                | 0.07              | 51.8              | 6.1                     | 4.154                   |
| GO      | 268.656              | 6.8                 | 6.64                | -0.16             | 40.3              | 5.9                     | 165                     |
| MT      | 137.579              | 6.72                | 6.6                 | -0.12             | 33.9              | 6.2                     | 19                      |
| PE      | 399.764              | 6.25                | 6.53                | 0.28              | 69.2              | 6.0                     | 90                      |
| MA      | 259.852              | 5.99                | 6.3                 | 0.31              | 69.5              | 5.7                     | 82                      |
| ES      | 151.401              | 6.43                | 6.28                | -0.15             | 43.6              | 5.8                     | 33                      |
| RO      | 61.938               | 6.24                | 6.27                | 0.03              | 30.4              | 5.9                     | 3                       |
| SP      | 1.632.098            | 6.02                | 5.96                | -0.06             | 46.2              | 5.5                     | 246                     |
| PA      | 277.373              | 5.4                 | 5.56                | 0.16              | 55.0              | 5.1                     | 69                      |
| AM      | 118.955              | 5.39                | 5.43                | 0.04              | 54.0              | 5.0                     | 6                       |
| AC      | 22.654               | 4.99                | 4.99                | 0.0               | 33.4              | 4.7                     | 5                       |
| TO      | 47.225               | 5.28                | 4.95                | -0.33             | 48.6              | 4.6                     | 2                       |
| AP      | 19.685               | 4.4                 | 4.58                | 0.18              | 52.9              | 4.3                     | 0                       |
| DF      | 84.114               | 4.84                | 4.5                 | -0.34             | 45.7              | 4.2                     | 1                       |
| RR      | 12.646               | 3.84                | 4.1                 | 0.26              | 27.5              | 3.9                     | 0                       |

- A taxa vai de 4.10% (RR) a 9.00% (PI). Correlação, entre estados, da taxa com a % de Lula: 0.38 (IC 95%: -0.00 a 0.66; só 27 estados, sem ponderar pelo tamanho, e é uma comparação entre regiões, não entre eleitores).
- Do 1º para o 2º turno a taxa nacional mudou +0.07 p.p.; a maior variação estadual foi 0.57 p.p. A liberação não "apareceu" no 2º turno.

## 2. Municípios com as maiores taxas (com pelo menos 5.000 votantes)

| SG_UF   | NM_MUNICIPIO      | votantes   | liberados   | taxa (%)   | % Lula   |
|:--------|:------------------|:-----------|:------------|:-----------|:---------|
| PI      | JATOBÁ DO PIAUÍ   | 5.750      | 1.216       | 21.1       | 84.9     |
| PI      | SIGEFREDO PACHECO | 7.623      | 1.599       | 21.0       | 82.3     |
| PR      | TOMAZINA          | 5.381      | 1.059       | 19.7       | 40.0     |
| CE      | JAGUARIBARA       | 7.874      | 1.465       | 18.6       | 78.6     |
| RS      | CRUZEIRO DO SUL   | 7.852      | 1.454       | 18.5       | 32.3     |
| RS      | ROSÁRIO DO SUL    | 23.474     | 4.282       | 18.2       | 50.7     |
| RS      | PLANALTO          | 6.563      | 1.188       | 18.1       | 38.2     |
| BA      | BOTUPORÃ          | 7.687      | 1.381       | 18.0       | 78.2     |
| CE      | JAGUARETAMA       | 13.085     | 2.351       | 18.0       | 79.4     |
| BA      | BREJOLÂNDIA       | 6.452      | 1.145       | 17.7       | 67.6     |
| BA      | CORIBE            | 9.916      | 1.745       | 17.6       | 70.0     |
| PI      | SÃO JOÃO DA SERRA | 5.388      | 946         | 17.6       | 78.8     |
| MG      | CORDISBURGO       | 5.597      | 973         | 17.4       | 53.9     |
| PR      | MOREIRA SALES     | 7.532      | 1.298       | 17.2       | 40.0     |
| BA      | PARATINGA         | 19.826     | 3.411       | 17.2       | 80.1     |

Municípios divididos em cinco grupos pela taxa de liberação:

| taxa (%)           | municipios   | taxa mediana (%)   | % Lula   |
|:-------------------|:-------------|:-------------------|:---------|
| 20% com menor taxa | 739          | 4.9                | 51.0     |
| 2º quinto          | 781          | 6.1                | 49.6     |
| 3º quinto          | 672          | 7.1                | 51.2     |
| 4º quinto          | 750          | 8.5                | 54.9     |
| 20% com maior taxa | 704          | 11.3               | 57.9     |

## 3. O que os logs mostram, eleitor a eleitor

Cada log registra, para cada eleitor, como ele foi liberado e a hora do voto. Tipos: **biométrica** (digital reconhecida), **manual** (digital falhou 4 vezes; dado pessoal + digital do mesário), **sem biometria cadastrada** (eleitor sem digital no cadastro; ano de nascimento). Horário convertido para Brasília.

- Logs lidos: 10.852 de 10.852 (10.809 urnas distintas; 43 seções da amostra aleatória também estão em outro grupo). Conferência: liberações manuais no log = número do BU em 10.852 seções; votos no log = comparecimento em 10.852.

| grupo                        | secoes   | votos     | manuais   | votos_apos_17h   | manuais_apos_17h   | biometricas_apos_17h   | % manual (dia todo)   | % manual entre os votos após 17h   |
|:-----------------------------|:---------|:----------|:----------|:-----------------|:-------------------|:-----------------------|:----------------------|:-----------------------------------|
| amostra aleatória do Brasil  | 3.000    | 771.027   | 52.742    | 193              | 20                 | 155                    | 6.84                  | 10.36                              |
| fechou 19h ou depois         | 6.352    | 1.861.259 | 118.270   | 4.492            | 245                | 3.915                  | 6.35                  | 5.45                               |
| vizinha que fechou até 17h15 | 1.500    | 435.553   | 28.999    | 172              | 17                 | 143                    | 6.66                  | 9.88                               |

- Nas seções que ficaram abertas até as 19h, **245 eleitores** foram liberados manualmente depois das 17h, em 220 das 6.352 seções. Desses, 164 com o mesário identificado pela digital.
- Mesmo que todos esses 245 votos fossem ilegítimos e de Lula, o efeito sobre a margem de 4.430.191 seria 0.006%.
- Maior número de liberações manuais feitas por um único mesário numa seção: 165 (mediana entre as seções com alguma liberação: 9).

### Casos extremos: um mesário com 50 ou mais liberações na mesma seção

16 das 10.809 seções lidas. Em 2 delas quase todos os eleitores foram liberados manualmente de manhã e a digital voltou a funcionar à tarde (leitor biométrico com defeito, depois consertado ou trocado). Nas demais, a taxa é alta o dia inteiro, sem pico em nenhum horário. Em 11 das 16 a % de Lula na seção ficou **abaixo** da % na zona eleitoral; em 2, mais de 2 p.p. acima.

| UF   | município      | zona   | seção   | votos   | liberações manuais   | pelo mesmo mesário   | % manual 8h–12h   | % manual 13h em diante   | % Lula na seção   | % Lula na zona   |
|:-----|:---------------|:-------|:--------|:--------|:---------------------|:---------------------|:------------------|:-------------------------|:------------------|:-----------------|
| RJ   | Rio De Janeiro | 9      | 262     | 339     | 200                  | 165                  | 85                | 20                       | 40.0              | 39.8             |
| RJ   | Rio De Janeiro | 9      | 273     | 349     | 85                   | 84                   | 24                | 26                       | 36.0              | 39.8             |
| RJ   | Rio De Janeiro | 214    | 325     | 306     | 210                  | 74                   | 89                | 15                       | 59.8              | 58.7             |
| RJ   | Rio De Janeiro | 9      | 292     | 360     | 73                   | 72                   | 23                | 9                        | 38.4              | 39.8             |
| BA   | Tanhaçu        | 58     | 326     | 312     | 74                   | 64                   | 25                | 20                       | 77.3              | 74.8             |
| RJ   | Rio De Janeiro | 9      | 492     | 438     | 60                   | 58                   | 14                | 14                       | 44.3              | 39.8             |
| RJ   | Rio De Janeiro | 182    | 7       | 339     | 60                   | 56                   | 18                | 16                       | 45.0              | 44.7             |
| SP   | São Paulo      | 249    | 605     | 312     | 60                   | 53                   | 21                | 14                       | 38.1              | 43.9             |
| PB   | João Pessoa    | 76     | 280     | 337     | 54                   | 52                   | 18                | 8                        | 50.9              | 52.2             |
| PB   | João Pessoa    | 76     | 17      | 333     | 57                   | 51                   | 19                | 12                       | 43.6              | 52.2             |
| RJ   | Rio De Janeiro | 191    | 33      | 329     | 51                   | 51                   | 15                | 17                       | 48.9              | 49.1             |
| RJ   | Rio De Janeiro | 7      | 26      | 307     | 58                   | 51                   | 18                | 21                       | 54.7              | 62.1             |
| RJ   | Rio De Janeiro | 9      | 281     | 417     | 58                   | 51                   | 15                | 12                       | 39.0              | 39.8             |
| RJ   | Rio De Janeiro | 9      | 153     | 322     | 55                   | 51                   | 18                | 14                       | 31.1              | 39.8             |
| RJ   | Rio De Janeiro | 9      | 179     | 320     | 65                   | 51                   | 21                | 18                       | 36.2              | 39.8             |
| PB   | João Pessoa    | 76     | 263     | 349     | 53                   | 50                   | 17                | 10                       | 45.9              | 52.2             |

### Liberação manual por hora

| grupo                        | hora (Brasília)   | votos   | manuais   | % manual   |
|:-----------------------------|:------------------|:--------|:----------|:-----------|
| amostra aleatória do Brasil  | 08h               | 129.572 | 10.633    | 8.21       |
| amostra aleatória do Brasil  | 09h               | 120.251 | 9.014     | 7.5        |
| amostra aleatória do Brasil  | 10h               | 115.409 | 8.066     | 6.99       |
| amostra aleatória do Brasil  | 11h               | 98.177  | 6.268     | 6.38       |
| amostra aleatória do Brasil  | 12h               | 77.503  | 4.754     | 6.13       |
| amostra aleatória do Brasil  | 13h               | 67.179  | 4.102     | 6.11       |
| amostra aleatória do Brasil  | 14h               | 63.841  | 4.070     | 6.38       |
| amostra aleatória do Brasil  | 15h               | 58.946  | 3.637     | 6.17       |
| amostra aleatória do Brasil  | 16h               | 39.956  | 2.178     | 5.45       |
| amostra aleatória do Brasil  | 17h               | 177     | 18        | 10.17      |
| amostra aleatória do Brasil  | 18h               | 16      | 2         | 12.5       |
| fechou 19h ou depois         | 08h               | 285.455 | 21.545    | 7.55       |
| fechou 19h ou depois         | 09h               | 265.893 | 19.334    | 7.27       |
| fechou 19h ou depois         | 10h               | 276.063 | 18.411    | 6.67       |
| fechou 19h ou depois         | 11h               | 258.875 | 16.150    | 6.24       |
| fechou 19h ou depois         | 12h               | 217.479 | 12.762    | 5.87       |
| fechou 19h ou depois         | 13h               | 176.824 | 9.641     | 5.45       |
| fechou 19h ou depois         | 14h               | 152.366 | 8.388     | 5.51       |
| fechou 19h ou depois         | 15h               | 133.963 | 7.259     | 5.42       |
| fechou 19h ou depois         | 16h               | 89.849  | 4.535     | 5.05       |
| fechou 19h ou depois         | 17h               | 2.632   | 152       | 5.78       |
| fechou 19h ou depois         | 18h               | 1.849   | 93        | 5.03       |
| fechou 19h ou depois         | 19h               | 11      | 0         | 0.0        |
| vizinha que fechou até 17h15 | 08h               | 67.886  | 5.160     | 7.6        |
| vizinha que fechou até 17h15 | 09h               | 63.806  | 4.617     | 7.24       |
| vizinha que fechou até 17h15 | 10h               | 65.497  | 4.523     | 6.91       |
| vizinha que fechou até 17h15 | 11h               | 61.078  | 4.023     | 6.59       |
| vizinha que fechou até 17h15 | 12h               | 50.543  | 3.114     | 6.16       |
| vizinha que fechou até 17h15 | 13h               | 40.678  | 2.443     | 6.01       |
| vizinha que fechou até 17h15 | 14h               | 35.124  | 2.143     | 6.1        |
| vizinha que fechou até 17h15 | 15h               | 30.407  | 1.767     | 5.81       |
| vizinha que fechou até 17h15 | 16h               | 20.362  | 1.192     | 5.85       |
| vizinha que fechou até 17h15 | 17h               | 172     | 17        | 9.88       |

