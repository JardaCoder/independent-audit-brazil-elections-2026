# Horário de fechamento, seções das 19h, liberação manual, seções unânimes e Benford — 2º turno 2026

Fonte: BWeb de Presidente do 2º turno (`dados/tse/2026/presidente/2turno/`), extraídos dos .zip oficiais conferidos com o SHA-512 do TSE.

## 0. Totais (conferem com o resultado oficial)

- Seções com voto: 499.205 · comparecimento: 128.236.074
- Lula: 64.256.232 (51.79% dos válidos) · Flávio: 59.826.041 · margem: **4.430.191**
- Liberados manualmente (digital falhou; campo QT_ELEI_BIOM_SEM_HABILITACAO): 8.632.488 (6.73% do comparecimento)

## 1. Os números que circularam, recalculados com o horário local da urna

Com o horário como gravado pela urna (local) e estas faixas, os números que circularam se reproduzem:

### 2026 (Lula × Flávio Bolsonaro)

| faixa            | secoes   | comparecimento   | lula       | adversario   | % Lula   | saldo Lula   |
|:-----------------|:---------|:-----------------|:-----------|:-------------|:---------|:-------------|
| até 17:00:59     | 150.771  | 37.630.420       | 17.369.159 | 19.116.798   | 47.61    | -1.747.639   |
| 17:01 a 17:15:59 | 339.593  | 88.071.750       | 45.525.188 | 39.627.772   | 53.46    | 5.897.416    |
| 17:16 a 18:59:59 | 2.472    | 674.799          | 372.470    | 279.102      | 57.16    | 93.368       |
| 19:00 a 19:59:59 | 6.333    | 1.856.306        | 987.956    | 801.108      | 55.22    | 186.848      |
| 20:00 ou depois  | 9        | 1.968            | 1.014      | 908          | 52.76    | 106          |

### 2022 (Lula × Jair Bolsonaro)

| faixa            | secoes   | comparecimento   | lula       | adversario   | % Lula   | saldo Lula   |
|:-----------------|:---------|:-----------------|:-----------|:-------------|:---------|:-------------|
| até 17:00:59     | 195.818  | 49.926.557       | 23.374.900 | 24.414.955   | 48.91    | -1.040.055   |
| 17:01 a 17:15:59 | 274.561  | 73.883.315       | 36.731.439 | 33.607.908   | 52.22    | 3.123.531    |
| 17:16 a 18:59:59 | 1.585    | 434.753          | 235.306    | 179.999      | 56.66    | 55.307       |
| 19:00 a 19:59:59 | 15       | 2.908            | 1.762      | 1.003        | 63.73    | 759          |
| 20:00 ou depois  | 5        | 1.023            | 597        | 407          | 59.46    | 190          |

- A afirmação de que "mais de 2 milhões de eleitores" votaram nas seções fechadas depois das 19h: nessas 6.333 seções havia 2.302.067 eleitores **aptos**, mas votaram 1.856.306. O número só bate contando os aptos.

## 2. O grupo "até 17:00:59": por que Flávio vence nele?

- Diferença bruta: 47.61% de Lula no grupo contra 53.53% no resto (**-5.92 p.p.**).
- Os estados com fuso a oeste (AC, AM, MT, MS, RO, RR), cujas urnas marcam 15h/16h quando são 17h em Brasília, são 21% das seções do grupo e respondem por 83% da vantagem de Flávio nele. Sem eles, o grupo ainda dá 50.5% a Flávio.

| comparação                           | diferença de % Lula (grupo − resto)   |
|:-------------------------------------|:--------------------------------------|
| sem controle                         | -5.91 p.p. (EP 0.56)                  |
| comparando dentro do mesmo estado    | -1.37 p.p. (EP 0.44)                  |
| comparando dentro do mesmo município | -0.20 p.p. (EP 0.06)                  |

- **As mesmas seções já votavam assim no 1º turno**: lá, o grupo deu 44.80% a Lula contra 50.76% no resto (-5.95 p.p.), praticamente a mesma diferença do 2º turno.
- Tamanho: mediana de 317 aptos no grupo contra 331 no resto. O tamanho da seção quase não explica a diferença; a geografia explica.
- Conclusão: o grupo concentra regiões onde Flávio é mais forte (os estados a oeste por causa do fuso, e o interior, onde há menos fila). Dentro do mesmo município a diferença praticamente some, e ela já existia no 1º turno.

## 3. Horário convertido para Brasília

| faixa            | secoes   | comparecimento   | lula       | adversario   | % Lula   | saldo Lula   |
|:-----------------|:---------|:-----------------|:-----------|:-------------|:---------|:-------------|
| até 17:00:59     | 125.624  | 31.599.960       | 15.001.166 | 15.608.268   | 49.01    | -607.102     |
| 17:01 a 17:15:59 | 363.428  | 93.718.230       | 47.692.656 | 42.962.768   | 52.61    | 4.729.888    |
| 17:16 a 18:59:59 | 2.493    | 675.182          | 372.437    | 279.413      | 57.14    | 93.024       |
| 19:00 a 19:59:59 | 6.350    | 1.860.942        | 989.686    | 803.919      | 55.18    | 185.767      |
| 20:00 ou depois  | 2        | 317              | 133        | 176          | 43.04    | -43          |

