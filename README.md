# elections-brazil — auditoria independente do 2º turno de 2026

Depois do 2º turno presidencial de 2026 (25/10/2026, Lula × Flávio Bolsonaro), circulou nas redes um
"Relatório Pericial Independente". Ele afirma que a vitória de Lula teria sido "fabricada" em urnas
fechadas depois das 17h e em votos liberados sem biometria, e diz que "o método é replicável".

Este repositório faz duas coisas:

1. **Replica o relatório**: refaz cada conta dele com os mesmos dados oficiais do TSE.
2. **Audita os próprios dados**: confere a integridade dos arquivos, a consistência de cada boletim
   de urna, os arquivos originais gravados pelas urnas e se as urnas usadas eram as publicadas antes da
   eleição. Também usa 2022 como grupo de controle.

Só foram usados arquivos públicos do Portal de Dados Abertos do TSE, com hash conferido. Os dados
estão no repositório e qualquer etapa pode ser refeita com os scripts.

> Relatório completo da auditoria: **[`analise/AUDITORIA.md`](analise/AUDITORIA.md)**

---

## Conclusão em uma frase

Os números do relatório **conferem e se reproduzem exatamente**, mas as conclusões não se sustentam.
O mesmo método aplicado à eleição de 2022 mostra o mesmo padrão de "duas eleições". A auditoria dos
arquivos originais das urnas não encontrou divergência entre urna, boletim e totalização. Sobraram 168 seções
(cerca de 0,1% da margem) que pedem documentação aos TREs.

## O que foi feito, passo a passo

### 1. Download e integridade dos dados
Baixei do TSE os boletins de urna (BWeb) do 2º turno de 2026 (27 UFs + exterior), os mesmos de 2022, as
correspondências esperadas publicadas na véspera da eleição e os arquivos originais das urnas de AC, RR e
AP. Conferi todos os arquivos que têm `.sha512` oficial: 84 de 84 batem.

### 2. Consistência interna de cada boletim de urna — [`analise/CONSISTENCIA.md`](analise/CONSISTENCIA.md)
Foram verificados 499.205 BUs: aptos = comparecimento + abstenções, soma dos votos = comparecimento, comparecimento ≤
aptos, horários de abertura e fechamento, data da carga, uma urna por seção. Houve **zero violações** nas regras
de contagem, e as poucas exceções de horário têm explicação (votação no exterior sem urna, urnas
substituídas, voto em trânsito).

### 3. Arquivos originais das urnas — [`analise/LOGS.md`](analise/LOGS.md)
Para as 5.703 urnas de AC, RR e AP, li a imagem do BU impresso e o log interno da urna (`logd.dat`), que
registra cada eleitor habilitado e cada voto computado.
- O BU impresso e a planilha do TSE batem em **100%** das seções (votos de cada candidato e comparecimento).
- Os votos registrados no log e o comparecimento do BU também batem em **100%**.
- Nenhum voto foi registrado depois do horário de fechamento.
- A liberação manual (digital falhou) **não** é a "simples digitação do ano de nascimento". A urna pede um
  dado pessoal, recusa quando ele não confere (1.383 recusas na amostra) e exige a digital do mesário,
  registrando quem liberou.

### 4. Urnas usadas × urnas publicadas antes da eleição — [`analise/CORRESPONDENCIA.md`](analise/CORRESPONDENCIA.md)
Em 24/10, o TSE publicou qual urna e qual código de carga cada seção deveria usar.
- 99,4% das seções usaram exatamente a urna esperada.
- 2.899 trocas foram feitas por urnas de contingência que já estavam na lista.
- 168 seções (37.639 votos, saldo de 4.835 para Lula) ficaram fora desse padrão. Estão em
  [`analise/secoes_para_documentar.csv`](analise/secoes_para_documentar.csv) e são o próximo passo de uma auditoria:
  pedir as atas dessas seções aos TREs.

### 5. Réplica do relatório e controle com 2022 — [`analise/RESULTADOS.md`](analise/RESULTADOS.md)

| Afirmação do relatório | O que os dados mostram |
|---|---|
| "Até as 17h Flávio venceu; a virada veio depois" | Os números se reproduzem com o relógio **local** da urna. Mas o mesmo corte em 2022 dá Bolsonaro +1,04 mi "até 17h" e Lula na frente depois. O grupo que fecha "até 17:00:59" concentra os estados a oeste (lá, 17h de Brasília é 15h ou 16h no relógio local) e as seções pequenas, sem fila. A faixa 17:01–17:15, com 68% das seções do país, é o fechamento normal da fila. |
| Seções depois das 19h decidiram a eleição | Essas seções são reais e foram muito mais numerosas que em 2022 (6.342 contra 20). Mas o saldo delas é de cerca de 187 mil votos, 4% da margem. Excluindo todas as seções que fecharam depois das 17h15, Lula ainda vence por 4,1 mi. |
| 8,6 mi sem biometria ≈ dobro da margem | A correlação com o voto em Lula é 0,07 no país e 0,01 dentro do mesmo município. Excluindo esses eleitores, Lula ainda vence por 4,0 mi. Em 2022 o campo equivalente somou 4,7 vezes a margem. |
| 106 × 4 seções unânimes | Confere, e em 2022 foram 143 × 4. Reflete o voto regional: Lula teve cerca de 69% no Nordeste. |
| Lei de Benford | Os dois candidatos "falham" igualmente. O teste é inadequado para contagens por seção, que têm no máximo uns 400 eleitores. |
| Dados "trancados por 72 horas" | O servidor do TSE marca os arquivos com `Last-Modified` de 26/10, 9h de Brasília, cerca de 1 dia após a eleição. |

