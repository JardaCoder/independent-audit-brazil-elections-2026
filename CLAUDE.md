# CLAUDE.md — contexto para continuar o trabalho

Auditoria independente, com dados públicos do TSE, da eleição presidencial de 2026 (1º turno 04/10, 2º turno
25/10, Lula nº 13 × Flávio Bolsonaro nº 22), incluindo o teste das suspeitas de fraude que circularam depois do
2º turno. **Idioma do projeto: português (BR).** Os textos (README, relatório, saídas .md) são escritos para
leigos entenderem.

**Regra editorial (pedido do usuário):** README.md tem pt-BR e inglês em blocos <details>; manter os dois em sincronia;
leitura rápida, entendível por leigo. os textos públicos (README, relatório, saídas .md, gráficos) não dizem que
o trabalho foi feito a partir de um relatório específico de rede social, não mencionam revisões/revisores e não
podem ter cara de texto gerado por IA (pouco negrito, sem frases de efeito, sem fórmulas "não é X, é Y", prosa
em vez de listas quando couber). As suspeitas aparecem como "suspeitas que circularam".

## Estado atual (concluído)

- Repositório **público**: https://github.com/JardaCoder/independent-audit-brazil-elections-2026 (renomeado de
  `elections-brazil`), branch padrão `main`. Para publicar: commit e `git push origin HEAD:main`. `gh` com a conta
  JardaCoder.
- **Veredito:** nenhuma evidência de fraude. Resultado oficial íntegro. Nenhum achado material.
- Documentos principais:
  - `README.md`: explicação para leigos, glossário, origem dos dados, problemas, 12 verificações com gráficos.
  - `docs/RELATORIO_DE_AUDITORIA.md`: relatório formal (escopo, metodologia P1–P15, achados A1–A8, limitações,
    parecer, recomendações, anexo com parecer por alegação).
  - `analise/*.md`: saída de cada script (gerada; não editar à mão — rode o script).

## Números-chave (para conferir se algo mudou)

| Item | Valor |
|---|---|
| 2º turno: Lula / Flávio | 64.256.232 (51,79%) / 59.826.041 (48,21%), margem **4.430.191** |
| 2º turno: comparecimento / seções com voto | 128.236.074 / 499.205 (oficial: 499.207 em funcionamento; 2 do exterior sem votantes) |
| 1º turno: Flávio / Lula | 56.104.503 (47,03%) / 53.879.538 (45,16%); válidos oficiais 119.300.788 |
| 1º turno: nº 28 | 5.246 votos = "nulos técnicos" do oficial (registro anulado). Tratado em `estatistica.NULO_TECNICO_1T` |
| Soma dos BUs × PDF oficial | idêntica em 29/29 regiões, nos dois turnos |
| Recontagem RDV nacional | 499.178/499.178 urnas eletrônicas idênticas à BWeb; 27 seções ZZ em cédula (Sistema de Apuração) sem RDV, 831 votos |
| Liberação manual ("sem biometria") | 8.632.488 no 2º turno (6,73%); campo `QT_ELEI_BIOM_SEM_HABILITACAO` = linha "Habilitação biográfica" do BU |
| Seções que fecharam ≥19h Brasília | 6.352 (1.993 no minuto 19:00; 1.131 locais); só 4.492 de 1.861.259 votos após 17h (logs) |
| Limite estatístico das seções das 19h | 23.360 votos (pior entre especificações, ponderação e EP município/UF/jackknife, IC 95%) |
| Urnas fora das listas sem explicação | 17 seções, 4.563 votos, saldo +42 Lula |
| Modelo 1º→2º turno (com lula_1) | R² 0,985 nacional; 0,932 dentro do município |
| Biometria (logs de 10.809 urnas distintas) | liberações no log = BU em 100%; nas seções das 19h, 245 liberações manuais depois das 17h; taxa por UF 4,1% (RR) a 9,0% (PI) |

## Estrutura

