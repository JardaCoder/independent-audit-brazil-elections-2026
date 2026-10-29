# 1º turno de 2026 e comparação com o 2º turno

Fonte: BWeb do 1º turno (05/10/2026) e do 2º turno (25/10/2026), conferidos com o SHA-512 do TSE. Cargo: Presidente.

## 1. Resultado do 1º turno (soma dos BUs)

Seções: 499.206 · comparecimento: 125.275.835 · válidos: 119.306.034 · brancos: 2.300.798 · nulos: 3.669.003

|       | votos      | % válidos   |
|:------|:-----------|:------------|
| nº 22 | 56.104.503 | 47.03       |
| nº 13 | 53.879.538 | 45.16       |
| nº 70 | 3.448.569  | 2.89        |
| nº 14 | 2.675.887  | 2.24        |
| nº 55 | 2.605.148  | 2.18        |
| nº 30 | 326.488    | 0.27        |
| nº 80 | 122.911    | 0.1         |
| nº 16 | 43.103     | 0.04        |

## 2. Horário de fechamento e biometria nos dois turnos

| turno    | seções   | fechou até 17:00:59 (local)   | fechou 17:01–17:15 (local)   | fechou 17:16–18:59 (local)   | fechou 19h ou depois (local)   | fechou 19h+ (Brasília)   | liberação manual (biográfica)   | % do comparecimento   |
|:---------|:---------|:------------------------------|:-----------------------------|:-----------------------------|:-------------------------------|:-------------------------|:--------------------------------|:----------------------|
| 1º turno | 499.206  | 71.525                        | 309.816                      | 109.891                      | 7.944                          | 8.324                    | 8.342.249                       | 6.66                  |
| 2º turno | 499.205  | 153.970                       | 336.394                      | 2.472                        | 6.342                          | 6.352                    | 8.632.488                       | 6.73                  |

## 3. As mesmas seções nos dois turnos

- Seções presentes nos dois turnos: 499.205 (1º: 499.206, 2º: 499.205).
- Aptos iguais nos dois turnos: 443.483 (88.8%). A diferença vem do voto em trânsito, que muda entre os turnos.
- Das 6.352 seções que fecharam às 19h ou depois (Brasília) no 2º turno, 102 também fecharam às 19h ou depois no 1º turno.
- Correlação, por seção, entre a taxa de liberação manual no 1º e no 2º turno: **0.82**. Se a taxa se repete, ela é uma característica da seção (eleitorado, leitor biométrico), não algo que apareceu no 2º turno.

## 4. Modelo de transferência de votos: o 2º turno é previsível pelo 1º?

Variável prevista: % de Lula entre Lula e Flávio no 2º turno, por seção. Variáveis explicativas: votos de cada candidato do 1º turno, branco+nulo e abstenção, como fração dos aptos. Seções: 499.205.

- **R² = 0.979**: o 1º turno explica 97.9% da variação do 2º turno entre seções.
- Erro típico (desvio-padrão do resíduo): 2.48 pontos percentuais.

Pesos do modelo. São pesos de previsão, não taxas exatas de transferência: o que importa é o sinal e a ordem. Eleitor de Lula e de Augusto Cury (70) puxa para Lula; eleitor de Flávio puxa contra.

|             | coeficiente   |
|:------------|:--------------|
| nº 22       | -0.157        |
| nº 13       | 1.148         |
| nº 70       | 0.704         |
| nº 14       | 0.501         |
| nº 55       | 0.422         |
| nº 30       | 0.005         |
| outros      | 0.962         |
| branco+nulo | 0.864         |
| abstenção   | 0.56          |

### Resíduo por grupo de seções

Resíduo = % real de Lula no 2º turno menos o previsto pelo 1º turno, em pontos percentuais. Se a virada tivesse sido "fabricada" em algum grupo, o resíduo desse grupo seria claramente positivo. A coluna "dentro do município" compara só seções do mesmo município, o que neutraliza diferenças regionais.

**fechamento 2º turno**

| fechamento 2º turno   | secoes   | residuo_medio   | dentro_do_municipio   |
|:----------------------|:---------|:----------------|:----------------------|
| até 17:00:59          | 129.526  | -0.1            | -0.03                 |
| 17:01–17:15           | 360.751  | 0.03            | 0.01                  |
| 17:16–18:59           | 2.549    | 0.17            | -0.06                 |
| 19h ou depois         | 6.352    | 0.34            | -0.17                 |

**liberação manual 2º turno**

| liberação manual 2º turno   | secoes   | residuo_medio   | dentro_do_municipio   |
|:----------------------------|:---------|:----------------|:----------------------|
| 0–5%                        | 177.011  | 0.15            | 0.12                  |
| 5–10%                       | 237.829  | -0.02           | -0.03                 |
| 10–20%                      | 80.331   | -0.25           | -0.16                 |
| 20–30%                      | 3.686    | -0.67           | -0.3                  |
| 30–100%                     | 348      | -0.32           | -0.18                 |

