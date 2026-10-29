"""Análise do 1º turno de 2026 e comparação seção a seção com o 2º turno. Gera analise/PRIMEIRO_TURNO.md.

Ideia central: a mesma seção, com os mesmos eleitores, votou duas vezes com 3 semanas de intervalo.
Um modelo de transferência de votos (2º turno explicado pelo 1º) mostra se algum grupo de seções
(fechamento tardio, muita liberação manual, etc.) se afastou do padrão no 2º turno."""
import os

import numpy as np
import pandas as pd

from carregar import FUSO, RAIZ, carregar

SAIDA = os.path.join(RAIZ, "analise", "PRIMEIRO_TURNO.md")
CHAVE = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
L = []


def out(s=""):
    L.append(s)


def fmt(n):
    return f"{n:,.0f}".replace(",", ".")


def md(df, idx=True):
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_integer_dtype(df[c]):
            df[c] = df[c].map(fmt)
    return df.to_markdown(index=idx, disable_numparse=True)


def faixas_horario(d, col):
    seg = (d[col] - d[col].dt.normalize()).dt.total_seconds()
    return pd.cut(seg, [0, 17 * 3600 + 61, 17 * 3600 + 16 * 60, 19 * 3600, 86400], right=False,
                  labels=["até 17:00:59", "17:01–17:15", "17:16–18:59", "19h ou depois"])


