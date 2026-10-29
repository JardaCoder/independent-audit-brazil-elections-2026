# Relatório de Auditoria Independente — Eleição Presidencial de 2026

**Objeto:** resultado da eleição para Presidente da República, 1º turno (04/10/2026) e 2º turno (25/10/2026).
**Objetivo:** verificar a integridade e a coerência dos dados públicos oficiais e testar as suspeitas de fraude
que circularam depois do 2º turno.
**Natureza:** auditoria de dados, independente, feita somente com dados públicos do Tribunal Superior Eleitoral
(TSE). Sem vínculo com o TSE, partidos ou candidatos.
**Data de referência:** dados obtidos em 29/10/2026.
**Reprodutibilidade:** todos os dados, scripts e resultados estão neste repositório. Cada número citado pode ser
recalculado (ver [Anexo B](#anexo-b--como-reproduzir)).

---

## Sumário

1. [Escopo](#1-escopo)
2. [Metodologia](#2-metodologia)
   - 2.1 Princípios
   - 2.2 Fontes de dados
   - 2.3 Preparação e controle de integridade
   - 2.4 Procedimentos de auditoria
   - 2.5 Critérios de avaliação
   - 2.6 Ferramentas
3. [Resultados por procedimento](#3-resultados-por-procedimento)
4. [Achados](#4-achados)
5. [Limitações](#5-limitações)
6. [Conclusão da auditoria](#6-conclusão-da-auditoria)
7. [Recomendações](#7-recomendações)
- [Anexo A — Suspeitas testadas e parecer](#anexo-a--suspeitas-testadas-e-parecer)
- [Anexo B — Como reproduzir](#anexo-b--como-reproduzir)

---

## 1. Escopo

**Incluído:**
- Cargo de Presidente, 1º e 2º turnos de 2026, em todas as 27 UFs e no exterior.
- Integridade dos arquivos publicados, coerência interna de cada boletim de urna (BU), correspondência entre
  os BUs e o resultado oficial, entre os BUs e os arquivos originais gravados pelas urnas, e entre as urnas
  usadas e as previstas antes da eleição.
- Teste de cada suspeita quantitativa que circulou depois do 2º turno.
- Testes estatísticos de padrões anômalos, usando o 1º turno de 2026 e o 2º turno de 2022 como controles.

**Excluído:**
- Demais cargos (governador, senador, deputados), exceto quando usados em checagens de coerência.
- Código-fonte e segurança do software da urna, cerimônias de lacração e testes públicos de segurança.
- Atos administrativos e judiciais (decisões de prorrogação, processos, investigações), que não constam dos
  dados de votação.
- Verificação criptográfica das assinaturas digitais dos arquivos das urnas (ver [Limitações](#5-limitações)).

---

## 2. Metodologia

### 2.1 Princípios

1. **Somente fontes primárias oficiais.** Todo dado vem do Portal de Dados Abertos do TSE ou do servidor de
   arquivos do TSE. Nenhum dado de terceiros.
2. **Integridade antes da análise.** Nenhum arquivo baixado inteiro foi usado antes da conferência do hash publicado
   (quando existe) ou do registro de um hash próprio (quando não existe). As leituras parciais remotas (RDV de todo
   o país e logs fora de AC, RR e AP) não têm hash do pacote e foram conferidas apenas contra a BWeb.
3. **Reprodutibilidade.** Cada resultado é gerado por um script versionado; os resultados intermediários
   também estão no repositório.
4. **Contagem antes de estatística.** Onde é possível contar (somas, recontagens, cruzamentos de arquivos), a
   conclusão vem da contagem exata. A estatística entra só onde a pergunta é sobre padrões, e sempre com
   margem de erro.
5. **Controles.** Sempre que possível, cada padrão "suspeito" é comparado com: (a) o 1º turno das mesmas seções; (b) a eleição de
   2022; (c) seções vizinhas (mesmo município ou mesmo local de votação).
6. **Pior caso explícito.** Para cada suspeita, calcula-se quanto da margem ela poderia explicar no cenário mais
   desfavorável que os dados permitem.

### 2.2 Fontes de dados

| Código | Fonte | Conteúdo | Uso |
|---|---|---|---|
| F1 | BWeb — Boletins de Urna, 1º e 2º turnos 2026 | Votos por seção e candidato, aptos, comparecimento, horários, liberações manuais, urna e carga usadas | Base de quase todos os procedimentos |
| F2 | BWeb — Boletins de Urna, 2º turno 2022 | Idem, eleição anterior | Grupo de controle |
| F3 | Correspondências esperadas, 2º turno 2026 | Urna e código de carga previstos por seção, e lista de urnas de contingência, gerados em 24/10/2026 às 12:31 | Cadeia de custódia das urnas |
| F4 | Arquivos transmitidos para totalização | Por urna: BU digital (`bu.dat`), imagem do BU impresso, RDV (registro de cada voto), log, assinatura | Recontagem e confronto com a planilha |
| F5 | Relatório Resultado da Totalização (PDF) | Resultado oficial assinado, Brasil e cada UF, dois turnos | Confronto com a soma dos BUs |

Detalhes de cada arquivo, tamanhos e locais no repositório: README, seção 4.

### 2.3 Preparação e controle de integridade

1. **Download e hash.** Os 112 arquivos com hash oficial (F1, F2, F3) foram conferidos por SHA-512: 112 de 112
   conferem. Para F4 e F5, sem hash oficial, registrou-se SHA-512 próprio, tamanho, data e identificador (ETag)
   informados pelo servidor (`MANIFESTO.csv`).
2. **Extração do cargo de Presidente.** As linhas de Presidente foram copiadas byte a byte dos arquivos
   oficiais (`scripts/extrair_presidente.py`), com manifesto ligando cada arquivo extraído ao original e ao hash
   do TSE.
3. **Normalização do horário.** A urna grava o horário local (comprovado em `analise/FUSO.md` por três testes
   independentes). Os horários foram convertidos para Brasília por município: Acre e 11 municípios do oeste
   do Amazonas em UTC−5; demais municípios de AM, MT, MS, RO e RR em UTC−4; Fernando de Noronha em UTC−2;
   exterior excluído das análises de horário.
4. **Tabela por seção.** Uma linha por seção (499.205 no 2º turno, 499.206 no 1º), com votos de cada candidato,
   brancos, nulos, aptos, comparecimento, liberações manuais e horários (`analise/carregar.py`).

### 2.4 Procedimentos de auditoria

| # | Procedimento | Pergunta | Técnica | Script |
|---|---|---|---|---|
| P1 | Integridade dos arquivos | Os arquivos são os publicados pelo TSE? | Hash SHA-512 | `scripts/baixar_dados_tse.py` |
| P2 | Totalização | O resultado oficial é a soma dos BUs? | Soma por UF e Brasil × PDF oficial, campo a campo | `totalizacao.py` |
| P3 | Coerência interna | Cada BU fecha suas contas? | 9 regras lógicas por BU (aptos, comparecimento, votos, horários, carga) | `consistencia.py` |
| P4 | Recontagem voto a voto | A planilha reproduz o que cada urna registrou? | Decodificação ASN.1/DER do RDV de todas as urnas e contagem dos votos de Presidente | `recontagem_rdv.py`, `recontagem_rdv_nacional.py` |
| P5 | BU digital e imagem do BU | O BU digital e o texto que a urna manda imprimir batem com a planilha? | Decodificação do `bu.dat` e leitura do `imgbu.dat`, ambos do mesmo pacote (AC, RR, AP) | `recontagem_rdv.py`, `imagem_bu.py` |
| P6 | Logs das urnas | O diário da urna confirma o BU? | Leitura eleitor a eleitor do `logd.dat`: habilitações, votos, horários | `logs_urna.py` |
| P7 | Cadeia de custódia | As urnas usadas eram as previstas? | Cruzamento urna/carga do BU × lista de correspondências com data de geração de 24/10 (baixada em 29/10), com classificação de cada divergência | `correspondencia.py` |
| P8 | Réplica das suspeitas | Os números que circularam se reproduzem? | Recalcular cada número com o mesmo critério usado na afirmação | `suspeitas.py` |
| P9 | Horário de encerramento | Há "duas eleições" antes e depois das 17h? | Decomposição por estado e município; comparação com 2022 e com o 1º turno | `suspeitas.py` |
| P10 | Seções fechadas às 19h | Essas seções receberam votos irregulares? | Leitura do log de cada uma das 6.352 urnas (horário de cada voto); comparação com seções do mesmo local; comparação com o 1º turno | `logs_tardias.py`, `suspeitas.py`, `primeiro_turno.py` |
| P11 | Liberação manual ("sem biometria") | As liberações favoreceram um candidato? | Inclinação ponderada com efeitos fixos (país, estado, município) e margem de erro; pior caso aritmético; teste contra o 1º turno (nível e variação) | `suspeitas.py`, `primeiro_turno.py` |
| P12 | 1º × 2º turno | Algum grupo de seções destoa do próprio 1º turno? | Modelo de previsão por seção (6 especificações: linear e logit; nacional, estadual e municipal; com e sem peso), resíduo por grupo com erro-padrão agrupado por município, seções extremas | `primeiro_turno.py` |
| P13 | Testes de dígitos | Há sinal de números inventados? | Benford 1º e 2º dígitos comparados a uma eleição honesta simulada; uniformidade do último dígito | `suspeitas.py` |
| P14 | Publicação dos dados | Os dados ficaram "trancados"? | Datas do servidor, do catálogo e dos próprios arquivos | `SERVIDOR.csv`, `CATALOGO.csv` |
| P15 | Liberação manual em detalhe | Onde, quando e por quem as liberações aconteceram? | Taxa por estado e município nos dois turnos; leitura eleitor a eleitor dos logs de 10.809 urnas (seções das 19h, vizinhas e amostra aleatória de 3.000), com hora e mesário de cada liberação | `biometria.py` |

### 2.5 Critérios de avaliação

- **Procedimentos de contagem (P1–P7):** o critério é igualdade exata. Qualquer diferença é investigada até
  ser explicada ou registrada como achado.
- **Procedimentos estatísticos (P9–P13):** um grupo de seções é considerado anômalo se o seu desvio em relação ao
  esperado for positivo para um candidato, estatisticamente significativo (margem de erro de 95%, erro-padrão
  agrupado por município) e robusto às diferentes especificações do modelo.
- **Materialidade:** um achado é material se, no pior caso compatível com os testes feitos, puder explicar 10% ou
  mais da margem de 4.430.191 votos (443 mil). Cenários aritméticos que os testes contradizem são mostrados, mas não
  entram nessa conta. Estes critérios foram definidos durante a análise.
- **O que mudaria a conclusão:** uma UF cuja soma de boletins não bata com o oficial; um RDV diferente do boletim; um
  log com voto fora do horário ou liberações diferentes do boletim; um grupo de seções que se desvie a favor de um
  candidato em todas as especificações, inclusive dentro do município; boletins de papel diferentes dos arquivos;
  assinaturas inválidas. Os quatro primeiros não apareceram; os dois últimos não foram testados.

### 2.6 Ferramentas

Python 3 (pandas, numpy, matplotlib), `pdftotext`, um leitor DER mínimo escrito para este trabalho (sem a
especificação oficial do formato) e leitura remota dos pacotes do TSE por download parcial (HTTP Range), que
permitiu ler o RDV de todas as urnas e o log das urnas de interesse evitando baixar os mais de 100 GB dos pacotes.

---

## 3. Resultados por procedimento

| # | Resultado | Detalhe |
|---|---|---|
| P1 | 112/112 arquivos com hash oficial conferem | README 6.1 |
| P2 | Votos, brancos, nulos e comparecimento idênticos ao oficial em 29/29 regiões, nos dois turnos. Diferenças só em seções e aptos: 1–2 seções do exterior sem nenhum votante. Os 5.246 votos do nº 28 no 1º turno são exatamente os "nulos técnicos" oficiais | `analise/TOTALIZACAO.md` |
| P3 | 0 violações nas regras de contagem. Exceções de horário explicadas: 29 seções apuradas em cédula, 5 urnas substituídas antes da abertura, 8 BUs com relógio até 52 s adiantado | `analise/CONSISTENCIA.md` |
| P4 | 499.178 de 499.178 seções com urna eletrônica: RDV idêntico à planilha (Lula, Flávio, brancos, nulos). As 27 restantes são seções do exterior apuradas em cédula, cujo arquivo não segue o formato do RDV da urna; seus 831 votos são a diferença exata | `analise/RECONTAGEM_RDV_NACIONAL.md` |
| P5 | AC, RR, AP: BU digital, código de carga e imagem do BU iguais à planilha em 5.703/5.703 | `analise/RECONTAGEM_RDV.md`, `IMAGEM_BU.md` |
| P6 | AC, RR, AP: votos, habilitações biométricas, manuais e sem biometria no log iguais ao BU em 5.703/5.703; nenhum voto após o fechamento | `analise/LOGS.md` |
| P7 | 99,4% das seções com urna e carga exatamente previstas; trocas por contingência registradas. 17 seções (4.563 votos, saldo +42 Lula) sem explicação nos dados | `analise/CORRESPONDENCIA.md` |
| P8 | Os números que circularam se reproduzem com o critério usado neles (relógio local) | `analise/RESULTADOS.md` §1 |
| P9 | A diferença do grupo "até 17h" cai de −5,9 para −0,2 p.p. dentro do mesmo município, aparece em 2022 e já existia no 1º turno (−5,95 p.p.) | `analise/RESULTADOS.md` §2 |
| P10 | 6.352 seções fecharam às 19h (pico real, só no 2º turno). Só 4.492 de 1.861.259 votos (0,24%) foram dados após as 17h. Mesmo comparecimento e voto que as seções do mesmo local que fecharam às 17h (diferenças de −0,06 e +0,03 p.p.) | `analise/LOGS_TARDIAS.md`, `RESULTADOS.md` §4 |
| P11 | Dentro do município, os liberados votam quase como os demais (54% Lula); mais liberação vem com menos Lula do que o 1º turno previa; o aumento da liberação entre turnos não tem efeito | `analise/RESULTADOS.md` §5, `PRIMEIRO_TURNO.md` §5 |
| P12 | O 1º turno explica 93,2% das diferenças entre seções da mesma cidade (98,5% no país). Nenhum grupo desvia a favor de Lula de forma significativa; nas seções das 19h o desvio fica entre −0,12 e +0,18 p.p., sem nenhuma forma distinguível de zero. O grupo de liberação ≥ 20% fica abaixo do previsto para Lula em todas as formas (−0,19 a −0,58 p.p., 3 a 10 mil votos a favor de Flávio). Limite superior de 95% para as seções das 19h, na forma mais desfavorável: 18.771 votos | `analise/PRIMEIRO_TURNO.md` |
| P13 | Os dígitos dos votos reais são indistinguíveis dos de uma eleição honesta simulada; último dígito uniforme | `analise/RESULTADOS.md` §7 |
| P15 | Taxa entre 4,1% (RR) e 9,0% (PI), alta também em estados pró-Flávio (RS 8,45%); estável entre turnos (+0,07 p.p.). Logs de 10.809 urnas: liberações = BU em 100%; mais liberações de manhã, queda ao longo do dia; nas seções das 19h só 245 liberações depois das 17h. 16 seções com ≥ 50 liberações por um mesário, sem favorecimento (Lula abaixo da zona em 11) | `analise/BIOMETRIA.md` |
| P14 | Arquivos no servidor em 26/10 (~1 dia após a eleição); listados no catálogo em 27/10; ausentes do catálogo na consulta de 29/10, embora ainda no servidor e idênticos | README 6.12 |

---

## 4. Achados

Classificação: **material** (poderia afetar o resultado), **relevante** (merece esclarecimento oficial, mas não
afeta o resultado), **informativo**.

| # | Achado | Classificação | Pior caso sobre a margem |
|---|---|---|---|
| A1 | 1.131 locais de votação, sobretudo em capitais e grandes cidades do RJ, SP, BA, PE e PB, encerraram às 19h no 2º turno (6.352 seções). Os dados não informam o motivo | Relevante | 4.492 votos após as 17h (0,1%); anular todas: 185.724 (4,2%) |
| A2 | 17 seções usaram urna fora das listas publicadas, sem explicação nos dados | Relevante | 4.563 votos (0,1%) |
| A3 | Outras 382 seções usaram urna ou carga diferente da prevista, com explicação provável nos dados (recarga, troca depois da lista, mesmo cartão de carga) | Informativo | 96.234 votos (2,2%); saldo +6.603 Lula (0,15%) |
| A4 | Os BUs do 2º turno entraram no catálogo do portal só em 27/10 e saíram dele até 29/10, embora permaneçam no servidor | Relevante (transparência) | Nenhum: os arquivos batem com o resultado assinado em 25/10 |
| A5 | Os pacotes de arquivos das urnas e o PDF de totalização não têm hash oficial publicado | Informativo (transparência) | Nenhum |
| A6 | Em 29% das liberações manuais (AC, RR, AP), a digital do mesário foi capturada mas não associada a um nome | Informativo | Liberações não favorecem candidato (P11) |
| A7 | 8 BUs registram emissão até 52 s depois do recebimento pelo TSE (relógio da urna adiantado) | Informativo | Nenhum |
| A8 | 16 seções (de 10.809 com log lido) em que um mesário liberou 50 ou mais eleitores manualmente; em 2, padrão de leitor biométrico com defeito pela manhã | Informativo | Sem favorecimento: Lula abaixo da zona em 11 das 16 |

**Nenhum achado é material.**

---

## 5. Limitações

1. **Assinaturas digitais não verificadas.** Os arquivos das urnas são assinados digitalmente; esta auditoria não
   validou as assinaturas com as chaves públicas do TSE. Todas as conferências de P4–P6 comparam arquivos do
   mesmo pacote entre si e com a planilha; provam coerência total, mas não, sozinhas, a autenticidade do pacote.
2. **Logs e imagem do BU:** lidos para AC, RR e AP (5.703 urnas); logs também para as 6.352 seções fechadas às 19h,
   dois sorteios de vizinhas de controle e uma amostra aleatória de 3.000 seções do Brasil (11.382 urnas distintas);
   não para todas as urnas. A imagem do BU (`imgbu.dat`) vem do mesmo pacote; não é o boletim de papel.
3. **Software da urna fora do escopo.** Dados de votação não provam que o software é íntegro; isso cabe aos testes
   públicos de segurança e à fiscalização. O que os dados mostram é que BU, RDV, log e resultado oficial contam
   a mesma história.
4. **Inferência ecológica.** Os testes sobre liberação manual usam dados agregados por seção; não é possível saber
   como cada eleitor liberado votou. Por isso foram usados vários testes, inclusive contra o 1º turno.
5. **Modelo 1º → 2º turno** detecta desvios **entre grupos** de seções; uma manipulação uniforme em todo o país
   seria absorvida por ele. Se ocorresse depois da urna, apareceria em P2 e P4; se ocorresse dentro da urna, RDV,
   boletim e log sairiam coerentes entre si, e só a auditoria do software poderia detectá-la.
6. **Hash do mesmo servidor e ausência de conferência externa.** Os `.sha512` oficiais vêm do mesmo servidor dos
   dados; provam a integridade do download, não a independência da fonte. Todas as conferências comparam arquivos
   publicados pelo TSE entre si; nenhum boletim de papel (por exemplo, fotografado por fiscais) foi comparado.
7. **Atos administrativos e judiciais** (motivo do fechamento às 19h, registros das trocas de urna) não constam
   dos dados públicos de votação.
8. **Incerteza dos limites estatísticos.** Os limites das seções das 19h usam erro-padrão agrupado por município,
   e 75% dessas seções estão em 5 municípios, o que pode subestimar a incerteza. Como verificação grosseira,
   dobrar o limite leva a cerca de 38 mil votos (0,8% da margem).

---

## 6. Conclusão da auditoria

Com base nos procedimentos descritos e dentro do escopo e das limitações acima, concluímos que:

1. O resultado oficial da eleição para Presidente de 2026 corresponde exatamente à soma dos boletins de urna,
   em todas as unidades da federação e nos dois turnos.

2. Os boletins de urna coincidem com o Registro Digital do Voto publicado para cada urna (assinaturas não
   verificadas; ver limitação 1). A recontagem voto a voto do Registro Digital
   do Voto de todas as 499.178 urnas eletrônicas do 2º turno reproduziu exatamente os votos de cada candidato,
   os brancos e os nulos de cada seção. Nos estados em que os arquivos foram lidos integralmente (AC, RR, AP), o
   boletim digital, a imagem do boletim e o log de cada urna também coincidem com a planilha oficial.

3. A cadeia de custódia das urnas é consistente com a lista gerada antes da eleição em 99,4% das seções; a maior
   parte das trocas usou urna de contingência da lista, e 382 seções têm explicação provável nos dados. Restam 17 seções (4.563 votos) cuja urna não tem explicação nos dados públicos.

4. As suspeitas que circularam não se sustentam. Os números citados nelas são reproduzíveis, mas as
   conclusões decorrem de erros de interpretação, principalmente o uso do horário local da
   urna como se fosse o de Brasília, a ausência de grupos de controle e a comparação de grandezas incomparáveis
   (Anexo A).

5. Não foram encontrados padrões estatísticos compatíveis com manipulação. Nenhum grupo de seções testado
   (fechamento tardio, corte das 17h no relógio local, liberação manual elevada) se desvia a favor de Lula de forma
   significativa em relação ao próprio 1º turno ou às seções vizinhas.

6. Nenhum achado é material. Entre as suspeitas medidas em votos, a maior (anular todas as seções que fecharam às
   19h) corresponde a 4,2% da margem; com base nos logs das urnas, os votos efetivamente dados no horário
   estendido correspondem a 0,1%. A liberação manual só inverteria o resultado em cenários (voto em bloco dos
   liberados, ou comparação que ignora a geografia) para os quais os testes contra o 1º turno não mostram sinal.

7. A liberação manual de eleitores não mostra uso irregular. A taxa é estável entre os turnos, alta também em
   estados onde Flávio venceu e, nos logs lidos, maior de manhã e decrescente ao longo do dia; nas seções que ficaram abertas até as
   19h, só 245 eleitores foram liberados manualmente depois das 17h.

**Parecer:** os dados públicos do TSE não apresentam evidência de fraude ou de alteração do resultado da eleição
presidencial de 2026. O resultado proclamado (Lula 64.256.232 votos, 51,79%; Flávio Bolsonaro 59.826.041 votos,
48,21%; margem de 4.430.191 votos) é coerente com todos os registros públicos verificados.

Este parecer não abrange a segurança do software da urna nem os atos administrativos e judiciais citados nas
limitações, e não substitui perícia oficial.

---

## 7. Recomendações

Para o TSE e os TREs, com o objetivo de aumentar a transparência e facilitar auditorias independentes:

1. Publicar os atos que motivaram o encerramento às 19h nos locais do achado A1, com a lista dos locais afetados.
2. Publicar as atas das 17 seções do achado A2 (lista em `analise/secoes_para_documentar.csv`, categorias 7 e 10).
3. Publicar o hash SHA-512 dos pacotes de arquivos das urnas e do relatório de totalização.
4. Manter os arquivos de cada turno listados no catálogo do portal de forma permanente, com data de publicação.
5. Para partidos e observadores: comparar uma amostra de boletins de papel fotografados por fiscais com os
   arquivos publicados, a única conferência de fora do TSE.
6. Publicar a especificação do formato ASN.1 do RDV e do BU, junto com as chaves públicas e o procedimento de
   verificação das assinaturas, para que qualquer pessoa possa validá-las.

Para quem analisa dados eleitorais:

7. Converter o horário da urna para Brasília antes de qualquer análise por horário.
8. Comparar sempre com um controle (turno anterior, eleição anterior, seções vizinhas) antes de concluir que um
   padrão é anômalo.

---

## Anexo A — Suspeitas testadas e parecer

| Suspeita | O número confere? | Avaliação |
|---|---|---|
| Até 17h Flávio venceu com 52,39%; a virada veio depois das 17h | Sim (relógio local) | Não se sustenta. Efeito de fuso horário e geografia; ocorre em 2022 e já existia no 1º turno |
| Mais de 2 milhões votaram em seções fechadas após as 19h | Não: pelo relógio local, 2,30 mi são aptos; votaram 1,86 mi | Não se sustenta. Só 4.492 votos após as 17h; votação igual às seções vizinhas e ao 1º turno; no RJ, Flávio venceu nessas seções |
| 8.632.488 liberados sem biometria, quase o dobro da margem | Sim | Não se sustenta. Liberação é estável por seção, não favorece candidato e vem com menos Lula do que o previsto |
| 106 seções com 100% Lula contra 4 de Flávio | Sim | Não se sustenta como indício. Reflete voto regional; padrão semelhante em 2022 (143 × 4) |
| Teste de Benford indica manipulação | — | Não se sustenta. Comportamento idêntico ao de uma eleição honesta simulada |
| Dados trancados por 72 horas | Parcialmente | Procede em parte quanto à acessibilidade (catálogo só em 27/10); não procede quanto a alteração (resultado assinado em 25/10 bate com os arquivos) |
| Afirmações políticas e jurídicas | — | Fora do escopo (não constam dos dados) |

---

## Anexo B — Como reproduzir

```bash
git clone https://github.com/JardaCoder/independent-audit-brazil-elections-2026.git && cd independent-audit-brazil-elections-2026
pip install pandas numpy tabulate matplotlib geopandas   # e poppler-utils para pdftotext
python3 scripts/remontar_arquivos_urna.py
cd analise
python3 totalizacao.py; python3 consistencia.py; python3 fuso.py
python3 recontagem_rdv.py AC RR AP; python3 imagem_bu.py AC RR AP; python3 logs_urna.py AC RR AP
python3 correspondencia.py; python3 suspeitas.py; python3 primeiro_turno.py; python3 graficos.py
python3 logs_tardias.py --refazer; python3 recontagem_rdv_nacional.py   # leem do servidor do TSE
```

Explicação de cada etapa em linguagem simples, glossário e gráficos: [README](../README.md).
