"""Análise dedicada da liberação manual de eleitores ("sem biometria"). Gera analise/BIOMETRIA.md.

Parte 1 (planilhas BWeb, todas as seções): taxa por estado e por município nos dois turnos.
Parte 2 (logs das urnas, eleitor a eleitor, com horário): quando as liberações aconteceram, quantas depois das
17h e quem liberou. Logs lidos direto do servidor do TSE (download parcial) para:
  - as 6.352 seções que fecharam às 19h ou depois;
  - 1.500 seções vizinhas (mesmo local de votação) que fecharam até 17h15;
  - uma amostra aleatória de 3.000 seções do Brasil (semente 2026).

    python3 analise/biometria.py            # usa o cache dos logs se existir
    python3 analise/biometria.py --refazer  # relê os logs do servidor (~30 min)
"""
import io
import os
import sys
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from carregar import RAIZ, carregar, fuso
from estatistica import fmt, md
from logs_tardias import URL, ArquivoRemoto, ler_membro, selecionar
from logs_urna import linhas_log

SAIDA = os.path.join(RAIZ, "analise", "BIOMETRIA.md")
CACHE = os.path.join(RAIZ, "dados", "derivados", "biometria_logs_2t_2026.csv.gz")
DIA = "25/10/2026"
TIPOS = ["biometrica", "manual", "sem_biometria", "outro"]
L = []


def out(s=""):
    L.append(s)


# ---------------------------------------------------------------- parte 2: leitura dos logs
def sessoes(linhas, desloc_h):
    """Percorre o log eleitor a eleitor. Para cada voto computado devolve (minuto em Brasília, tipo, mesário)."""
    tipo, mesario, votos = None, None, []
    for ln in linhas:
        if not ln.startswith(DIA):
            continue
        p = ln.split("\t")
        if len(p) < 5:
            continue
        msg = p[4]
        if msg.startswith("Aguardando digitação do identificador do eleitor"):
            tipo, mesario = None, None
        elif msg.startswith("Tipo de habilitação do eleitor [biométrica]"):
            tipo = "biometrica"
        elif msg.startswith("Solicitação de dado pessoal do eleitor para habilitação manual"):
            tipo = "manual"
        elif msg.startswith("Ano de nascimento digitado é igual ao do cadastro"):
            tipo = "sem_biometria"
        elif msg.startswith("Mesário") and msg.endswith("habilitou o eleitor"):
            mesario = msg.split()[1]
        elif msg.startswith(("Digital coletada bate com uma digital gravada após o registro inicial",
                             "Não encontrou digital coletada em nenhum dos arquivos")):
            mesario = "nao_identificado"
        elif msg == "O voto do eleitor foi computado":
            minuto = (int(p[0][11:13]) + desloc_h) * 60 + int(p[0][14:16])
            votos.append((minuto, tipo or "outro", mesario))
            tipo, mesario = None, None
    return votos