def main():
    t1 = carregar(turno=1)
    t2 = carregar(turno=2)
    votos1 = [c for c in t1 if c.startswith("V_") and c not in ("V_BRANCO", "V_NULO")]
    nominais1 = t1[votos1].sum().sort_values(ascending=False)
    comp1 = t1.QT_COMPARECIMENTO.sum()
    validos1 = nominais1.sum()

    out("# 1º turno de 2026 e comparação com o 2º turno")
    out()
    out("Fonte: BWeb do 1º turno (05/10/2026) e do 2º turno (25/10/2026), conferidos com o SHA-512 do TSE. Cargo: Presidente.")
    out()
    out("## 1. Resultado do 1º turno (soma dos BUs)")
    out()
    res = pd.DataFrame({"votos": nominais1.astype(int)})
    res["% válidos"] = (res.votos / validos1 * 100).round(2)
    res.index = [i.replace("V_", "nº ") for i in res.index]
    out(f"Seções: {fmt(len(t1))} · comparecimento: {fmt(comp1)} · válidos: {fmt(validos1)} · "
        f"brancos: {fmt(t1.V_BRANCO.sum())} · nulos: {fmt(t1.V_NULO.sum())}")
    out()
    out(md(res.head(8)))
    out()

    # ---------- horários e biometria nos dois turnos ----------
    out("## 2. Horário de fechamento e biometria nos dois turnos")
    out()
    linhas = []
    for nome, d in [("1º turno", t1), ("2º turno", t2)]:
        f = faixas_horario(d, "ENC_LOCAL").value_counts().reindex(
            ["até 17:00:59", "17:01–17:15", "17:16–18:59", "19h ou depois"])
        linhas.append({"turno": nome, "seções": len(d), **{f"fechou {k} (local)": int(v) for k, v in f.items()},
                       "fechou 19h+ (Brasília)": int((d.ENC_BRASILIA.dt.hour >= 19).sum()),
                       "liberação manual (biográfica)": int(d.QT_BIOM_SEM_HAB.sum()),
                       "% do comparecimento": round(d.QT_BIOM_SEM_HAB.sum() / d.QT_COMPARECIMENTO.sum() * 100, 2)})
    out(md(pd.DataFrame(linhas).set_index("turno")))
    out()

    # ---------- junção seção a seção ----------
    for d in (t1, t2):
        for c in ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]:
            d[c] = d[c].astype(int)
    m = t1.merge(t2, on=CHAVE, suffixes=("_1", "_2"))
    out("## 3. As mesmas seções nos dois turnos")
    out()
    out(f"- Seções presentes nos dois turnos: {fmt(len(m))} (1º: {fmt(len(t1))}, 2º: {fmt(len(t2))}).")
    out(f"- Aptos iguais nos dois turnos: {fmt((m.QT_APTOS_1 == m.QT_APTOS_2).sum())} "
        f"({(m.QT_APTOS_1 == m.QT_APTOS_2).mean() * 100:.1f}%). A diferença vem do voto em trânsito, que muda entre os turnos.")
    tarde2 = m.ENC_BRASILIA_2.dt.hour >= 19
    tarde1 = m.ENC_BRASILIA_1.dt.hour >= 19
    out(f"- Das {fmt(tarde2.sum())} seções que fecharam às 19h ou depois (Brasília) no 2º turno, "
        f"{fmt((tarde1 & tarde2).sum())} também fecharam às 19h ou depois no 1º turno.")
    bio1 = m.QT_BIOM_SEM_HAB_1 / m.QT_COMPARECIMENTO_1
    bio2 = m.QT_BIOM_SEM_HAB_2 / m.QT_COMPARECIMENTO_2
    out(f"- Correlação, por seção, entre a taxa de liberação manual no 1º e no 2º turno: **{np.corrcoef(bio1, bio2)[0, 1]:.2f}**. "
        "Se a taxa se repete, ela é uma característica da seção (eleitorado, leitor biométrico), não algo que apareceu no 2º turno.")
    out()

    # ---------- modelo de transferência ----------
    out("## 4. Modelo de transferência de votos: o 2º turno é previsível pelo 1º?")
    out()
    principais = list(nominais1.index[:6])
    outros = [c for c in votos1 if c not in principais]
    X = pd.DataFrame({c.replace("V_", "nº "): m[c + "_1"] if c + "_1" in m else m[c] for c in principais})
    X["outros"] = m[[c + "_1" if c + "_1" in m else c for c in outros]].sum(axis=1)
    X["branco+nulo"] = m.V_BRANCO_1 + m.V_NULO_1
    X["abstenção"] = m.QT_APTOS_1 - m.QT_COMPARECIMENTO_1
    X = X.div(m.QT_APTOS_1, axis=0)
    ok = (m.QT_APTOS_1 > 0) & ((m.V_13_2 + m.V_22_2) > 0)
    y = (m.V_13_2 / (m.V_13_2 + m.V_22_2))[ok]
    Xo = X[ok]
    # As fatias somam 100% dos aptos, então o intercepto seria redundante (colinearidade perfeita).
    A = Xo.values
    coef, *_ = np.linalg.lstsq(A, y.values, rcond=None)
    pred = A @ coef
    res_ = y.values - pred
    r2 = 1 - (res_ ** 2).sum() / ((y - y.mean()) ** 2).sum()
    # Mesmo modelo com efeito fixo de município (compara seções do mesmo município)
    Xd = Xo - Xo.groupby([m[ok].SG_UF, m[ok].CD_MUNICIPIO]).transform("mean")
    yd = y - y.groupby([m[ok].SG_UF, m[ok].CD_MUNICIPIO]).transform("mean")
    cd, *_ = np.linalg.lstsq(Xd.values, yd.values, rcond=None)
    rd = yd.values - Xd.values @ cd
    out(f"Variável prevista: % de Lula entre Lula e Flávio no 2º turno, por seção. Variáveis explicativas: votos "
        f"de cada candidato do 1º turno, branco+nulo e abstenção, como fração dos aptos. Seções: {fmt(ok.sum())}.")
    out()
    out(f"- **R² = {r2:.3f}**: o 1º turno explica {r2 * 100:.1f}% da variação do 2º turno entre seções.")
    out(f"- Erro típico (desvio-padrão do resíduo): {res_.std() * 100:.2f} pontos percentuais.")
    out()
    co = pd.Series(coef, index=Xo.columns).round(3).to_frame("coeficiente")
    out("Pesos do modelo. São pesos de previsão, não taxas exatas de transferência: o que importa é o sinal "
        "e a ordem. Eleitor de Lula e de Augusto Cury (70) puxa para Lula; eleitor de Flávio puxa contra.")
    out()
    out(md(co))
    out()

    mm = m[ok].assign(residuo=res_ * 100, residuo_mun=rd * 100)
    mm["fechamento 2º turno"] = faixas_horario(mm, "ENC_BRASILIA_2")
    mm["liberação manual 2º turno"] = pd.cut(bio2[ok], [-.01, .05, .1, .2, .3, 1.01],
                                             labels=["0–5%", "5–10%", "10–20%", "20–30%", "30–100%"])
    mm["variação liberação manual 1º→2º"] = pd.cut((bio2 - bio1)[ok], [-1.01, -.05, .05, .1, 1.01],
                                                    labels=["caiu >5 p.p.", "estável (±5 p.p.)", "subiu 5–10 p.p.", "subiu >10 p.p."])
    out("### Resíduo por grupo de seções")
    out()
    out("Resíduo = % real de Lula no 2º turno menos o previsto pelo 1º turno, em pontos percentuais. Se a virada "
        "tivesse sido \"fabricada\" em algum grupo, o resíduo desse grupo seria claramente positivo. A coluna "
        "\"dentro do município\" compara só seções do mesmo município, o que neutraliza diferenças regionais.")
    out()
    for col in ["fechamento 2º turno", "liberação manual 2º turno", "variação liberação manual 1º→2º"]:
        t = mm.groupby(col, observed=True).agg(secoes=("residuo", "size"), residuo_medio=("residuo", "mean"),
                                               dentro_do_municipio=("residuo_mun", "mean"))
        t[["residuo_medio", "dentro_do_municipio"]] = t[["residuo_medio", "dentro_do_municipio"]].round(2)
        out(f"**{col}**")
        out()
        out(md(t))
        out()
    sd = mm.residuo_mun.std()
    ext = mm[mm.residuo_mun.abs() > 4 * sd]
    out(f"- Seções com resíduo dentro do município acima de 4 desvios-padrão ({4 * sd:.1f} p.p.): {fmt(len(ext))} "
        f"({len(ext) / len(mm) * 100:.2f}%), sendo {fmt((ext.residuo_mun > 0).sum())} a favor de Lula e "
        f"{fmt((ext.residuo_mun < 0).sum())} a favor de Flávio.")
    impacto = ((ext.residuo_mun / 100) * (ext.V_13_2 + ext.V_22_2) * 2).sum()
    out(f"- Mesmo atribuindo todo o resíduo dessas seções a manipulação, o efeito líquido na margem seria de "
        f"{fmt(impacto)} votos, contra uma margem de {fmt(t2.V_13.sum() - t2.V_22.sum())}.")
    ext[CHAVE + ["NM_MUNICIPIO_2", "QT_COMPARECIMENTO_2", "V_13_2", "V_22_2", "residuo", "residuo_mun"]].sort_values(
        "residuo_mun").to_csv(os.path.join(RAIZ, "analise", "secoes_fora_do_padrao_1t_2t.csv"), index=False)
    out("- A lista dessas seções está em `secoes_fora_do_padrao_1t_2t.csv`.")
    out()

    # ---------- por UF ----------
    out("## 5. Do 1º para o 2º turno, por UF")
    out()
    u1 = t1.groupby("SG_UF")[["V_13", "V_22", "QT_COMPARECIMENTO"]].sum()
    u1["validos"] = t1.groupby("SG_UF")[votos1].sum().sum(axis=1)
    u2 = t2.groupby("SG_UF")[["V_13", "V_22", "QT_COMPARECIMENTO"]].sum()
    uf = pd.DataFrame({
        "Lula 1º (% válidos)": (u1.V_13 / u1.validos * 100).round(1),
        "Flávio 1º (% válidos)": (u1.V_22 / u1.validos * 100).round(1),
        "Lula 2º (% válidos)": (u2.V_13 / (u2.V_13 + u2.V_22) * 100).round(1),
        "comparecimento 1º": u1.QT_COMPARECIMENTO.astype(int), "comparecimento 2º": u2.QT_COMPARECIMENTO.astype(int)})
    uf["previsto pelo modelo"] = (mm.assign(p=pred).groupby("SG_UF").apply(
        lambda x: np.average(x.p, weights=x.V_13_2 + x.V_22_2)) * 100).round(1)
    out(md(uf))
    out()

    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
