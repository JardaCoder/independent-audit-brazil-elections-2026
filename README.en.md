# Independent audit of Brazil's 2026 presidential election

[Português](README.md) · English

A check of the 2026 presidential election result (1st round on Oct 4, runoff on Oct 25, Lula × Flávio Bolsonaro)
using only public data from Brazil's electoral court (TSE). Everything can be reproduced: the data is in this
repository (or downloads with one command) and every number comes from a script you can read and run. If you find
an error, open an issue with the script and the output.

The charts and the detailed outputs (`analise/*.md`) are in Portuguese. The formal audit report, also in
Portuguese, is at [`docs/RELATORIO_DE_AUDITORIA.md`](docs/RELATORIO_DE_AUDITORIA.md).

## Contents

1. [Introduction](#1-introduction)
2. [The hypotheses, one by one](#2-the-hypotheses-one-by-one)
3. [Conclusion](#3-conclusion)
4. [Extra: how the vote shifted between rounds](#4-extra-how-the-vote-shifted-between-rounds)
- [Appendix A. Glossary](#appendix-a-glossary)
- [Appendix B. Where each dataset came from](#appendix-b-where-each-dataset-came-from)
- [Appendix C. How to run everything](#appendix-c-how-to-run-everything)

---

## 1. Introduction

### Why this audit

Lula won the runoff by 4,430,191 votes (51.79% to 48.21%). Right after, fraud claims circulated that used the TSE's
own data: that polling stations closing late flipped the election, that millions of voters released without a
fingerprint decided the result, that the data was hidden for days. Claims made with public data can be checked with
the same data, and that is what this work does.

The method is simple. Where something can be counted, I count it: add up the polling-station reports, recount the
votes recorded by each voting machine, cross-check files against each other. Where the question is about patterns, I
compare each suspicious group with a control: the same polling station in the 1st round, the 2022 election, and
neighboring stations in the same city. And for each suspicion I compute how much of the margin it could explain in the
worst case the data allows.

### Official result

| 1st round, Oct 4, 2026 | Votes | % of valid votes |
|---|---|---|
| Flávio Bolsonaro (22) | 56,104,503 | 47.03% |
| Lula (13) | 53,879,538 | 45.16% |
| Augusto Cury (70) | 3,448,569 | 2.89% |
| Renan Santos (14) | 2,675,887 | 2.24% |
| Ronaldo Caiado (55) | 2,605,148 | 2.18% |
| Other 7 candidates | 587,143 | 0.49% |
| Valid votes | 119,300,788 | |
| Blank / null | 2,300,798 / 3,674,249 (incl. 5,246 technical nulls) | |
| Turnout | 125,275,835 (78.92% of registered voters) | |

| Runoff, Oct 25, 2026 | Votes | % of valid votes |
|---|---|---|
| Lula (13) | 64,256,232 | 51.79% |
| Flávio Bolsonaro (22) | 59,826,041 | 48.21% |
| Margin | 4,430,191 | |
| Blank / null | 1,430,496 / 2,723,305 | |
| Turnout | 128,236,074 (80.78% of registered voters) | |

### The hypotheses tested

Each hypothesis is one way the result could be wrong or altered. Section 2 tests them one by one.

| | Hypothesis | Verdict |
|---|---|---|
| H1 | The official result is not the sum of the polling-station reports. | Rejected |
| H2 | The reports don't match what the voting machines recorded. | Rejected |
| H3 | Voting machines other than the planned ones were used. | Rejected for 99.4% of stations; 17 stations unexplained by the data |
| H4 | There were "two elections": Flávio won until 5 pm and the turnaround came later. | Rejected |
| H5 | Stations that stayed open until 7 pm received extra votes. | Rejected; the 7 pm closing did happen |
| H6 | The 8.6 million voters released without a fingerprint decided the election. | No sign of it |
| H7 | Stations with 100% for Lula indicate fraud. | Rejected |
| H8 | Benford's law shows made-up numbers. | No sign (weak test) |
| H9 | The runoff departs from the 1st round, station by station. | Rejected |
| H10 | The data was "locked" for 72 hours so it could be altered. | Partly true about access; rejected about alteration |

### What would change the conclusion

I would conclude the result was altered if any of these showed up: a state whose sum of reports doesn't match the
official result; a machine's digital vote record different from its report; a log with votes outside voting hours
or releases different from the report; a group of stations deviating toward one candidate, relative to its own 1st
round, in every model form, including comparisons within the same city; paper reports different from the files;
invalid digital signatures. None of the first four appeared. The last two were not tested.

---

## 2. The hypotheses, one by one

### H1. Is the official result the sum of the reports?

First I checked the files: the SHA-512 of every downloaded file matches the `.sha512` published by the TSE in 112 of
112. That proves the download is intact, but the hash comes from the same server as the data.

Then `analise/totalizacao.py` adds up stations, registered voters, turnout, blank, null and each candidate's votes
across all reports, by state and nationwide, and compares them with the TSE's official PDF. Votes, blanks, nulls and
turnout match exactly in 29 of 29 regions (27 states, abroad and Brazil), in both rounds. Counting stations and
registered voters too, 27 of 29 match: the difference is 1 or 2 stations abroad where nobody voted. The runoff result
was signed at 11:28 pm on Oct 25.

Each report was also checked on its own (499,205 reports): turnout never exceeds registered voters, the sum of votes
always equals turnout, and the remaining rules hold with zero violations, except 8 reports received by the TSE up to
52 seconds before the machine printed them (machine clock slightly fast) and 5 machines replaced before opening.

Verdict: rejected.

### H2. Do the reports match what the machines recorded?

Besides the report, each machine records the digital vote record (RDV): every vote typed, shuffled. I wrote a reader
for that format (ASN.1/DER), counted the presidential votes one by one on every machine in the country and compared
them with the TSE spreadsheet.

| Recount from the RDV | Result |
|---|---|
| Stations with an electronic machine recounted | 499,178 |
| RDV identical to the spreadsheet (Lula, Flávio, blank, null) | 499,178 of 499,178 |
| Lula / Flávio adding up the RDVs | 64,255,787 / 59,825,688 |
| Difference from the official result | 445 / 353, exactly the votes of the 27 paper-ballot stations abroad |

In three states (AC, RR, AP; 5,703 machines) I read the whole package: digital report, software load code, the
printed-report image and each machine's log. Everything matches in 5,703 of 5,703, and no vote was recorded after
closing. Since the RDV is written by the same machine that produces the report, this shows nothing changed between
the machine and the national tally. It does not show that the machine software is honest (section 3).

Verdict: rejected.

### H3. Were the planned machines used?

The day before the election, the TSE generates a list of which machine and which software load goes to each station,
plus backup machines. `analise/correspondencia.py` compares each report with that list. In 496,138 stations
(127.4 million votes) machine and load were exactly as planned; most swaps used a backup machine that was on the list;
382 stations have a likely explanation in the data. 17 stations (4,563 votes, net +42 for Lula) have no explanation
in the data and can be clarified with the station minutes.

Verdict: rejected for 99.4% of stations. The remaining 17 change nothing.

### H4. Were there "two elections", before and after 5 pm?

The claim: in machines that closed by 5 pm Flávio won with 52.39%, and the turnaround only came later.

The numbers come out exactly when using the time as the machine records it. The catch is that the machine records
local time. Machines in Acre, Amazonas and the Center-West that closed at 5 pm Brasília time show 3 or 4 pm and fall
into the "before 5 pm" group. The proof: machines open at 6 am in Acre, 7 am in the North and Center-West and 8 am
elsewhere, that is, all at 8 am Brasília time.

Three facts show the "by 5 pm" group is geography: the same cut produces "two elections" in 2022 too; comparing only
stations within the same city, the gap falls from −5.9 to −0.2 points; and the same stations already voted that way
in the 1st round.

![Same cut in 2026 and 2022](docs/graficos/01_duas_eleicoes_2026_vs_2022.png)

Verdict: rejected.

### H5. Did stations open until 7 pm receive extra votes?

There is a real fact here. In the runoff, 6,352 stations (Brasília time) closed at 7 pm or shortly after, 1,993 of
them at exactly 7:00 pm, a sign of a set deadline rather than queues. They are in 1,131 polling places, mostly in
state capitals (Rio, São Paulo, Salvador). This did not happen in the 1st round or in 2022.

But the extra hours had almost no votes. I read the log of every one of the 6,352 machines: only 4,492 of 1,861,259
votes (0.24%) were cast after 5 pm. These stations also voted like the others: compared with stations in the same
polling place that closed at 5 pm, the difference in Lula's share is −0.06 points, and relative to their own 1st
round, no model form shows a deviation toward Lula distinguishable from chance. Even voiding all of them, Lula would
win by 4,244,467 votes.

![Votes after 5 pm](docs/graficos/04_votos_depois_das_17h_nas_secoes_tardias.png)

Verdict: rejected. Why these places stayed open until 7 pm is not in the data; it is in the regional courts' orders.

### H6. Did voters released without a fingerprint decide the election?

When a voter's fingerprint fails 4 times, the machine asks for personal data and then the poll worker's fingerprint.
The number checks out: 8,632,488 such releases (6.73% of turnout). Comparing it with the margin only makes sense if
these voters voted as a bloc. I tested that in four ways:

1. Arithmetic worst case: if every released voter had voted for Lula and were removed, Flávio would win by 4.19
   million. It is the extreme scenario, with no test behind it.
2. Slope (how Lula's share moves with the release rate). Comparing the whole country, it suggests 79% of released
   voters chose Lula; within the same city, 54%, close to everyone else. Release rates and Lula's vote are both higher
   in the Northeast, so the national comparison mixes in geography.
3. Against the 1st round: given how the same station voted in the 1st round, more releases come with slightly less
   Lula than expected, and the increase in releases between rounds has no effect.
4. Stability: each station's rate repeats across rounds and is high both where Lula won and where Flávio won easily.

Logs of 10,809 machines read voter by voter confirm the reports in 100% of them; releases are higher in the morning
and fall during the day.

Verdict: no sign the releases favored Lula. Since data is per station, how each individual voted cannot be known.

### H7. Do stations with 100% for Lula indicate fraud?

The counts that circulated (106 stations with 100% for Lula against 4 for Flávio) are right. But 75% of stations with
over 90% for Lula are in five Northeastern states where he got 69% to 76%, and 2022 shows the same pattern (143 against 4).

Verdict: rejected. It is regional voting.

### H8. Does Benford's law show made-up numbers?

The first-digit test does not apply to votes per station, and both candidates "fail" it the same way. The second and
last digits look like a simulated honest election.

Verdict: no sign. Digit tests detect little and are a weak complement to the counting tests.

### H9. Does the runoff depart from the 1st round, station by station?

The same station, with the same voters, voted twice in three weeks. If machines had been tampered with in the runoff,
those stations would leave the pattern the 1st round predicted. `analise/primeiro_turno.py` uses each station's 1st
round to predict Lula's runoff share, in six different ways, and compares prediction and reality. The prediction is
off by about 2 points per station on average and explains 93% of the differences between stations in the same city.

No suspicious group deviates toward Lula. In the 7 pm stations the gap stays between −0.12 and +0.18 points, too small
to distinguish from chance. The test cannot catch tampering identical in every station (that would show up in H1/H2 if
it happened after the machine; if inside the machine, only a software audit could catch it).

Verdict: rejected.

### H10. Was the data "locked" for 72 hours?

The files were on the server about 1 day after the election, but only appeared in the data portal's catalog about 2
days later, and by Oct 29 had dropped out of it again.

Verdict: partly true. The criticism that the data was slow to become accessible has merit. The claim that it was
hidden to be altered finds no support: the files match the result signed at 11:28 pm on election day.

---

## 3. Conclusion

The TSE's public data shows no sign that the runoff result was fabricated or altered. The official result is the exact
sum of the reports, the reports match vote by vote what each machine recorded, and no suspicious group of stations
moves toward Lula relative to its own 1st round. Almost all the numbers in the claims reproduce; the error is in the
reading: local time taken as Brasília time, regions mixed together, registered voters counted as voters, and
quantities that don't compare.

How much each suspicion could weigh, in the scenario considered:

| Suspicion | Votes | % of margin |
|---|---|---|
| Void every station that closed at 7 pm | 185,724 | 4.2% |
| 7 pm stations: 95% upper bound of the deviation from the 1st round | 18,771 | 0.4% |
| Stations far off the 1st→2nd round pattern (deviations toward Lula only) | 8,044 | 0.2% |
| Stations with an unexplained machine (all their votes) | 4,563 | 0.1% |
| 7 pm stations: every vote cast after 5 pm | 4,492 | 0.1% |
| Fingerprint releases, 95% bound comparing within the same city | margin would drop to 2.55 M | 42% |
| Fingerprint releases, arithmetic worst case | margin would become −4.19 M | 195% |

The fingerprint releases are the only suspicion with scenarios that flip the result, and they all assume released
voters voted as a bloc or that geography doesn't explain the relationship. The tests against the 1st round show no
sign of either.

Still open, not tested: the machines' digital signatures were not verified cryptographically (the main technical
limitation); no paper report was compared with the files (everything here compares TSE files with each other); no
data analysis proves the machine software is honest; logs were read for a large sample, not every machine; and why
about 1,100 polling places stayed open until 7 pm is only in the regional courts' orders.

---

## 4. Extra: how the vote shifted between rounds

The most direct way to see who gained ground is to look only at the two-way race: Lula's share of the votes for Lula
and Flávio. Nationwide it went from 49.0% in the 1st round to 51.8% in the runoff, a 2.8-point swing.

![Lula gained ground on Flávio in every state](docs/graficos/12_mapa_estados_disputa.png)

Lula gained in all 27 states. The gain was largest in the Southeast and Center-West (Rio +4.3 points, São Paulo +3.8,
Goiás +3.7) and smallest in the Northeast, where he was already very strong in the 1st round (Piauí +1.2, Bahia +1.4).

![Where Lula and Flávio gained ground, by municipality](docs/graficos/11_mapa_municipios_disputa.png)

By municipality the picture repeats: Lula gained ground in 5,411 of 5,571 (median +2.4 points). Of the 160 where
Flávio advanced (in blue), 123 are in the Northeast, mostly in Bahia (86) and Piauí (21), where Lula already had very
high shares.

Where did the swing come from? Lula went from 45.2% to 51.8% of valid votes (+6.6 points) and Flávio from 47.0% to
48.2% (+1.2). Both grow almost by construction, because the 1st round had other candidates: of the 7.8 points they
held, 6.6 went to Lula and 1.2 to Flávio. In Goiás both grew more than elsewhere (Lula +9.3, Flávio +6.1), because
Ronaldo Caiado got 12.3% there in the 1st round.

![Growth of Lula and Flávio by state, in valid votes](docs/graficos/13_mapa_estados_validos.png)

---

## Appendix A. Glossary

| Term | Meaning |
|---|---|
| Station (seção) | A voting "table": one room, one machine, a few hundred voters. Brazil has about 499,000. |
| Report (BU, boletim de urna) | The result each machine prints and records at closing, with each candidate's total. |
| BWeb | The TSE spreadsheet with the contents of every report. |
| RDV | The machine's digital vote record: every vote typed, shuffled (without saying who voted). Allows a recount. |
| Machine log | The machine's automatic diary, with the time of every event. |
| Fingerprint release | When a voter's fingerprint fails 4 times and the poll worker releases them another way (the "without biometrics" number, 8.6 million). |
| Points (p.p.) | Difference between percentages: from 50% to 52% is 2 points. |
| Within the same city | Comparing only stations in the same municipality, so regional differences don't get in the way. |

## Appendix B. Where each dataset came from

Election data comes from the TSE Open Data Portal (<https://dadosabertos.tse.jus.br>) and the TSE file server
(`cdn.tse.jus.br`); the map shapes come from IBGE. Everything was downloaded on Oct 29, 2026. Folder by folder, with
sizes and integrity checks, see the Portuguese [README](README.md#apêndice-b-de-onde-veio-cada-dado).

## Appendix C. How to run everything

Requires Python 3 and `pdftotext` (`poppler-utils`).

```bash
git clone https://github.com/JardaCoder/independent-audit-brazil-elections-2026.git
cd independent-audit-brazil-elections-2026
pip install pandas numpy tabulate matplotlib geopandas
python3 scripts/remontar_arquivos_urna.py   # reassembles the AC, RR, AP machine packages
cd analise
python3 totalizacao.py; python3 consistencia.py; python3 recontagem_rdv.py AC RR AP
python3 imagem_bu.py AC RR AP; python3 logs_urna.py AC RR AP; python3 correspondencia.py; python3 fuso.py
python3 suspeitas.py; python3 biometria.py; python3 primeiro_turno.py; python3 graficos.py
```

---

Independent work, with no ties to the TSE, parties or candidates.
