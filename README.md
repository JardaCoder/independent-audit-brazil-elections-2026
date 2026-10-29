# elections-brazil

Dados oficiais do TSE das eleições de 2026 e uma checagem, número por número, do
"Relatório Pericial Independente" que circulou nas redes depois do 2º turno.

## Auditoria independente

O relatório completo está em **[`analise/AUDITORIA.md`](analise/AUDITORIA.md)**. Ele cobre integridade dos arquivos, consistência de
cada BU, BU × log original das urnas (AC, RR, AP), urnas usadas × urnas publicadas antes da eleição,
réplica exata do relatório e controle com 2022.

## Estrutura

```
dados/tse/2026/boletim_urna/2turno/    BUs (BWeb) do 2º turno, 27 UFs + exterior, com .sha512 do TSE
dados/tse/2026/correspondencias/2turno/ urna e carga esperadas por seção, publicadas em 24/10/2026
dados/tse/2022/boletim_urna/2turno/    BUs do 2º turno de 2022 (grupo de controle)
dados/tse/2026/<outros>/               baixados sob demanda, não versionados (vários GB)
scripts/baixar_dados_tse.py            baixa qualquer conjunto e confere o SHA-512
analise/                               scripts e resultados (AUDITORIA.md é o ponto de entrada)
```

```bash
python3 scripts/baixar_dados_tse.py                        # lista os conjuntos
python3 scripts/baixar_dados_tse.py arquivos_urna_2t AC    # BU/log/RDV assinados de cada urna
pip install pandas tabulate
python3 analise/verificar_relatorio.py
```

## Resumo da verificação

Todos os números do relatório **se reproduzem exatamente** quando se usa o relógio local da urna. Os números brutos também conferem com os arquivos oficiais: 499.205 seções,
128.236.074 votos, margem de 4.430.191 votos e 8.632.488 eleitores liberados sem
biometria. As **conclusões** tiradas desses números não se sustentam:

| Afirmação do relatório | O que os dados mostram |
|---|---|
| "Até as 17h Flávio venceu; a virada veio depois das 17h" | O campo `DT_ENCERRAMENTO` está no relógio **local** da urna. As urnas "fechadas antes das 17h" são as de AC, AM, MT, MS, RO e RR, que fecharam às 15h ou 16h locais (17h de Brasília). São estados em que Flávio vence, daí o resultado. Mesmo excluindo todas as seções que fecharam depois das 17h15 (Brasília), Lula vence por cerca de 4,1 milhões. |
| Seções após 19h decidiram a eleição | As 6.342 seções que fecharam às 19h ou depois (6.333 delas entre 19h e 19h59, o número citado no relatório) somam saldo de cerca de 187 mil votos para Lula, 4% da margem. No RJ, que tem mais seções tardias que qualquer outro estado, Flávio venceu nelas. Em SP, 94% das seções tardias são da capital. |
| 8,6 mi sem biometria ≈ dobro da margem | A correlação entre % sem biometria e % Lula é 0,07 no país e 0,01 dentro do mesmo município. A taxa é parecida no Nordeste (7,2%) e no resto do país (6,6%). Tirando esses eleitores proporcionalmente, Lula ainda vence por cerca de 4,0 milhões. |
| 106 × 4 seções unânimes "não gaussiano" | Os números conferem, mas refletem o voto regional: Lula teve cerca de 69% no Nordeste, onde estão quase todas essas seções. |
| Teste de Benford (resultado omitido) | Os dois candidatos desviam igualmente, como é esperado para contagens limitadas a cerca de 400 eleitores por seção. O teste não indica nada. |
| Dados "trancados por 72 horas" | O servidor do TSE informa `Last-Modified: 26/10/2026 12:00 GMT` (9h de Brasília de segunda-feira) para os BUs do 2º turno, cerca de 1 dia após a eleição. O relatório fala em quarta-feira, 28/10. Além disso, os BUs de cada urna costumam sair em resultados.tse.jus.br já na noite da apuração. |

Detalhes e tabelas completas em [`analise/RESULTADOS.md`](analise/RESULTADOS.md).

**Limites:** esta análise testa apenas o que os microdados permitem testar. Não cobre as
afirmações sobre decisões judiciais, prorrogação de horário, passaportes, PF ou reações
internacionais (Cap. 6); essas exigem outras fontes. A conversão de fuso usa o fuso
padrão de cada UF; os municípios do oeste do AM (UTC-5) ficam com 1h de erro, o que não
altera nenhuma conclusão.