**variação liberação manual 1º→2º**

| variação liberação manual 1º→2º   | secoes   | residuo_medio   | dentro_do_municipio   |
|:----------------------------------|:---------|:----------------|:----------------------|
| caiu >5 p.p.                      | 7.732    | -0.25           | -0.08                 |
| estável (±5 p.p.)                 | 483.940  | 0.01            | 0.0                   |
| subiu 5–10 p.p.                   | 7.243    | -0.15           | -0.13                 |
| subiu >10 p.p.                    | 290      | -0.05           | -0.04                 |

- Seções com resíduo dentro do município acima de 4 desvios-padrão (8.8 p.p.): 747 (0.15%), sendo 421 a favor de Lula e 326 a favor de Flávio.
- Mesmo atribuindo todo o resíduo dessas seções a manipulação, o efeito líquido na margem seria de 3.487 votos, contra uma margem de 4.430.191.
- A lista dessas seções está em `secoes_fora_do_padrao_1t_2t.csv`.

## 5. Do 1º para o 2º turno, por UF

| SG_UF   | Lula 1º (% válidos)   | Flávio 1º (% válidos)   | Lula 2º (% válidos)   | comparecimento 1º   | comparecimento 2º   | previsto pelo modelo   |
|:--------|:----------------------|:------------------------|:----------------------|:--------------------|:--------------------|:-----------------------|
| AC      | 28.7                  | 64.6                    | 33.4                  | 488.330             | 453.654             | 34.3                   |
| AL      | 54.7                  | 40.4                    | 60.8                  | 1.938.428           | 1.951.632           | 59.7                   |
| AM      | 48.2                  | 45.0                    | 54.0                  | 2.234.549           | 2.192.059           | 53.4                   |
| AP      | 45.7                  | 45.7                    | 52.9                  | 476.562             | 429.975             | 51.8                   |
| BA      | 66.2                  | 28.5                    | 71.3                  | 9.053.601           | 9.422.047           | 71.4                   |
| CE      | 63.3                  | 31.3                    | 68.9                  | 5.910.471           | 6.024.843           | 69.2                   |
| DF      | 38.1                  | 51.3                    | 45.7                  | 1.831.396           | 1.868.280           | 45.1                   |
| ES      | 37.8                  | 54.8                    | 43.6                  | 2.352.282           | 2.409.214           | 44.0                   |
| GO      | 31.1                  | 53.6                    | 40.3                  | 3.971.587           | 4.047.280           | 40.3                   |
| MA      | 64.0                  | 30.9                    | 69.5                  | 4.160.343           | 4.127.771           | 68.7                   |
| MG      | 43.3                  | 48.2                    | 50.4                  | 12.637.274          | 13.044.203          | 50.2                   |
| MS      | 34.7                  | 58.6                    | 40.4                  | 1.541.220           | 1.594.460           | 40.6                   |
| MT      | 29.2                  | 65.1                    | 33.9                  | 2.052.133           | 2.085.334           | 34.3                   |
| PA      | 49.9                  | 44.5                    | 55.0                  | 5.066.504           | 4.989.573           | 55.3                   |
| PB      | 61.3                  | 33.1                    | 67.5                  | 2.683.988           | 2.743.560           | 67.2                   |
| PE      | 63.5                  | 31.0                    | 69.2                  | 5.911.062           | 6.126.467           | 68.9                   |
| PI      | 71.0                  | 24.1                    | 75.9                  | 2.240.883           | 2.239.830           | 76.6                   |
| PR      | 31.2                  | 59.9                    | 37.4                  | 6.841.457           | 7.059.339           | 37.8                   |
| RJ      | 39.4                  | 53.0                    | 46.9                  | 9.859.802           | 10.077.449          | 46.2                   |
| RN      | 59.7                  | 34.8                    | 65.7                  | 2.171.013           | 2.232.823           | 65.2                   |
| RO      | 25.9                  | 67.4                    | 30.4                  | 991.080             | 988.489             | 31.2                   |
| RR      | 22.9                  | 71.1                    | 27.5                  | 332.772             | 308.597             | 26.4                   |
| RS      | 35.7                  | 55.6                    | 42.2                  | 6.702.903           | 6.889.638           | 42.2                   |
| SC      | 25.0                  | 66.7                    | 30.6                  | 4.648.159           | 4.762.303           | 30.5                   |
| SE      | 62.7                  | 30.6                    | 69.5                  | 1.439.082           | 1.466.659           | 69.0                   |
| SP      | 38.2                  | 51.9                    | 46.2                  | 26.431.992          | 27.364.389          | 46.4                   |
| TO      | 43.4                  | 50.4                    | 48.6                  | 965.196             | 954.763             | 48.3                   |
| ZZ      | 47.5                  | 43.5                    | 53.9                  | 341.766             | 381.443             | 56.0                   |

