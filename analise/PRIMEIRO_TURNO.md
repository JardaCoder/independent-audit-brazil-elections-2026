# 1º turno de 2026 e comparação com o 2º turno

Fonte: BWeb de Presidente do 1º turno (04/10/2026) e do 2º turno (25/10/2026), extraídos dos .zip oficiais conferidos com o SHA-512 do TSE (`dados/tse/2026/presidente/`).

## 1. Resultado do 1º turno (soma dos BUs)

Seções com voto: 499.206 · comparecimento: 125.275.835 · válidos: 119.300.788 · brancos: 2.300.798 · nulos na urna: 3.669.003 · nulos técnicos (nº 28, registro anulado): 5.246

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

O TSE conta 499.207 seções em funcionamento. A diferença é a seção 91 de Ciudad Guayana (exterior, 72 aptos), que não aparece no BWeb do 1º turno (ninguém votou).

## 2. Horário de fechamento e liberação manual nos dois turnos

Faixas pelo horário de **Brasília** (exterior fora: cada país tem seu fuso). % Lula = Lula ÷ (Lula + Flávio).

| turno    | faixa (Brasília)   | seções   | % Lula   |
|:---------|:-------------------|:---------|:---------|
| 1º turno | até 17:00:59       | 42.172   | 40.8     |
| 1º turno | 17:01 a 17:15:59   | 331.129  | 45.75    |
| 1º turno | 17:16 a 18:59:59   | 116.228  | 57.48    |
| 1º turno | 19:00 a 19:59:59   | 7.024    | 69.13    |
| 1º turno | 20:00 ou depois    | 1.342    | 76.35    |
| 2º turno | até 17:00:59       | 125.624  | 49.01    |
| 2º turno | 17:01 a 17:15:59   | 363.428  | 52.61    |
| 2º turno | 17:16 a 18:59:59   | 2.493    | 57.14    |
| 2º turno | 19:00 a 19:59:59   | 6.350    | 55.18    |
| 2º turno | 20:00 ou depois    | 2        | 43.04    |

- 1º turno: fecharam no minuto 19:00 exato 237 seções; entre 18:50 e 19:10, 5.219; liberação manual: 8.342.249 (6.66% do comparecimento).
- 2º turno: fecharam no minuto 19:00 exato 1.993 seções; entre 18:50 e 19:10, 6.676; liberação manual: 8.632.488 (6.73% do comparecimento).
- No 1º turno houve **mais** seções fechando às 19h ou depois do que no 2º, mas como uma cauda contínua de filas (5 cargos para votar). O que só existe no 2º turno é o **pico concentrado às 19h00**.

## 3. As mesmas seções nos dois turnos

- Seções comparáveis: 499.205. Aptos iguais nos dois turnos: 88.8% (a diferença vem do voto em trânsito, que muda entre os turnos).
- Seções que fecharam às 19h ou depois nos dois turnos: 98. Se não houvesse relação nenhuma, o esperado ao acaso seria 106. São outros locais.
- Correlação, por seção, entre a taxa de liberação manual do 1º e do 2º turno: **0.82**. A taxa é uma característica estável da seção.

## 4. Modelo: o 2º turno é previsível pelo 1º?

Para cada seção, prevemos a % de Lula (entre Lula e Flávio) no 2º turno usando só o 1º turno da mesma seção: fatia de cada candidato, de branco+nulo e de abstenção. Duas formas: **linear** (frações dos aptos) e **logit** (log da razão Lula/Flávio; frações do comparecimento + taxa de abstenção). "Dentro do município" = compara só seções da mesma cidade (efeito fixo), o que tira a diferença entre regiões.

| modelo                      | variação explicada (R²)   | erro típico (p.p.)   |
|:----------------------------|:--------------------------|:---------------------|
| linear, nacional            | 0.985                     | 2.11                 |
| linear, nacional, ponderado | 0.986                     | 2.11                 |
| linear, dentro da UF        | 0.97                      | 2.07                 |
| linear, dentro do município | 0.932                     | 1.98                 |
| logit, nacional             | 0.986                     | 2.11                 |
| logit, dentro do município  | 0.932                     | 1.99                 |

- Só com a % de Lula entre Lula e Flávio no 1º turno (uma variável) o R² nacional já é 0.984; o modelo usa essa variável mais as fatias de cada candidato, brancos, nulos e abstenção. O número que importa é o **dentro do município**: mostra quanto o 1º turno explica comparando só seções da mesma cidade.

## 5. Algum grupo de seções se desviou da previsão?

Resíduo = % real de Lula − % prevista, em pontos percentuais (p.p.). A tabela mostra a diferença média do resíduo entre o grupo e as demais seções, com o erro-padrão (EP) agrupado por município entre parênteses. Um valor positivo e grande indicaria Lula acima do esperado no grupo.

