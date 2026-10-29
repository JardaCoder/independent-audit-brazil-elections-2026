"""Prova de que o horário gravado pela urna é o horário LOCAL do estado, e não o de Brasília.
Gera analise/FUSO.md.

Três testes:
1. Hora de abertura: a lei manda abrir às 8h de Brasília no país todo.
2. Hora em que o TSE recebeu cada BU: é anotada pelo servidor do TSE (Brasília), não pela urna.
3. Logs das urnas de AC, RR e AP: o relógio é acertado à mão por um operador na preparação da urna.
"""
import os
import re
import zipfile

import pandas as pd

from carregar import RAIZ, carregar
from estatistica import fmt, md
from imagem_bu import PASTA_URNA
from logs_urna import linhas_log

SAIDA = os.path.join(RAIZ, "analise", "FUSO.md")


def grupo(uf):
    if uf == "AC":
        return "AC (UTC−5)"
    if uf in ("AM", "MT", "MS", "RO", "RR"):
        return "AM, MT, MS, RO, RR (UTC−4)"
    return "demais estados (UTC−3, Brasília)"


def main():
    d = carregar()
    d = d[d.SG_UF != "ZZ"].copy()
    d["grupo"] = d.SG_UF.map(grupo)
    ab = pd.to_datetime(d.DT_ABERTURA)
    rec = pd.to_datetime(d.DT_BU_RECEBIDO)
    t = d.assign(abertura=ab.dt.strftime("%H:00")).groupby("grupo").abertura.agg(
        lambda s: f"{s.mode()[0]} ({s.eq(s.mode()[0]).mean() * 100:.1f}% das seções)").to_frame("hora de abertura mais comum (relógio da urna)")
    gap = (rec - d.ENC_LOCAL).dt.total_seconds() / 3600
    t["menor intervalo entre fechar (urna) e chegar ao TSE (Brasília), em horas"] = gap.groupby(d.grupo).min().round(2)
    t["primeiro BU recebido pelo TSE (Brasília)"] = rec.groupby(d.grupo).min().dt.strftime("%H:%M:%S")
    L = ["# O horário gravado pela urna é o horário local", "",
         "As urnas não têm internet. O relógio delas é acertado à mão durante a preparação, semanas antes, e depois "
         "segue contando sozinho. A pergunta é: o operador acerta pela hora local ou pela de Brasília?", "",
         "## 1 e 2. Abertura e chegada ao TSE", "", md(t), "",
         f"- BUs recebidos pelo TSE antes das 17h00 de Brasília: **{fmt((rec.dt.hour < 17).sum())}**.",
         "- Se as urnas do Acre estivessem no horário de Brasília, teriam aberto 2 horas antes do permitido e fechado às "
         "15h de Brasília, e seus boletins chegariam ao TSE entre 15h e 17h. Nenhum chegou antes das 17h.",
         "- O menor intervalo entre \"fechou\" e \"chegou\" é exatamente o fuso de cada grupo (2h, 1h, 0h).", ""]
    linhas = []
    for uf in ["AC", "RR", "AP"]:
        z = zipfile.ZipFile(os.path.join(PASTA_URNA, f"bu_imgbu_logjez_rdv_vscmr_2026_2t_{uf}.zip"))
        logs = sorted(n for n in z.namelist() if n.endswith("-log.jez"))
        com, exemplo = 0, ""
        for n in logs:
            for ln in linhas_log(z.read(n)):
                if "Data e hora que foi digitada pelo operador" in ln:
                    com += 1
                    if not exemplo:
                        p = ln.split("\t")
                        exemplo = f"{p[0]} → \"{p[4]}\""
                    break
        linhas.append({"UF": uf, "urnas": len(logs), "com hora digitada pelo operador no log": com, "exemplo": exemplo})
    L += ["## 3. O relógio é acertado à mão", "",
          "No log de cada urna aparece o momento em que o operador digita a data e a hora, na preparação da urna, "
          "no cartório eleitoral do estado:", "", md(pd.DataFrame(linhas), index=False), "",
          "Conclusão: o horário de abertura, de encerramento e dos logs está no relógio local de cada estado. Para "
          "comparar com as regras (8h–17h de Brasília) é preciso converter. Ver `carregar.py` (fuso por município).", ""]
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