- Só com as seções que fecharam até 17h15 (Brasília), Lula vence por **4.122.786** votos.

## 4. As seções que fecharam às 19h ou depois (Brasília)

- São **6.352** seções: 1.993 fecharam no minuto 19:00 exato e 6.319 entre 19:00 e 19:15. O formato é o de um horário-limite marcado às 19h (como o fechamento normal das 17h, deslocado 2 horas), não o de uma fila que se estende.
- Votaram nelas 1.861.259 eleitores (80.6% dos aptos; no país, 80.8%). Saldo de Lula nelas: 185.724 (4.2% da margem). Anulando **todas** essas seções, Lula ainda venceria por 4.244.467.
- Onde estão: Rio De Janeiro (RJ) 1.978, São Paulo (SP) 1.481, Salvador (BA) 730, Petrópolis (RJ) 285, João Pessoa (PB) 265, Itaboraí (RJ) 237. Os 5 primeiros municípios somam 75% do grupo.
- Elas estão em 1.131 locais de votação; em 313 deles **todas** as seções fecharam às 19h. O agrupamento é por local de votação (escola), compatível com uma decisão tomada por local.
- Comparando com as seções **do mesmo local de votação** que fecharam às 17h (10.002 seções em 818 locais mistos): diferença de % Lula -0.06 p.p. (EP 0.10); diferença de comparecimento +0.03 p.p. (EP 0.11). Nenhum sinal de votos a mais nem de voto diferente.

| SG_UF   | secoes   | lula    | flavio   | % Lula nas seções tardias   | % Lula no estado todo   |
|:--------|:---------|:--------|:---------|:----------------------------|:------------------------|
| RJ      | 2.805    | 370.026 | 437.760  | 45.81                       | 46.9                    |
| SP      | 1.571    | 233.402 | 172.816  | 57.46                       | 46.15                   |
| BA      | 936      | 201.695 | 77.225   | 72.31                       | 71.31                   |
| PE      | 657      | 125.972 | 65.779   | 65.7                        | 69.2                    |
| PB      | 275      | 42.964  | 38.777   | 52.56                       | 67.46                   |
| SE      | 51       | 8.775   | 4.657    | 65.33                       | 69.53                   |
| DF      | 17       | 1.718   | 1.994    | 46.28                       | 45.72                   |
| MT      | 9        | 804     | 1.919    | 29.53                       | 33.94                   |
| PA      | 8        | 1.218   | 995      | 55.04                       | 55.02                   |
| PI      | 7        | 1.136   | 406      | 73.67                       | 75.88                   |
| RN      | 3        | 527     | 346      | 60.37                       | 65.72                   |
| MA      | 3        | 519     | 104      | 83.31                       | 69.54                   |
| AL      | 2        | 362     | 154      | 70.16                       | 60.77                   |
| RS      | 2        | 239     | 251      | 48.78                       | 42.16                   |
| ES      | 2        | 167     | 338      | 33.07                       | 43.63                   |
| AC      | 1        | 45      | 160      | 21.95                       | 33.43                   |
| GO      | 1        | 79      | 216      | 26.78                       | 40.34                   |
| MG      | 1        | 78      | 18       | 81.25                       | 50.43                   |
| PR      | 1        | 93      | 180      | 34.07                       | 37.42                   |

- **Votos dados depois das 17h, segundo o log de cada urna**: ver `LOGS_TARDIAS.md` (todas as seções tardias foram lidas).

## 5. Eleitores liberados manualmente ("sem biometria")

| % liberados na seção   | secoes   | lula       | flavio     | liberados   | % Lula   | % das seções no Nordeste   |
|:-----------------------|:---------|:-----------|:-----------|:------------|:---------|:---------------------------|
| 0-2%                   | 17.810   | 2.268.122  | 2.092.682  | 65.416      | 52.01    | 24.6                       |
| 2-5%                   | 157.893  | 20.729.348 | 19.877.339 | 1.565.408   | 51.05    | 25.6                       |
| 5-10%                  | 237.829  | 30.521.272 | 28.758.874 | 4.336.218   | 51.49    | 28.0                       |
| 10-20%                 | 80.331   | 10.061.133 | 8.584.117  | 2.454.737   | 53.96    | 34.5                       |
| 20-30%                 | 3.686    | 433.883    | 313.052    | 174.933     | 58.09    | 42.0                       |
| 30-50%                 | 251      | 28.656     | 19.818     | 17.324      | 59.12    | 43.4                       |
| 50-100%                | 97       | 13.664     | 8.662      | 18.452      | 61.2     | 52.6                       |

