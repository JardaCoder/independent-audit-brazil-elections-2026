# Consistência interna dos BUs — 2º turno 2026

499.205 seções (Presidente) e 538.946 pares seção×cargo verificados.

| Regra | Violações |
|---|---|
| recebido antes de emitido: maior diferença (s) | 52 |
| aptos = comparecimento + abstenções | 0 |
| comparecimento <= aptos | 0 |
| soma dos votos (nominais+brancos+nulos) = comparecimento | 0 |
| sem biometria <= comparecimento | 0 |
| valores únicos de aptos/comparecimento por BU | 0 |
| seções sem horário de abertura/encerramento (apuradas em cédula) | 29 |
| abertura < encerramento ≤ emissão do BU (seções com horário) | 0 |
| abertura no dia da eleição (seções com horário) | 0 |
| BU recebido pelo TSE depois de emitido pela urna (Brasil, em horário de Brasília, sem folga) | 8 |
| carga da urna antes do dia da eleição | 5 |
| comparecimento diferente entre Presidente e Governador (UFs com 2º turno estadual) | 1818 de 39739 |
| …comparecimento de Presidente **menor** que o de Governador | 0 |
| mesmo nº de urna em mais de uma seção | 2 (são as urnas do Sistema de Apuração do exterior, usadas para digitar cédulas) |

Horários vêm do relógio local da urna (ver RESULTADOS.md).

## Carga das urnas (DT_CARGA_URNA_EFETIVADA)

De 2026-09-15 15:57:00 a 2026-10-25 10:04:00.

## Abertura (relógio local)

|   abertura |   seções |
|-----------:|---------:|
|         06 |     2826 |
|         07 |    29207 |
|         08 |   467053 |
|         09 |       76 |
|         10 |       13 |
|         11 |        2 |
|         13 |        1 |

## Exemplos de violações

| SG_UF   |   CD_MUNICIPIO |   NR_ZONA |   NR_SECAO | NM_MUNICIPIO        |   CD_CARGO_PERGUNTA |   aptos |   comp |   abst |   votos |   bio |   n_aptos |   n_comp | abertura            | encerramento        | emissao             | recebido            | carga               |    urna |   n_urna | regra                                                                                        |
|:--------|---------------:|----------:|-----------:|:--------------------|--------------------:|--------:|-------:|-------:|--------:|------:|----------:|---------:|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|--------:|---------:|:---------------------------------------------------------------------------------------------|
| MS      |          90514 |         8 |        486 | CAMPO GRANDE        |                   1 |     339 |    280 |     59 |     280 |    11 |         1 |        1 | 2026-10-25 07:26:47 | 2026-10-25 16:01:19 | 2026-10-25 16:03:13 | 2026-10-25 20:04:10 | 2026-10-25 06:55:00 | 2338906 |        1 | carga da urna antes do dia da eleição                                                        |
| MS      |          91650 |        51 |         44 | TRÊS LAGOAS         |                   1 |     261 |    218 |     43 |     218 |    10 |         1 |        1 | 2026-10-25 08:13:13 | 2026-10-25 16:00:29 | 2026-10-25 16:01:48 | 2026-10-25 20:07:10 | 2026-10-25 07:36:00 | 2001864 |        1 | carga da urna antes do dia da eleição                                                        |
| PA      |           4057 |        16 |         19 | AFUÁ                |                   1 |     300 |    239 |     61 |     239 |     1 |         1 |        1 | 2026-10-25 08:00:01 | 2026-10-25 17:06:10 | 2026-10-25 17:06:23 | 2026-10-25 17:05:41 | 2026-09-22 09:32:00 | 2408714 |        1 | BU recebido pelo TSE depois de emitido pela urna (Brasil, em horário de Brasília, sem folga) |
| PA      |           4057 |        16 |         23 | AFUÁ                |                   1 |     300 |    240 |     60 |     240 |    13 |         1 |        1 | 2026-10-25 08:00:01 | 2026-10-25 17:04:19 | 2026-10-25 17:06:05 | 2026-10-25 17:05:13 | 2026-09-22 09:58:00 | 2415163 |        1 | BU recebido pelo TSE depois de emitido pela urna (Brasil, em horário de Brasília, sem folga) |
| PA      |           4057 |        16 |         77 | AFUÁ                |                   1 |     360 |    305 |     55 |     305 |     4 |         1 |        1 | 2026-10-25 08:05:05 | 2026-10-25 17:04:05 | 2026-10-25 17:07:09 | 2026-10-25 17:06:20 | 2026-09-22 11:38:00 | 2393841 |        1 | BU recebido pelo TSE depois de emitido pela urna (Brasil, em horário de Brasília, sem folga) |
| PR      |          78778 |        52 |         54 | SÃO JOÃO DO TRIUNFO |                   1 |     220 |    205 |     15 |     205 |    11 |         1 |        1 | 2026-10-25 08:00:01 | 2026-10-25 17:03:32 | 2026-10-25 17:05:27 | 2026-10-25 17:05:16 | 2026-09-26 09:41:00 | 2021052 |        1 | BU recebido pelo TSE depois de emitido pela urna (Brasil, em horário de Brasília, sem folga) |
| PR      |          74918 |        56 |         37 | CARLÓPOLIS          |                   1 |     324 |    278 |     46 |     278 |    38 |         1 |        1 | 2026-10-25 10:02:54 | 2026-10-25 17:01:04 | 2026-10-25 17:02:29 | 2026-10-25 19:57:22 | 2026-10-25 09:20:00 | 1797363 |        1 | carga da urna antes do dia da eleição                                                        |
| PR      |          75833 |        43 |        397 | GUARAPUAVA          |                   1 |      65 |     38 |     27 |      38 |     2 |         1 |        1 | 2026-10-25 10:51:03 | 2026-10-25 17:00:47 | 2026-10-25 17:02:05 | 2026-10-25 20:45:27 | 2026-10-25 10:04:00 | 2462584 |        1 | carga da urna antes do dia da eleição                                                        |
| SP      |          61816 |        16 |        436 | ATIBAIA             |                   1 |     373 |    297 |     76 |     297 |     4 |         1 |        1 | 2026-10-25 08:32:01 | 2026-10-25 17:00:35 | 2026-10-25 17:00:58 | 2026-10-25 20:17:39 | 2026-10-25 07:58:00 | 2295578 |        1 | carga da urna antes do dia da eleição                                                        |
| ZZ      |          29173 |         1 |        494 | KATMANDU            |                   1 |      32 |     13 |     19 |      13 |     0 |         1 |        1 | NaT                 | NaT                 | 2026-10-25 17:35:23 | 2026-10-25 20:14:50 | 2026-09-18 15:17:00 | 1808076 |        1 | seções sem horário de abertura/encerramento (apuradas em cédula)                             |
| ZZ      |          29254 |         1 |          1 | ABIDJÃ              |                   1 |      91 |     53 |     38 |      53 |     0 |         1 |        1 | NaT                 | NaT                 | 2026-10-25 17:32:31 | 2026-10-25 20:15:20 | 2026-09-18 14:16:00 | 1762246 |        1 | seções sem horário de abertura/encerramento (apuradas em cédula)                             |
| ZZ      |          29270 |         1 |          3 | ACCRA               |                   1 |      43 |     14 |     29 |      14 |     0 |         1 |        1 | NaT                 | NaT                 | 2026-10-25 18:08:08 | 2026-10-25 21:21:06 | 2026-09-18 15:17:00 | 1808076 |        1 | seções sem horário de abertura/encerramento (apuradas em cédula)                             |