```
analise/carregar.py      carrega tabela por seção (Presidente) de dados/tse/<ano>/presidente/<turno>turno/*.csv.gz
                         com cache em dados/derivados/secoes_presidente_<t>t_<ano>.csv.gz.
                         FUSO por UF + FUSO_MUNICIPIO (oeste do AM UTC-5, Noronha UTC-2), fuso(df), exterior = NaN.
                         FAIXAS_SEG/FAIXAS_ROTULO e faixa_horario(): faixas de horário ÚNICAS para todos os scripts.
analise/estatistica.py   junta_turnos() (1º×2º por seção, sufixos _1/_2), regressores(), ajustar() (linear/logit,
                         efeito fixo por UF/município, peso), centrar(), coef_cluster() (EP agrupado),
                         especificacoes(), desvio_grupo(), limite_tardias(), locais() (NR_LOCAL_VOTACAO), fmt(), md()
analise/<verificação>.py um script por verificação; cada um grava o seu .md em analise/
                         (suspeitas.py = antigo verificar_relatorio.py → RESULTADOS.md)
scripts/                 baixar_dados_tse.py (conjuntos do portal + arquivos_urna_2t <UF>), extrair_presidente.py,
                         remontar_arquivos_urna.py
dados/tse/2026/boletim_urna/2turno/   BWeb oficiais (todos os cargos) + .sha512 + SERVIDOR.csv + CATALOGO.csv
dados/tse/2026/boletim_urna/1turno/   só .sha512 + SERVIDOR.csv (os .zip, 4,8 GB, ficam fora do git)
dados/tse/{2026,2022}/presidente/     linhas de Presidente copiadas byte a byte + MANIFESTO.csv
dados/tse/2026/correspondencias/2turno/  CESP (urna/carga previstas, gerados 24/10 12:31)
dados/tse/2026/arquivos_urna/2turno/  pacotes AC/RR/AP em partes de 90 MB (partes/) + MANIFESTO.csv;
                                      os .zip remontados são ignorados pelo git
dados/tse/2026/totalizacao/           PDF oficial (Relatorio_Resultado_Totalizacao_2026_BR.zip, T1 e T2)
dados/derivados/                      caches/resultados: secoes_*, locais_2t_2026, logs_tardias_2t_2026,
                                      recontagem_rdv_2t_2026 (consolidado). recontagem_rdv/ (parciais) é ignorado.
docs/graficos/                        13 PNGs gerados por analise/graficos.py (11–13 = mapas)
dados/ibge/                           malhas do IBGE para o mapa + MANIFESTO.csv
```

## Como rodar

```bash
pip install pandas numpy tabulate matplotlib geopandas   # pdftotext (poppler-utils) já existe no ambiente
python3 scripts/remontar_arquivos_urna.py      # necessário para logs_urna, imagem_bu, recontagem_rdv, fuso, graficos (g7)
cd analise
python3 totalizacao.py; python3 consistencia.py; python3 fuso.py
python3 recontagem_rdv.py AC RR AP; python3 imagem_bu.py AC RR AP; python3 logs_urna.py AC RR AP
python3 correspondencia.py; python3 suspeitas.py; python3 primeiro_turno.py; python3 graficos.py
python3 logs_tardias.py            # usa cache; --refazer lê do servidor do TSE (~20 min)
python3 biometria.py               # usa cache dados/derivados/biometria_logs_2t_2026.csv.gz; --refazer ~30 min
python3 recontagem_rdv_nacional.py # usa parciais em dados/derivados/recontagem_rdv/ se existirem; sem eles ~2 h
```

Depois de qualquer mudança: rode os scripts afetados, confira que os `.md` e PNGs mudaram só onde devia,
e atualize README e `docs/RELATORIO_DE_AUDITORIA.md` se algum número citado mudar (os números estão escritos
à mão nesses dois documentos).

## Armadilhas já resolvidas (não repetir)

- **Horário da urna é LOCAL**, não Brasília (prova em `analise/FUSO.md`: abertura 06/07/08h por fuso; nenhum BU
  chegou ao TSE antes de 17:05 Brasília; operador digita a hora à mão na preparação). Sempre usar `ENC_BRASILIA`
  e `faixa_horario()`; o relatório viral usou o relógio local, e as faixas dele (até 17:00:59, 17:01–17:15:59,
  17:16–18:59:59, 19:00–19:59:59) estão replicadas com `ENC_LOCAL`.
