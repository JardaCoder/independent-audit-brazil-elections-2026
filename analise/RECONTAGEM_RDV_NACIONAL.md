# Recontagem nacional voto a voto pelo RDV — 2º turno 2026

Cada RDV foi baixado do pacote oficial do TSE ("arquivos transmitidos para totalização") por download parcial e os votos de Presidente foram contados um a um. Ver `recontagem_rdv.py` para o leitor.

- Seções na BWeb: 499.205. RDVs lidos sem erro: 499.178; com erro de leitura: 29 (27 seções em cédula e 2 arquivos sem seção com votos na BWeb). **RDV idêntico à BWeb (Lula, Flávio, brancos e nulos): 499.178**.
- **Seções com urna eletrônica: 499.178 de 499.178 idênticas.** As 27 que não batem são todas seções do exterior apuradas em **cédula** (Sistema de Apuração): o leitor não consegue interpretar o arquivo delas (erro de leitura). Os votos dessas seções somam 831, exatamente a diferença entre os totais abaixo.
- Seções da BWeb sem arquivo RDV no pacote: 0.

## Totais

|                |    votos |
|:---------------|---------:|
| Lula (RDV)     | 64255787 |
| Lula (BWeb)    | 64256232 |
| Flávio (RDV)   | 59825688 |
| Flávio (BWeb)  | 59826041 |
| brancos (RDV)  |  1430484 |
| brancos (BWeb) |  1430496 |
| nulos (RDV)    |  2723284 |
| nulos (BWeb)   |  2723305 |

## Por UF

| SG_UF   |   secoes_bweb |   rdv_lidos |   erros |   RDV = BWeb |
|:--------|--------------:|------------:|--------:|-------------:|
| AC      |          2270 |        2270 |       0 |         2270 |
| AL      |          7101 |        7101 |       0 |         7101 |
| AM      |          8157 |        8157 |       0 |         8157 |
| AP      |          1914 |        1914 |       0 |         1914 |
| BA      |         35476 |       35476 |       0 |        35476 |
| CE      |         23765 |       23765 |       0 |        23765 |
| DF      |          6969 |        6969 |       0 |         6969 |
| ES      |          9844 |        9844 |       0 |         9844 |
| GO      |         15686 |       15686 |       0 |        15686 |
| MA      |         18093 |       18093 |       0 |        18093 |
| MG      |         52062 |       52062 |       0 |        52062 |
| MS      |          7106 |        7106 |       0 |         7106 |
| MT      |          8287 |        8287 |       0 |         8287 |
| PA      |         20827 |       20827 |       0 |        20827 |
| PB      |         10712 |       10712 |       0 |        10712 |
| PE      |         21418 |       21418 |       0 |        21418 |
| PI      |         10225 |       10225 |       0 |        10225 |
| PR      |         27142 |       27142 |       0 |        27142 |
| RJ      |         37675 |       37675 |       0 |        37675 |
| RN      |          8115 |        8115 |       0 |         8115 |
| RO      |          4698 |        4698 |       0 |         4698 |
| RR      |          1519 |        1519 |       0 |         1519 |
| RS      |         27547 |       27547 |       0 |        27547 |
| SC      |         17326 |       17326 |       0 |        17326 |
| SE      |          5923 |        5923 |       0 |         5923 |
| SP      |        103656 |      103656 |       0 |       103656 |
| TO      |          4384 |        4384 |       0 |         4384 |
| ZZ      |          1308 |        1281 |      29 |         1281 |

## Seções com diferença

|   CD_MUNICIPIO |   NR_ZONA |   NR_SECAO |   bweb_13 |   bweb_22 |   bweb_branco |   bweb_nulo |   bweb_comparecimento | SG_UF   |   rdv_13 |   rdv_22 |   rdv_branco |   rdv_nulo |   rdv_total | erro                                  | _merge   |
|---------------:|----------:|-----------:|----------:|----------:|--------------:|------------:|----------------------:|:--------|---------:|---------:|-------------:|-----------:|------------:|:--------------------------------------|:---------|
|          29173 |         1 |        494 |         1 |        12 |             0 |           0 |                    13 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29254 |         1 |          1 |        31 |        22 |             0 |           0 |                    53 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29270 |         1 |          3 |         8 |         5 |             1 |           0 |                    14 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29297 |         1 |        495 |        29 |         8 |             0 |           2 |                    39 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29300 |         1 |          6 |        23 |         3 |             3 |           0 |                    29 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29394 |         1 |         28 |        19 |        22 |             0 |           0 |                    41 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29580 |         1 |         96 |         3 |        28 |             0 |           0 |                    31 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29645 |         1 |        380 |        18 |        33 |             1 |           0 |                    52 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29750 |         1 |       1703 |        15 |        17 |             0 |           2 |                    34 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29777 |         1 |        127 |        43 |         1 |             1 |           0 |                    45 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29858 |         1 |       1183 |         3 |        16 |             0 |           2 |                    21 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          29912 |         1 |        150 |        32 |         5 |             0 |           0 |                    37 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          30163 |         1 |        647 |        60 |        33 |             0 |           4 |                    97 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          30171 |         1 |       1340 |         8 |         1 |             0 |           1 |                    10 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          30295 |         1 |        348 |         4 |         3 |             0 |           0 |                     7 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          30325 |         1 |        352 |         9 |        12 |             3 |           0 |                    24 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          30333 |         1 |        353 |         6 |         2 |             0 |           0 |                     8 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          30430 |         1 |        384 |         8 |        12 |             2 |           1 |                    23 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          30546 |         1 |       1764 |        40 |        13 |             0 |           2 |                    55 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          30597 |         1 |       1182 |        16 |        11 |             0 |           1 |                    28 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          30708 |         1 |        444 |        16 |         7 |             0 |           0 |                    23 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          30821 |         1 |       1524 |         8 |         4 |             0 |           0 |                    12 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          38962 |         1 |        558 |        11 |         6 |             0 |           0 |                    17 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          39102 |         1 |        712 |        10 |        22 |             1 |           1 |                    34 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          99155 |         1 |       1504 |         7 |        13 |             0 |           0 |                    20 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          99180 |         1 |       1228 |         6 |        14 |             0 |           2 |                    22 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |
|          99473 |         1 |       1327 |        11 |        28 |             0 |           3 |                    42 | ZZ      |        0 |        0 |            0 |          0 |           0 | IndexError('list index out of range') | both     |