def resumo_urna(votos):
    r = {"votos_log": len(votos)}
    por_hora = Counter()
    mesarios = Counter()
    for minuto, tipo, mesario in votos:
        por_hora[(minuto // 60, tipo)] += 1
        r[f"n_{tipo}"] = r.get(f"n_{tipo}", 0) + 1
        if minuto >= 17 * 60:
            r[f"apos17_{tipo}"] = r.get(f"apos17_{tipo}", 0) + 1
            r["apos17_votos"] = r.get("apos17_votos", 0) + 1
        if tipo == "manual":
            if mesario and mesario != "nao_identificado":
                mesarios[mesario] += 1
                r["manual_mesario_identificado"] = r.get("manual_mesario_identificado", 0) + 1
            if minuto >= 17 * 60 and mesario and mesario != "nao_identificado":
                r["apos17_manual_mesario_identificado"] = r.get("apos17_manual_mesario_identificado", 0) + 1
    r["max_manual_um_mesario"] = max(mesarios.values(), default=0)
    r["por_hora"] = ";".join(f"{h}:{t}:{n}" for (h, t), n in sorted(por_hora.items()))
    return r


def amostra_nacional(n=3000, semente=2026):
    d = carregar(turno=2)
    d = d[d.SG_UF != "ZZ"].sample(n, random_state=semente).copy()
    d["grupo"] = "amostra aleatória do Brasil"
    d["fuso"] = fuso(d)
    d["arquivo"] = ("o03221" + d.SG_UF.str.lower() + d.CD_MUNICIPIO.astype(int).map("{:05d}".format)
                    + d.NR_ZONA.astype(int).map("{:04d}".format) + d.NR_SECAO.astype(int).map("{:04d}".format) + "-log.jez")
    return d


def ler_logs():
    sel = pd.concat([selecionar(), amostra_nacional()], ignore_index=True)
    linhas = []
    for uf, g in sel.groupby("SG_UF"):
        url = URL.format(uf)
        zf = zipfile.ZipFile(io.BufferedReader(ArquivoRemoto(url), buffer_size=1 << 22))
        infos = {i.filename: i for i in zf.infolist()}
        print(f"{uf}: {len(g)} seções", flush=True)

        def um(row):
            info = infos.get(row.arquivo)
            if info is None:
                return {"idx": row.Index, "erro": "sem log"}
            try:
                r = resumo_urna(sessoes(linhas_log(ler_membro(url, info)), int(row.fuso)))
            except Exception as e:
                return {"idx": row.Index, "erro": repr(e)[:150]}
            r["idx"] = row.Index
            return r

        with ThreadPoolExecutor(32) as ex:
            linhas.extend(ex.map(um, g.itertuples()))
    r = pd.DataFrame(linhas).set_index("idx")
    res = sel.join(r)
    cols = ["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "grupo", "QT_COMPARECIMENTO",
            "QT_BIOM_SEM_HAB", "V_13", "V_22"] + [c for c in r.columns]
    res[cols].to_csv(CACHE, index=False, compression="gzip")
    return res[cols]


# ---------------------------------------------------------------- parte 1: planilhas
def parte_planilhas():
    t1, t2 = carregar(turno=1), carregar(turno=2)
    t1, t2 = t1[t1.SG_UF != "ZZ"], t2[t2.SG_UF != "ZZ"]  # no exterior não há identificação biométrica
    out("## 1. Taxa de liberação manual por estado (todas as seções do Brasil; no exterior não há biometria)")
    out()
    out("Taxa = eleitores liberados manualmente ÷ comparecimento. \"% Lula\" = Lula ÷ (Lula + Flávio) no 2º turno.")
    out()
    g1 = t1.groupby("SG_UF")[["QT_BIOM_SEM_HAB", "QT_COMPARECIMENTO"]].sum()
    g2 = t2.groupby("SG_UF")[["QT_BIOM_SEM_HAB", "QT_COMPARECIMENTO", "V_13", "V_22"]].sum()
    uf = pd.DataFrame({
        "liberados 2º turno": g2.QT_BIOM_SEM_HAB.astype(int),
        "taxa 1º turno (%)": (g1.QT_BIOM_SEM_HAB / g1.QT_COMPARECIMENTO * 100).round(2),
        "taxa 2º turno (%)": (g2.QT_BIOM_SEM_HAB / g2.QT_COMPARECIMENTO * 100).round(2),
    })
    uf["variação (p.p.)"] = (uf["taxa 2º turno (%)"] - uf["taxa 1º turno (%)"]).round(2)
    uf["% Lula 2º turno"] = (g2.V_13 / (g2.V_13 + g2.V_22) * 100).round(1)
    x2 = t2.assign(t=t2.QT_BIOM_SEM_HAB / t2.QT_COMPARECIMENTO)
    uf["mediana por seção (%)"] = (x2.groupby("SG_UF").t.median() * 100).round(1)
    uf["seções com taxa ≥ 20%"] = x2[x2.t >= 0.2].groupby("SG_UF").size().reindex(uf.index).fillna(0).astype(int)
    uf.loc["Brasil"] = [int(g2.QT_BIOM_SEM_HAB.sum()), round(g1.QT_BIOM_SEM_HAB.sum() / g1.QT_COMPARECIMENTO.sum() * 100, 2),
                        round(g2.QT_BIOM_SEM_HAB.sum() / g2.QT_COMPARECIMENTO.sum() * 100, 2), 0,
                        round(g2.V_13.sum() / (g2.V_13.sum() + g2.V_22.sum()) * 100, 1), round(x2.t.median() * 100, 1),
                        int((x2.t >= 0.2).sum())]
    uf.loc["Brasil", "variação (p.p.)"] = round(uf.loc["Brasil", "taxa 2º turno (%)"] - uf.loc["Brasil", "taxa 1º turno (%)"], 2)
    uf = uf.sort_values("taxa 2º turno (%)", ascending=False)
    out(md(uf.astype({"liberados 2º turno": "int64", "seções com taxa ≥ 20%": "int64"})))
    out()
    sem_br = uf.drop("Brasil")
    c = np.corrcoef(sem_br["taxa 2º turno (%)"], sem_br["% Lula 2º turno"])[0, 1]
    out(f"- A taxa vai de {sem_br['taxa 2º turno (%)'].min():.2f}% ({sem_br['taxa 2º turno (%)'].idxmin()}) a "
        f"{sem_br['taxa 2º turno (%)'].max():.2f}% ({sem_br['taxa 2º turno (%)'].idxmax()}). Correlação, entre estados, "
        f"da taxa com a % de Lula: {c:.2f}.")
    out(f"- Do 1º para o 2º turno a taxa nacional mudou {uf.loc['Brasil', 'variação (p.p.)']:+.2f} p.p.; a maior variação "
        f"estadual foi {sem_br['variação (p.p.)'].abs().max():.2f} p.p. A liberação não \"apareceu\" no 2º turno.")
    out()
    # municípios
    gm = t2.groupby(["SG_UF", "NM_MUNICIPIO"]).agg(comp=("QT_COMPARECIMENTO", "sum"), lib=("QT_BIOM_SEM_HAB", "sum"),
                                                   l=("V_13", "sum"), f=("V_22", "sum"))
    gm["taxa (%)"] = (gm.lib / gm.comp * 100).round(1)
    gm["% Lula"] = (gm.l / (gm.l + gm.f) * 100).round(1)
    grandes = gm[gm.comp >= 5000]
    out("## 2. Municípios com as maiores taxas (com pelo menos 5.000 votantes)")
    out()
    top = grandes.sort_values("taxa (%)", ascending=False).head(15).reset_index()
    top = top.rename(columns={"comp": "votantes", "lib": "liberados"})[["SG_UF", "NM_MUNICIPIO", "votantes", "liberados",
                                                                         "taxa (%)", "% Lula"]]
    out(md(top.astype({"votantes": "int64", "liberados": "int64"}), index=False))
    out()
    q = pd.qcut(grandes["taxa (%)"], 5, labels=["20% com menor taxa", "2º quinto", "3º quinto", "4º quinto", "20% com maior taxa"])
    gq = grandes.groupby(q, observed=True).agg(municipios=("comp", "size"), l=("l", "sum"), f=("f", "sum"),
                                                taxa=("taxa (%)", "median"))
    gq["% Lula"] = (gq.l / (gq.l + gq.f) * 100).round(1)
    out("Municípios divididos em cinco grupos pela taxa de liberação:")
    out()
    out(md(gq[["municipios", "taxa", "% Lula"]].rename(columns={"taxa": "taxa mediana (%)"})))
    out()
    return uf


# ---------------------------------------------------------------- parte 2: relatório dos logs
def parte_logs(res):
    ok = res[res.get("erro").isna()] if "erro" in res else res
    for c in [f"n_{t}" for t in TIPOS] + [f"apos17_{t}" for t in TIPOS] + ["apos17_votos", "manual_mesario_identificado",
                                                                            "apos17_manual_mesario_identificado"]:
        if c not in ok:
            ok[c] = 0
    ok = ok.fillna({c: 0 for c in ok.columns if c.startswith(("n_", "apos17_", "manual_"))})
    out("## 3. O que os logs mostram, eleitor a eleitor")
    out()
    out("Cada log registra, para cada eleitor, como ele foi liberado e a hora do voto. Tipos: **biométrica** (digital "
        "reconhecida), **manual** (digital falhou 4 vezes; dado pessoal + digital do mesário), **sem biometria cadastrada** "
        "(eleitor sem digital no cadastro; ano de nascimento). Horário convertido para Brasília.")
    out()
    out(f"- Logs lidos: {fmt(len(ok))} de {fmt(len(res))}. Conferência: liberações manuais no log = número do BU em "
        f"{fmt((ok.n_manual == ok.QT_BIOM_SEM_HAB).sum())} seções; votos no log = comparecimento em "
        f"{fmt((ok.votos_log == ok.QT_COMPARECIMENTO).sum())}.")
    out()
    t = ok.groupby("grupo").agg(secoes=("votos_log", "size"), votos=("votos_log", "sum"), manuais=("n_manual", "sum"),
                                votos_apos_17h=("apos17_votos", "sum"), manuais_apos_17h=("apos17_manual", "sum"),
                                biometricas_apos_17h=("apos17_biometrica", "sum"))
    t["% manual (dia todo)"] = (t.manuais / t.votos * 100).round(2)
    t["% manual entre os votos após 17h"] = (t.manuais_apos_17h / t.votos_apos_17h.replace(0, np.nan) * 100).round(2)
    out(md(t.astype({c: "int64" for c in ["secoes", "votos", "manuais", "votos_apos_17h", "manuais_apos_17h", "biometricas_apos_17h"]})))
    out()
    tard = ok[ok.grupo == "fechou 19h ou depois"]
    ap = int(tard.apos17_manual.sum())
    out(f"- Nas seções que ficaram abertas até as 19h, **{fmt(ap)} eleitores** foram liberados manualmente depois das 17h, "
        f"em {fmt((tard.apos17_manual > 0).sum())} das {fmt(len(tard))} seções. Desses, "
        f"{fmt(tard.apos17_manual_mesario_identificado.sum())} com o mesário identificado pela digital.")
    out(f"- Mesmo que todos esses {fmt(ap)} votos fossem ilegítimos e de Lula, o efeito sobre a margem de 4.430.191 seria "
        f"{ap / 4430191 * 100:.3f}%.")
    out(f"- Maior número de liberações manuais feitas por um único mesário numa seção: {fmt(ok.max_manual_um_mesario.max())} "
        f"(mediana entre as seções com alguma liberação: {ok[ok.n_manual > 0].max_manual_um_mesario.median():.0f}).")
    out()
    # Por hora
    linhas = []
    for g, x in ok.groupby("grupo"):
        cont = Counter()
        for s in x.por_hora.dropna():
            for item in str(s).split(";"):
                if item.count(":") == 2:
                    h, tp, n = item.split(":")
                    cont[(int(h), tp)] += int(n)
        horas = sorted({h for h, _ in cont})
        for h in horas:
            tot = sum(cont[(h, tp)] for tp in TIPOS)
            if tot:
                linhas.append({"grupo": g, "hora (Brasília)": f"{h:02d}h", "votos": tot, "manuais": cont[(h, "manual")],
                               "% manual": round(cont[(h, "manual")] / tot * 100, 2)})
    ph = pd.DataFrame(linhas)
    out("### Liberação manual por hora")
    out()
    out(md(ph, index=False))
    out()
    return ok, ph


def main():
    out("# Liberação manual de eleitores (\"sem biometria\") — análise dedicada")
    out()
    out("O que é: quando a digital do eleitor falha 4 vezes, a urna pede um dado pessoal e exige a digital do mesário para "
        "liberar o voto. O BWeb conta esses casos no campo `QT_ELEI_BIOM_SEM_HABILITACAO` (8.632.488 no 2º turno). Os "
        "testes de efeito no voto estão em `RESULTADOS.md` (seção 5) e `PRIMEIRO_TURNO.md` (seção 5).")
    out()
    parte_planilhas()
    if os.path.exists(CACHE) and "--refazer" not in sys.argv:
        res = pd.read_csv(CACHE, dtype={"CD_MUNICIPIO": str, "NR_ZONA": str, "NR_SECAO": str})
    else:
        res = ler_logs()
    parte_logs(res)
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
