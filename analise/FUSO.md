# O horário gravado pela urna é o horário local

As urnas não têm internet. O relógio delas é acertado à mão durante a preparação, semanas antes, e depois segue contando sozinho. A pergunta é: o operador acerta pela hora local ou pela de Brasília?

## 1 e 2. Abertura e chegada ao TSE

| grupo                            | hora de abertura mais comum (relógio da urna)   | menor intervalo entre fechar (urna) e chegar ao TSE (Brasília), em horas   | primeiro BU recebido pelo TSE (Brasília)   |
|:---------------------------------|:------------------------------------------------|:---------------------------------------------------------------------------|:-------------------------------------------|
| AC (UTC−5)                       | 06:00 (100.0% das seções)                       | 2.06                                                                       | 17:05:10                                   |
| AM, MT, MS, RO, RR (UTC−4)       | 07:00 (98.1% das seções)                        | 1.04                                                                       | 17:05:10                                   |
| demais estados (UTC−3, Brasília) | 08:00 (100.0% das seções)                       | -0.01                                                                      | 17:05:10                                   |

- BUs recebidos pelo TSE antes das 17h00 de Brasília: **0**.
- Se as urnas do Acre estivessem no horário de Brasília, teriam aberto 2 horas antes do permitido e fechado às 15h de Brasília, e seus boletins chegariam ao TSE entre 15h e 17h. Nenhum chegou antes das 17h.
- O menor intervalo entre "fechou" e "chegou" é exatamente o fuso de cada grupo (2h, 1h, 0h).

## 3. O relógio é acertado à mão

No log de cada urna aparece o momento em que o operador digita a data e a hora, na preparação da urna, no cartório eleitoral do estado:

| UF   | urnas   | com hora digitada pelo operador no log   | exemplo                                                                                   |
|:-----|:--------|:-----------------------------------------|:------------------------------------------------------------------------------------------|
| AC   | 2.270   | 2.270                                    | 27/09/2026 13:59:53 → "Data e hora que foi digitada pelo operador: 27/09/2026 - 14:00:00" |
| RR   | 1.519   | 1.519                                    | 22/09/2026 08:31:31 → "Data e hora que foi digitada pelo operador: 22/09/2026 - 08:30:00" |
| AP   | 1.914   | 1.914                                    | 01/10/2026 09:33:49 → "Data e hora que foi digitada pelo operador: 01/10/2026 - 09:31:00" |

Conclusão: o horário de abertura, de encerramento e dos logs está no relógio local de cada estado. Para comparar com as regras (8h–17h de Brasília) é preciso converter. Ver `carregar.py` (fuso por município).

