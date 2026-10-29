"""Gera os gráficos do README em docs/graficos/*.png.

    python3 analise/graficos.py
"""
import os
from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from carregar import FUSO, RAIZ, carregar  # noqa: E402

PASTA = os.path.join(RAIZ, "docs", "graficos")
# Paleta: azul = Lula, laranja = adversário (Flávio em 2026, Jair em 2022), cinza = referência.
LULA, ADV, CINZA, TEXTO, TEXTO2, FUNDO = "#2a78d6", "#eb6834", "#8a8984", "#0b0b0b", "#52514e", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "savefig.facecolor": FUNDO,
    "axes.edgecolor": "#d6d5d0", "axes.labelcolor": TEXTO2, "xtick.color": TEXTO2, "ytick.color": TEXTO2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#ecebe7",
    "grid.linewidth": 0.8, "axes.axisbelow": True, "font.size": 10.5, "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.titlecolor": TEXTO, "axes.titlelocation": "left",
})
H = lambda h, m=0: h * 3600 + m * 60  # noqa: E731
FAIXAS = [0, H(17, 1), H(17, 16), H(19), 86400]
ROTULOS = ["até\n17:00:59", "17:01 a\n17:15", "17:16 a\n18:59", "19h ou\ndepois"]


def salvar(fig, nome):
    os.makedirs(PASTA, exist_ok=True)
    fig.savefig(os.path.join(PASTA, nome), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("ok", nome)


def faixa(d, col):
    seg = (d[col] - d[col].dt.normalize()).dt.total_seconds()
    return pd.cut(seg, FAIXAS, right=False, labels=ROTULOS)


def mil(n):
    return f"{n / 1e6:.1f} mi".replace(".", ",") if abs(n) >= 1e6 else f"{n / 1e3:.0f} mil"


def g1_duas_eleicoes(d26, d22):
    """O corte por horário do relatório, em 2026 e em 2022."""
    fig, eixos = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, (ano, d, adv) in zip(eixos, [(2026, d26, "Flávio"), (2022, d22, "Bolsonaro")]):
        g = d.assign(f=faixa(d, "ENC_LOCAL")).groupby("f", observed=False).agg(
            s=("NR_SECAO", "size"), l=("V_13", "sum"), a=("V_22", "sum"))
        pct = g.l / (g.l + g.a) * 100
        cores = [LULA if p >= 50 else ADV for p in pct]
        x = np.arange(len(g))
        ax.bar(x, pct, color=cores, width=0.6)
        ax.axhline(50, color=TEXTO2, lw=1, ls="--")
        for i, (p, s, sal) in enumerate(zip(pct, g.s, g.l - g.a)):
            quem = "Lula" if sal > 0 else adv
            ax.text(i, p + 1.2, f"{p:.1f}%".replace(".", ","), ha="center", color=TEXTO, fontsize=10, weight="bold")
            ax.text(i, p + 6, f"{quem} +{mil(abs(sal))}", ha="center", color=TEXTO2, fontsize=8.5)
        rot = [f"{r}\n({s:,} seções)".replace(",", ".") for r, s in zip(ROTULOS, g.s)]
        ax.set_xticks(x, rot, fontsize=8.8)
        ax.set_ylim(0, 75)
        ax.set_title(f"{ano}: % de Lula por horário de fechamento")
    fig.supxlabel("horário de fechamento da urna (relógio local, como o relatório usa)", color=TEXTO2, fontsize=10, y=-0.06)
    eixos[0].set_ylabel("% dos votos válidos para Lula")
    fig.suptitle("O mesmo corte do relatório mostra \"duas eleições\" também em 2022",
                 x=0.01, ha="left", fontsize=13, weight="bold", color=TEXTO, y=1.04)
    salvar(fig, "01_duas_eleicoes_2026_vs_2022.png")


def g2_fuso(d26):
    """Quem está no grupo 'até 17:00:59': os estados a oeste dominam."""
    seg = (d26.ENC_LOCAL - d26.ENC_LOCAL.dt.normalize()).dt.total_seconds()
    cedo = d26[seg < H(17, 1)]
    oeste = cedo.SG_UF.isin(FUSO)
    fig, ax = plt.subplots(figsize=(9, 3.2))
    grupos = [("estados com fuso a oeste\n(AC, AM, MT, MS, RO, RR)", cedo[oeste]),
              ("demais estados\n(seções que fecharam no 1º minuto)", cedo[~oeste])]
    for i, (nome, g) in enumerate(grupos):
        p = g.V_13.sum() / (g.V_13.sum() + g.V_22.sum()) * 100
        ax.barh(i, p, color=LULA, height=0.55)
        ax.barh(i, 100 - p, left=p, color=ADV, height=0.55)
        ax.text(p / 2, i, f"Lula {p:.0f}%", ha="center", va="center", color="white", weight="bold")
        ax.text(p + (100 - p) / 2, i, f"Flávio {100 - p:.0f}%", ha="center", va="center", color="white", weight="bold")
        ax.text(101, i, f"{len(g):,} seções".replace(",", "."), va="center", color=TEXTO2)
    ax.set_yticks([0, 1], [n for n, _ in grupos])
    ax.set_xlim(0, 118)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.invert_yaxis()
    ax.grid(False)
    ax.set_title("Grupo \"até 17:00:59\" de 2026: os estados a oeste puxam para Flávio")
    ax.set_xlabel("% dos votos válidos")
    salvar(fig, "02_grupo_ate_17h_composicao.png")


def g3_horarios(t1, t2, d22):
    """Distribuição do horário de fechamento (Brasília), minuto a minuto."""
    fig, ax = plt.subplots(figsize=(11, 4))
    series = [("2º turno 2026", t2, LULA, "-"), ("1º turno 2026", t1, ADV, "-"), ("2º turno 2022", d22, CINZA, "--")]
    for nome, d, cor, ls in series:
        m = (d.ENC_BRASILIA.dt.hour * 60 + d.ENC_BRASILIA.dt.minute)
        c = m[(m >= 16 * 60 + 50) & (m < 20 * 60)].value_counts().sort_index()
        c = c.reindex(range(16 * 60 + 50, 20 * 60), fill_value=0)
        ax.plot(c.index, c.values.clip(min=0.8), color=cor, lw=2, ls=ls, label=nome)
    ax.set_yscale("log")
    ticks = list(range(17 * 60, 20 * 60 + 1, 30))
    ax.set_xticks(ticks, [f"{t // 60}h{t % 60:02d}" for t in ticks])
    ax.set_ylabel("seções que fecharam naquele minuto\n(escala logarítmica)")
    ax.set_xlabel("horário de fechamento da urna (Brasília)")
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("No 2º turno de 2026 há um pico de fechamentos às 19h00, que não existe no 1º turno nem em 2022")
    salvar(fig, "03_horario_fechamento_por_minuto.png")


def g4_biometria(t2):
    """% de liberação manual × % Lula, por seção."""
    v = t2.V_13 + t2.V_22
    x = (t2.QT_BIOM_SEM_HAB / t2.QT_COMPARECIMENTO * 100)[v > 0]
    y = (t2.V_13 / v * 100)[v > 0]
    fig, ax = plt.subplots(figsize=(9, 5))
    hb = ax.hexbin(x.clip(upper=40), y, gridsize=60, bins="log", cmap="Blues", mincnt=1, linewidths=0)
    fig.colorbar(hb, ax=ax, label="nº de seções (escala log)")
    r = np.corrcoef(x, y)[0, 1]
    ax.set_xlabel("% de eleitores liberados manualmente na seção (digital falhou; 40 = 40% ou mais)")
    ax.set_ylabel("% de Lula na seção (2º turno)")
    ax.set_title(f"Liberação manual não acompanha o voto em Lula (correlação = {r:.2f})".replace(".", ","))
    ax.grid(False)
    salvar(fig, "04_biometria_vs_voto.png")


def g5_modelo(t1, t2):
    """Previsto pelo 1º turno × real no 2º, e resíduo por grupo."""
    import primeiro_turno as pt  # reaproveita o modelo
    for d in (t1, t2):
        for c in ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]:
            d[c] = d[c].astype(int)
    m = t1.merge(t2, on=pt.CHAVE, suffixes=("_1", "_2"))
    votos1 = [c for c in t1 if c.startswith("V_") and c not in ("V_BRANCO", "V_NULO")]
    princ = list(t1[votos1].sum().sort_values(ascending=False).index[:6])
    um = lambda c: c + "_1" if c + "_1" in m else c  # noqa: E731  (colunas só do 1º turno não têm sufixo)
    X = pd.DataFrame({c: m[um(c)] for c in princ})
    X["outros"] = m[[um(c) for c in votos1 if c not in princ]].sum(axis=1)
    X["bn"] = m.V_BRANCO_1 + m.V_NULO_1
    X["abst"] = m.QT_APTOS_1 - m.QT_COMPARECIMENTO_1
    X = X.div(m.QT_APTOS_1, axis=0)
    ok = (m.QT_APTOS_1 > 0) & ((m.V_13_2 + m.V_22_2) > 0)
    y = (m.V_13_2 / (m.V_13_2 + m.V_22_2))[ok].values
    A = X[ok].values
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()

    fig, ax = plt.subplots(figsize=(6.5, 6))
    hb = ax.hexbin(pred * 100, y * 100, gridsize=70, bins="log", cmap="Blues", mincnt=1, linewidths=0)
    ax.plot([0, 100], [0, 100], color=ADV, lw=1.5, ls="--", label="previsão perfeita")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("% de Lula previsto a partir do 1º turno da mesma seção")
    ax.set_ylabel("% de Lula real no 2º turno")
    ax.set_title(f"O 1º turno prevê o 2º seção a seção (R² = {r2:.3f})".replace(".", ","))
    ax.legend(frameon=False, loc="upper left")
    fig.colorbar(hb, ax=ax, label="nº de seções (escala log)")
    ax.grid(False)
    salvar(fig, "05_previsto_vs_real.png")

    mm = m[ok].copy()
    res = (y - pred) * 100
    chave_mun = [mm.SG_UF, mm.CD_MUNICIPIO]
    Xd = X[ok] - X[ok].groupby(chave_mun).transform("mean")
    yd = pd.Series(y, index=mm.index)
    yd = yd - yd.groupby(chave_mun).transform("mean")
    cd, *_ = np.linalg.lstsq(Xd.values, yd.values, rcond=None)
    mm["res_mun"] = (yd.values - Xd.values @ cd) * 100
    mm["f"] = faixa(mm, "ENC_BRASILIA_2")
    bio = mm.QT_BIOM_SEM_HAB_2 / mm.QT_COMPARECIMENTO_2
    mm["b"] = pd.cut(bio, [-.01, .05, .1, .2, 1.01], labels=["0–5%", "5–10%", "10–20%", "20%+"])
    fig, eixos = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    for ax, col, tit in [(eixos[0], "f", "por horário de fechamento (Brasília)"),
                         (eixos[1], "b", "por % de liberação manual na seção")]:
        g = mm.groupby(col, observed=True).res_mun.agg(["mean", "size"])
        ax.bar(range(len(g)), g["mean"], color=[LULA if v > 0 else ADV for v in g["mean"]], width=0.55)
        ax.axhline(0, color=TEXTO2, lw=1)
        for i, (v, n) in enumerate(zip(g["mean"], g["size"])):
            ax.text(i, v + (0.03 if v >= 0 else -0.03), f"{v:+.2f}".replace(".", ","), ha="center",
                    va="bottom" if v >= 0 else "top", color=TEXTO, fontsize=9.5, weight="bold")
            ax.text(i, -0.48, f"{n:,} seções".replace(",", "."), ha="center", color=TEXTO2, fontsize=8)
        ax.set_xticks(range(len(g)), [str(i).replace("\n", " ") for i in g.index], fontsize=9)
        ax.set_ylim(-0.55, 0.55)
        ax.set_title(tit, fontsize=11)
    eixos[0].set_ylabel("diferença real − previsto\n(pontos percentuais; + = mais Lula)")
    fig.suptitle("Nenhum grupo de seções se desviou a favor de Lula em relação ao próprio 1º turno",
                 x=0.01, ha="left", fontsize=13, weight="bold", color=TEXTO, y=1.04)
    salvar(fig, "06_residuo_por_grupo.png")