---

## Dados no repositório

| Pasta | Conteúdo | Fonte | Tamanho | Integridade |
|---|---|---|---|---|
| `dados/tse/2026/boletim_urna/2turno/` | BWeb do 2º turno 2026, todas as seções, 27 UFs + exterior (ZZ) | [Resultados 2026 – Boletim de Urna](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna) | 138 MB | `.sha512` oficial |
| `dados/tse/2026/correspondencias/2turno/` | Urna e carga esperadas por seção + urnas de contingência (gerado em 24/10/2026) | [Correspondências esperadas 2º turno](https://dadosabertos.tse.jus.br/dataset/resultados-2026-correspondencias-esperadas-e-efetivadas-2-turno) | 36 MB | `.sha512` oficial |
| `dados/tse/2026/arquivos_urna/2turno/partes/` | Arquivos originais de cada urna de **AC, RR e AP**: BU, imagem do BU, RDV, log e assinatura. Divididos em partes de 90 MB | [Arquivos transmitidos para totalização](https://dadosabertos.tse.jus.br/dataset/resultados-2026-arquivos-transmitidos-para-totalizacao) | 1,2 GB | `MANIFESTO.csv` (SHA-512 próprio, tamanho, ETag e Last-Modified do servidor; o TSE não publica hash desses pacotes) |
| `dados/tse/2022/boletim_urna/2turno/` | BWeb do 2º turno 2022 (grupo de controle) | [Resultados 2022 – Boletim de Urna](https://dadosabertos.tse.jus.br/dataset/resultados-2022-boletim-de-urna) | 67 MB | `.sha512` oficial |
| `dados/derivados/` | Uma linha por seção (Presidente, 2º turno), 2026 e 2022, gerada pelos scripts | `analise/carregar.py` | 18 MB | regenerável |

Para usar os arquivos das urnas, remonte os `.zip` primeiro. O script confere o SHA-512 de cada um:

```bash
scripts/remontar_arquivos_urna.sh
```

### O que ficou de fora (e como baixar)

Esses conjuntos não foram usados na auditoria ou são grandes demais para o GitHub, que aceita no máximo 100 MB
por arquivo e recomenda repositórios de poucos GB. O script baixa qualquer um e confere o hash:

```bash
python3 scripts/baixar_dados_tse.py                            # lista os conjuntos
python3 scripts/baixar_dados_tse.py bu_1t                      # BUs do 1º turno (~5 GB)
python3 scripts/baixar_dados_tse.py arquivos_urna_2t SP MG     # arquivos das urnas de outras UFs (>100 GB no total)
```

Também ficaram de fora votação por seção e município, comparecimento, eleitorado, mesários e logs do Gedai.

## Como reproduzir

```bash
pip install pandas tabulate
scripts/remontar_arquivos_urna.sh   # só para a etapa 3
cd analise
python3 consistencia.py             # etapa 2  -> CONSISTENCIA.md
python3 logs_urna.py AC RR AP       # etapa 3  -> LOGS.md
python3 correspondencia.py          # etapa 4  -> CORRESPONDENCIA.md
python3 verificar_relatorio.py      # etapa 5  -> RESULTADOS.md
```

| Script | O que faz |
|---|---|
| `scripts/baixar_dados_tse.py` | Baixa conjuntos do Portal de Dados Abertos e confere o SHA-512 |
| `scripts/remontar_arquivos_urna.sh` | Junta as partes dos pacotes das urnas e confere contra o manifesto |
| `analise/carregar.py` | Monta a tabela por seção a partir dos BWeb e converte o horário para Brasília |
| `analise/consistencia.py` | Regras de consistência em cada BU |
| `analise/imagem_bu.py` | Lê o BU impresso (`imgbu.dat`) e compara com a planilha |
| `analise/logs_urna.py` | Percorre o log de cada urna eleitor a eleitor e cruza com o BU |
| `analise/correspondencia.py` | Urna e carga usadas × esperadas |
| `analise/verificar_relatorio.py` | Réplica exata do relatório e controle com 2022 |

## Limites

- **Assinaturas digitais** das urnas (`*.vsc`) não foram verificadas criptograficamente.
- **Recontagem voto a voto pelo RDV** (`*rdv.dat`, formato ASN.1) ainda não foi feita.
- Os **logs** foram auditados em 3 de 27 UFs.
- O horário foi convertido pelo fuso padrão de cada UF. O oeste do AM (UTC-5) fica com 1h de erro, o que não
  muda nenhuma conclusão.
- As afirmações jurídicas e políticas do relatório (decisões judiciais, prorrogação, PF, reações
  internacionais) não estão nos microdados e não foram avaliadas.

Esta é uma análise independente, sem vínculo com o TSE, partidos ou autores do relatório. Correções e
reproduções são bem-vindas: abra uma issue com o script e o resultado.