- "% Lula" = Lula ÷ (Lula + Flávio). "Saldo" = Lula − Flávio num grupo.
- BWeb tem uma linha por seção × votável; campos de seção (aptos, comparecimento, biometria) se repetem — contar
  uma vez por seção. `#NULO#` → `np.nan` (não `None`).
- 2022: campo `QT_ELEITORES_BIOMETRIA_NH`, números entre aspas, datas dd/mm/aaaa (`format="mixed", dayfirst=True`).
  Definição possivelmente diferente da de 2026: não comparar biometria entre anos.
- Código de carga no BWeb = `CD_CARGA_1` (18 díg.) + `CD_CARGA_2` (6 díg.); na CESP, completar zeros à esquerda (24).
- `*-log.jez` é **zip** (o leia-me diz 7z). Urnas de contingência trazem o log anterior num `.jez` aninhado.
  Ler cada `logd.dat` em ordem e classificar habilitação pela sessão do eleitor (o "tipo" pode vir depois de
  "Eleitor foi habilitado" no mesmo segundo). Filtrar o dia (`25/10/2026`).
- RDV/bu.dat são ASN.1/DER; leitor mínimo em `recontagem_rdv.py` (sem especificação oficial). Tipo de voto 6, nas 3 UFs lidas
  localmente, só aparece no AC (51 votos) e a BWeb conta como nulo; qualquer outro tipo desconhecido fica à parte e quebra a conferência.
- Pacotes de arquivos das urnas têm 2–25 GB por UF: ler remotamente com HTTP Range (`logs_tardias.ArquivoRemoto`,
  `ler_membro`). Os pacotes do 2º turno não estão no catálogo; URL padrão
  `https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2026_2t_<UF>.zip`.
- Estatística: correlação baixa ≠ efeito pequeno (usar inclinação com IC); mostrar todas as especificações
  (nacional e dentro do município), não só a favorável; "pior caso" deve ser realmente pior caso; R² não é
  "precisão". Modelo linear sem intercepto (frações somam 1); coeficientes não interpretáveis um a um.
- Exterior (ZZ): fuso de cada país → fora das análises de horário; 29 seções em cédula sem horário nem RDV.
- Catálogo do portal: os BWeb do 2º turno foram listados em 27/10 e **sumiram do catálogo** até 29/10 (arquivos
  continuam no servidor, idênticos). Registrado em `CATALOGO.csv`.
- GitHub: limite de 100 MB por arquivo (por isso as partes de 90 MB e só as linhas de Presidente do 1º turno).

## Ambiente

- Container remoto; HTTPS via proxy já configurado (curl e urllib funcionam com cdn.tse.jus.br e
  dadosabertos.tse.jus.br). Disco limitado (~18 GB livres no fim da sessão anterior): não baixar pacotes inteiros
  de urnas de UFs grandes.
- Python 3.12; versões em `requirements.txt`. Paleta dos gráficos: vermelho `#d1302b` = Lula, azul `#2a78d6` =
  adversário, cinza `#8a8984` = referência (validada com o skill dataviz).
- **Commits em nome do usuário** (JardelSchaeferNortis <jardel.schaefer@nortistech.com.br>), sem `Co-Authored-By` nem
  `Claude-Session`, sem citar modelo (pedido do usuário; o histórico inteiro foi reescrito assim).

## Próximos passos possíveis (não feitos)

1. **Verificar assinaturas digitais** (`*-vota.vsc`) com as chaves públicas do TSE — principal limitação aberta.
2. Ler logs e BU impresso de todas as UFs (hoje: AC, RR, AP inteiros + 6.352 seções das 19h + 1.500 controles),
   via leitura remota.
3. Recontagem pelo RDV do **1º turno** (mesmo método; pacotes `..._2026_1t_<UF>.zip`, estes estão no catálogo).
4. Repetir a recontagem RDV para 2022 como controle.
5. Seção "Por que o relatório errou" já está no README (seção 2); se o usuário pedir página web/artifact do
   relatório, partir de `docs/RELATORIO_DE_AUDITORIA.md`.
6. Se o usuário quiser, apagar a branch `ccr-92bb87e8-nv2127` e definir `main` como padrão no GitHub
   (Settings → General → Default branch; só ele pode fazer).