def g7_logs():
    """Votos e liberações manuais por hora, a partir dos logs das urnas."""
    from logs_urna import FUSO as F2, auditar
    fig, eixos = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    for ax, uf in zip(eixos, ["AC", "RR", "AP"]):
        _, horas, manuais, _ = auditar(uf)
        hs = sorted(h for h in horas if horas[h] > 1000)
        hb = [int(h) + F2.get(uf, 0) for h in hs]
        taxa = [manuais.get(h, 0) / horas[h] * 100 for h in hs]
        ax.plot(hb, taxa, color=LULA, lw=2, marker="o", ms=5)
        ax.set_title(uf)
        ax.set_xticks(hb, [f"{h}h" for h in hb], fontsize=8.5)
        ax.set_ylim(0, 8)
        ax.set_xlabel("hora (Brasília)")
    eixos[0].set_ylabel("% dos votos daquela hora\nliberados manualmente")
    fig.suptitle("Pelos logs das urnas, a liberação manual cai ao longo do dia; não há pico no fim da votação",
                 x=0.01, ha="left", fontsize=13, weight="bold", color=TEXTO, y=1.05)
    salvar(fig, "07_logs_liberacao_manual_por_hora.png")


def g8_margem():
    """Quanto da margem cada 'suspeita' poderia explicar, no pior caso."""
    margem = 4_430_191
    itens = [
        ("Seções que fecharam às 19h ou depois\n(saldo líquido de Lula nelas)", 186_954),
        ("Seções com urna/carga fora da lista prévia\n(saldo líquido de Lula nelas)", 4_835),
        ("Seções fora do padrão 1º→2º turno\n(efeito líquido, se tudo fosse fraude)", 3_487),
    ]
    fig, ax = plt.subplots(figsize=(10, 3.4))
    for i, (nome, v) in enumerate(itens):
        ax.barh(i, v, color=ADV, height=0.55)
        ax.text(v + margem * 0.01, i, f"{v:,} votos ({v / margem * 100:.1f}% da margem)".replace(",", "X").replace(".", ",").replace("X", "."),
                va="center", color=TEXTO)
    ax.axvline(margem, color=LULA, lw=2)
    ax.text(margem * 0.99, 1.5, "margem de Lula: 4.430.191 →", ha="right", va="center", color=LULA, weight="bold")
    ax.set_yticks(range(len(itens)), [n for n, _ in itens], fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlim(0, margem * 1.02)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1e6:.0f} mi"))
    ax.set_title("Mesmo no pior caso, cada suspeita explica uma fração pequena da margem")
    salvar(fig, "08_suspeitas_vs_margem.png")


if __name__ == "__main__":
    import sys
    so = sys.argv[1:]
    t2 = carregar()
    t1 = carregar(turno=1)
    d22 = carregar(ano=2022)
    for nome, f in [("g1", lambda: g1_duas_eleicoes(t2, d22)), ("g2", lambda: g2_fuso(t2)),
                    ("g3", lambda: g3_horarios(t1, t2, d22)), ("g4", lambda: g4_biometria(t2)),
                    ("g5", lambda: g5_modelo(t1, t2)), ("g7", g7_logs), ("g8", g8_margem)]:
        if not so or nome in so:
            f()