A % de Lula sobe nas faixas de liberação alta, mas essas faixas têm poucas seções e mais Nordeste. Para separar isso, medimos a **inclinação** (quanto a % de Lula muda quando a liberação muda), comparando seções parecidas, e daí estimamos como os liberados votaram.

| comparação          | inclinação (EP)   | % Lula entre liberados (estimativa)   | margem sem os liberados (estimativa)   | % Lula entre liberados (limite de 95%)   | margem sem os liberados (limite de 95%)   |
|:--------------------|:------------------|:--------------------------------------|:---------------------------------------|:-----------------------------------------|:------------------------------------------|
| nacional            | 0.289 (0.080)     | 78.7                                  | -373.626                               | 93.3                                     | -2.802.136                                |
| dentro do estado    | 0.171 (0.055)     | 67.7                                  | 1.470.770                              | 77.8                                     | -223.374                                  |
| dentro do município | 0.024 (0.039)     | 54.0                                  | 3.755.951                              | 61.2                                     | 2.552.818                                 |

- **Pior caso aritmético** (todo liberado votou em Lula sempre que possível e é retirado): margem de -4.189.464. Esse cenário exige que, em cada seção, os liberados tenham votado em Lula em bloco, o que contradiz os testes abaixo.
- Por que as linhas dão resultados tão diferentes: liberação manual e voto em Lula são ambos mais altos em certas regiões (Nordeste, interior). Comparar o país todo (ou o estado todo) mistura essas regiões e atribui à liberação um efeito que é da geografia: é a *falácia ecológica*. A comparação mais justa é entre seções da **mesma cidade**: aí a inclinação cai a quase zero, e mesmo no limite de 95% Lula mantém pelo menos 2,5 milhões de margem.
- Mesmo assim, estimativas com dados agregados nunca são definitivas. Por isso o teste mais forte é o do 1º turno (abaixo), que compara cada seção com ela mesma.
- **Testes contra o 1º turno** (em `PRIMEIRO_TURNO.md`, seção 5): dado o voto da própria seção no 1º turno, mais liberação vem com **menos** Lula do que o esperado, e o **aumento** da liberação do 1º para o 2º turno não tem relação com o resultado. Se liberações fossem usadas para pôr votos em Lula, apareceria o contrário.
- A taxa de liberação é parecida no Nordeste (7.19%) e no resto do país (6.58%), e quase igual no 1º turno (6.66%).
- O que o campo significa, pelos logs das urnas (`LOGS.md`): o eleitor tem biometria cadastrada, a digital falhou 4 vezes, a urna pediu um dado pessoal (e recusou quando não conferia) e exigiu a digital do mesário. É a linha "Habilitação biográfica" do BU impresso.

## 6. Seções quase unânimes

| eleição       | 100% Lula   | 100% adversário   | >90% Lula   | >90% adversário   |
|:--------------|:------------|:------------------|:------------|:------------------|
| 2º turno 2026 | 106         | 4                 | 6.816       | 378               |
| 1º turno 2026 | 81          | 8                 | 6.005       | 713               |
| 2º turno 2022 | 143         | 4                 | 9.433       | 213               |

- Das 6.816 seções com mais de 90% para Lula, 75% estão em MA, BA, PI, PE, CE. Lula teve 69.4% no Nordeste. Com média regional perto de 70%, a cauda acima de 90% fica de um lado só: o voto no Brasil é regional e a distribuição nacional não precisa ser simétrica.

## 7. Lei de Benford

**1º dígito**

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

- Os dois candidatos desviam do mesmo jeito. Seções têm tamanho limitado (mediana de 327 aptos), e o voto de Lula numa seção fica entre 100 e 199 em 61% delas, então o dígito 1 domina. A literatura (Deckert, Myagkov & Ordeshook, 2011) considera o 1º dígito inadequado para votos por seção.

**2º dígito** (Benford esperado: média 4,187)

| série                                                                        | média do 2º dígito   | qui-quadrado vs Benford   |
|:-----------------------------------------------------------------------------|:---------------------|:--------------------------|
| Lula (real)                                                                  | 3.858                | 6.731                     |
| Flávio (real)                                                                | 3.971                | 6.461                     |
| Lula (simulação honesta: sorteio binomial com o tamanho e a % de cada seção) | 3.865                | 6.490                     |

- O 2º dígito real "falha" em Benford, mas **a simulação de uma eleição honesta falha do mesmo jeito**: o que se observa é o esperado para contagens desse tamanho, não sinal de manipulação.

**Último dígito** (teste de Beber & Scacco: em contagens honestas, cada dígito final aparece ~10% das vezes)

| candidato   | qui-quadrado (9 g.l.; crítico 5% = 16,9)   | maior desvio de 10% (p.p.)   |
|:------------|:-------------------------------------------|:-----------------------------|
| Lula        | 5.0                                        | 0.08                         |
| Flávio      | 12.4                                       | 0.11                         |

