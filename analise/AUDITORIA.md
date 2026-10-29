# Auditoria independente — 2º turno presidencial de 2026

O que este repositório faz: replicar o "Relatório Pericial Independente" que circulou nas redes e
auditar os próprios dados do TSE. Todas as etapas usam só arquivos públicos do TSE, com hash conferido, e
podem ser refeitas com os scripts em `analise/`.

## 1. Integridade dos arquivos

| Verificação | Resultado |
|---|---|
| SHA-512 dos 28 BWeb do 2º turno (27 UFs + exterior) | 28/28 conferem |
| SHA-512 das correspondências esperadas (publicadas em 24/10, véspera) | 28/28 conferem |
| SHA-512 dos BWeb de 2022 (controle) | 28/28 conferem |

## 2. Consistência interna de cada BU — [`CONSISTENCIA.md`](CONSISTENCIA.md)

Foram verificados 499.205 BUs e 538.946 pares seção×cargo. Resultado: **zero** violações em aptos = comparecimento +
abstenções, comparecimento ≤ aptos, soma dos votos = comparecimento, sem biometria ≤ comparecimento, uma urna
por seção e BU recebido depois de emitido.

Exceções, todas explicáveis:
- 29 seções do exterior sem horário de abertura e fechamento, compartilhando dois números de "urna". O padrão é
  compatível com votação sem urna eletrônica (cédula apurada em sistema).
- 5 urnas carregadas na manhã da eleição, com abertura da seção atrasada. É o padrão de substituição de urna antes da abertura.
- Comparecimento para Presidente maior que para Governador em 1.818 seções, nunca o contrário. É o voto em
  trânsito: quem vota fora do estado só vota para Presidente.

## 3. Arquivos originais assinados das urnas — [`LOGS.md`](LOGS.md)

Amostra: **AC, RR e AP**, 5.703 urnas. Para cada urna foram lidos a imagem do BU impresso e o log (`logd.dat`, inclusive
os logs arquivados de urnas substituídas).

| Verificação | AC | RR | AP |
|---|---|---|---|
| BU impresso = planilha BWeb (votos de cada candidato, comparecimento) | 2270/2270 | 1519/1519 | 1914/1914 |
| Votos computados no log = comparecimento do BU | 2270/2270 | 1519/1519 | 1914/1914 |
| Liberações manuais no log = "habilitação biográfica" do BU | 2270/2270 | 1519/1519 | 1914/1914 |
| Voto registrado depois do fechamento | 0 | 0 | 0 |

Como funciona a liberação manual, segundo os logs:
1. A digital do eleitor falha 4 vezes.
2. A urna pede um dado pessoal do eleitor. Se não confere, recusa: houve 1.383 recusas nas 3 UFs.
3. A urna exige a digital de um mesário e registra qual mesário liberou.

A taxa de liberação manual é maior de manhã e cai ao longo do dia; não há pico no fim da votação. Nenhum mesário liberou mais de 44
eleitores numa seção. O relatório descreve esse procedimento como "simples digitação do ano de nascimento"; o log
mostra que não é isso.

## 4. Urnas usadas × urnas publicadas antes da eleição — [`CORRESPONDENCIA.md`](CORRESPONDENCIA.md)

- 496.147 seções (99,4%) usaram exatamente a urna esperada, e 496.138 delas também o código de carga esperado.
- 2.899 trocas foram feitas por urnas de contingência já listadas.
- Sobram **168 seções** que pedem documentação: urna fora da lista, carga diferente ou seção fora da lista.
  Somam 37.639 votos, com saldo líquido de 4.835 para Lula, cerca de 0,1% da margem. A lista completa está em
  [`secoes_para_documentar.csv`](secoes_para_documentar.csv). 97 dessas urnas foram carregadas em 24/10, mesmo
  dia em que a lista foi gerada, então provavelmente são substituições posteriores a ela. O próximo passo é pedir as atas
  dessas seções aos TREs.

## 5. Réplica do relatório — [`RESULTADOS.md`](RESULTADOS.md)

**Todos os números do relatório se reproduzem** quando se usa o relógio local da urna e as faixas
dele. As conclusões, porém, não se sustentam:

| Afirmação | Achado |
|---|---|
| "Duas eleições": o candidato 22 vence até 17h e Lula depois | O mesmo corte em **2022** dá o mesmo padrão: Bolsonaro +1,04 mi até 17:00:59, Lula +3,1 mi depois. O primeiro grupo concentra os estados a oeste (relógio local 15h/16h) e as seções pequenas. A faixa 17:01–17:15, que reúne 68% das seções, é o fechamento normal da fila. |
| Seções depois das 19h | São reais: 6.342 em 2026, contra 20 em 2022. Pesam cerca de 187 mil votos de saldo, 4% da margem. Sem nenhuma seção fechada depois das 17h15, Lula ainda vence por 4,1 mi. |
| 8,6 mi sem biometria ≈ 2× a margem | Correlação com % Lula de 0,07 no país e 0,01 dentro do município. Excluindo esses eleitores, Lula ainda vence por 4,0 mi. Em 2022 a razão foi de 4,7×. |
| 106 × 4 seções unânimes | Confere. Em 2022 foram 143 × 4. Reflete o voto regional (cerca de 69% de Lula no Nordeste). |
| Benford | Os dois candidatos desviam igualmente. O teste é inadequado para contagens por seção. |
| Dados "trancados 72h" | O servidor do TSE marca os BWeb com `Last-Modified` de 26/10, 9h de Brasília, cerca de 1 dia depois da eleição. |

## O que esta auditoria **não** cobre

- **Assinaturas digitais** (`*.vsc`): não foram verificadas criptograficamente. Para isso são necessários os certificados
  públicos da urna e o formato da assinatura.
- **Recontagem pelo RDV** (`*rdv.dat`, ASN.1): ainda não foi decodificado. Seria a recontagem voto a voto.
- **Logs das outras 24 UFs**: o script já suporta (`python3 scripts/baixar_dados_tse.py arquivos_urna_2t SP ...`),
  mas o volume total passa de 100 GB.
- **Afirmações jurídicas e políticas** (Cap. 6 do relatório: decisões judiciais, prorrogação, PF, reações
  internacionais) não estão nos microdados.

## Como reproduzir

```bash
pip install pandas tabulate
python3 scripts/baixar_dados_tse.py arquivos_urna_2t AC RR AP   # ~1,3 GB, só para a etapa 3
cd analise
python3 consistencia.py          # etapa 2
python3 logs_urna.py AC RR AP    # etapa 3
python3 correspondencia.py       # etapa 4
python3 verificar_relatorio.py   # etapa 5
```