| grupo                                      | seções   | linear, nacional   | linear, nacional, ponderado   | linear, dentro da UF   | linear, dentro do município   | logit, nacional   | logit, dentro do município   |
|:-------------------------------------------|:---------|:-------------------|:------------------------------|:-----------------------|:------------------------------|:------------------|:-----------------------------|
| fechou às 19h ou depois (Brasília)         | 6.352    | +0.18 (0.18)       | +0.18 (0.17)                  | -0.11 (0.09)           | -0.12 (0.04)                  | +0.11 (0.17)      | -0.08 (0.06)                 |
| fechou até 17:00:59 (relógio local)        | 150.771  | -0.16 (0.03)       | -0.16 (0.03)                  | -0.05 (0.01)           | -0.03 (0.01)                  | -0.12 (0.03)      | -0.03 (0.01)                 |
| liberação manual ≥ 20% da seção (2º turno) | 4.154    | -0.58 (0.05)       | -0.58 (0.05)                  | -0.45 (0.05)           | -0.27 (0.04)                  | -0.42 (0.05)      | -0.19 (0.04)                 |

- Seções tardias: desvio a favor de Lula distinguível de zero em 0 das 6 formas. No pior caso (limite superior de 95% da especificação mais desfavorável, +0.52 p.p.), o efeito sobre a margem seria de no máximo **18.771 votos** (2 × 0.52% × 1.793.914 válidos).
- Efeito no resíduo de +10 p.p. de **nível da liberação manual no 2º turno**: linear, dentro do município: -0.320 p.p. (EP 0.029); logit, dentro do município: -0.281 p.p. (EP 0.026).
- Efeito no resíduo de +10 p.p. de **variação da liberação manual do 1º para o 2º turno**: linear, dentro do município: -0.020 p.p. (EP 0.014); logit, dentro do município: -0.022 p.p. (EP 0.014).
- Se a liberação manual fosse usada para pôr votos em Lula, mais liberação deveria vir com resíduo positivo, sobretudo onde ela **aumentou** do 1º para o 2º turno. Não é o que aparece.

## 6. Comparação simples: o grupo já votava diferente no 1º turno?

| grupo                                      | Lula 1º turno (grupo)   | Lula 2º turno (grupo)   | variação grupo   | Lula 1º (demais, mesmos municípios)   | Lula 2º (demais)   | variação demais   |
|:-------------------------------------------|:------------------------|:------------------------|:-----------------|:--------------------------------------|:-------------------|:------------------|
| fechou às 19h ou depois (Brasília)         | 51.93                   | 55.18                   | 3.25             | 51.4                                  | 54.6               | 3.2               |
| fechou até 17:00:59 (relógio local)        | 44.8                    | 47.61                   | 2.8              | 50.73                                 | 53.51              | 2.77              |
| liberação manual ≥ 20% da seção (2º turno) | 56.73                   | 58.22                   | 1.49             | 50.33                                 | 53.24              | 2.91              |

Lula entre Lula e Flávio (somando os votos do grupo). Se a variação do grupo é igual à das demais seções dos mesmos municípios, o grupo não teve nada de especial no 2º turno: já votava diferente antes.

## 7. Seções muito fora do padrão

| critério                                      | k   | seções   | a favor de Lula   | a favor de Flávio   | efeito bruto a favor de Lula (votos)   | efeito líquido (votos)   |
|:----------------------------------------------|:----|:---------|:------------------|:--------------------|:---------------------------------------|:-------------------------|
| resíduo > k desvios                           | 2   | 22.983   | 12.330            | 10.653              | 265.876                                | 52.685                   |
| resíduo padronizado pelo tamanho da seção > k | 2   | 1.893    | 1.105             | 788                 | 33.327                                 | 13.030                   |
| resíduo > k desvios                           | 3   | 2.962    | 1.710             | 1.252               | 42.692                                 | 15.655                   |
| resíduo padronizado pelo tamanho da seção > k | 3   | 149      | 74                | 75                  | 2.573                                  | 500                      |
| resíduo > k desvios                           | 4   | 573      | 341               | 232                 | 8.044                                  | 3.233                    |
| resíduo padronizado pelo tamanho da seção > k | 4   | 43       | 16                | 27                  | 747                                    | -121                     |
| resíduo > k desvios                           | 5   | 185      | 108               | 77                  | 2.482                                  | 862                      |
| resíduo padronizado pelo tamanho da seção > k | 5   | 19       | 5                 | 14                  | 392                                    | -105                     |

Efeito = quanto a margem mudaria se todo o desvio dessas seções fosse removido (2 × resíduo × válidos). "Bruto" soma só os desvios a favor de Lula, sem descontar os a favor de Flávio.
- Lista (critério 4 desvios): `secoes_fora_do_padrao_1t_2t.csv`.
- No modelo linear nacional, há um aglomerado de seções com Lula muito abaixo do previsto: 8 são do exterior (principalmente Accra, Boston, Caracas, Kuala Lumpur), com abstenção média de 65% no 1º turno. O modelo linear trata parte da abstenção como voto futuro, o que não vale no exterior. É limitação do modelo, e o desvio é contra Lula.

## 8. O que este teste não detecta

- Manipulação **igual em todas as seções** do país (seria absorvida pelos coeficientes do modelo). Coberta por outro teste: a soma dos BUs bate com o resultado oficial e os BUs batem com os logs das urnas.
- Manipulação que também tenha ocorrido no **1º turno** (fica embutida na previsão).
- Manipulação do **município inteiro** (a coluna "dentro do município" não a vê; a nacional sim).
- Os coeficientes do modelo não são taxas de transferência de votos e não devem ser interpretados um a um.

## 9. Do 1º para o 2º turno, por UF

| SG_UF   | Lula 1º (% válidos)   | Flávio 1º (% válidos)   | Lula 2º (% válidos)   | comparecimento 1º   | comparecimento 2º   | previsto pelo modelo   |
|:--------|:----------------------|:------------------------|:----------------------|:--------------------|:--------------------|:-----------------------|
| AC      | 28.7                  | 64.6                    | 33.4                  | 488.330             | 453.654             | 34.3                   |
| AL      | 54.7                  | 40.4                    | 60.8                  | 1.938.428           | 1.951.632           | 60.1                   |
| AM      | 48.2                  | 45.0                    | 54.0                  | 2.234.549           | 2.192.059           | 53.6                   |
| AP      | 45.7                  | 45.7                    | 52.9                  | 476.562             | 429.975             | 52.1                   |
| BA      | 66.2                  | 28.5                    | 71.3                  | 9.053.601           | 9.422.047           | 71.7                   |
| CE      | 63.3                  | 31.3                    | 68.9                  | 5.910.471           | 6.024.843           | 68.8                   |
| DF      | 38.1                  | 51.3                    | 45.7                  | 1.831.396           | 1.868.280           | 45.4                   |
| ES      | 37.8                  | 54.8                    | 43.6                  | 2.352.282           | 2.409.214           | 44.1                   |
| GO      | 31.1                  | 53.6                    | 40.3                  | 3.971.587           | 4.047.280           | 40.1                   |
| MA      | 64.0                  | 30.9                    | 69.5                  | 4.160.343           | 4.127.771           | 68.8                   |
| MG      | 43.3                  | 48.2                    | 50.4                  | 12.637.274          | 13.044.203          | 50.3                   |
| MS      | 34.7                  | 58.6                    | 40.4                  | 1.541.220           | 1.594.460           | 40.5                   |
| MT      | 29.2                  | 65.1                    | 33.9                  | 2.052.133           | 2.085.334           | 34.3                   |
| PA      | 49.9                  | 44.5                    | 55.0                  | 5.066.504           | 4.989.573           | 55.2                   |
| PB      | 61.3                  | 33.1                    | 67.5                  | 2.683.988           | 2.743.560           | 67.3                   |
| PE      | 63.5                  | 31.0                    | 69.2                  | 5.911.062           | 6.126.467           | 69.1                   |
| PI      | 71.0                  | 24.1                    | 75.9                  | 2.240.883           | 2.239.830           | 76.0                   |
| PR      | 31.2                  | 59.9                    | 37.4                  | 6.841.457           | 7.059.339           | 37.8                   |
| RJ      | 39.4                  | 53.0                    | 46.9                  | 9.859.802           | 10.077.449          | 46.1                   |
| RN      | 59.8                  | 34.8                    | 65.7                  | 2.171.013           | 2.232.823           | 65.2                   |
| RO      | 25.9                  | 67.5                    | 30.4                  | 991.080             | 988.489             | 31.2                   |
| RR      | 22.9                  | 71.1                    | 27.5                  | 332.772             | 308.597             | 27.5                   |
| RS      | 35.7                  | 55.6                    | 42.2                  | 6.702.903           | 6.889.638           | 42.5                   |
| SC      | 25.0                  | 66.7                    | 30.6                  | 4.648.159           | 4.762.303           | 30.9                   |
| SE      | 62.7                  | 30.6                    | 69.5                  | 1.439.082           | 1.466.659           | 69.1                   |
| SP      | 38.2                  | 51.9                    | 46.2                  | 26.431.992          | 27.364.389          | 46.2                   |
| TO      | 43.4                  | 50.4                    | 48.6                  | 965.196             | 954.763             | 48.7                   |
| ZZ      | 47.6                  | 43.5                    | 53.9                  | 341.766             | 381.443             | 55.7                   |

