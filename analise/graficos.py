"""Gera os gráficos do README em docs/graficos/*.png. Todos os números vêm dos dados (nada digitado à mão).

    python3 analise/graficos.py            # todos
    python3 analise/graficos.py g3 g8      # só alguns
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from carregar import RAIZ, carregar, faixa_horario  # noqa: E402
from estatistica import ajustar, centrar, coef_cluster, especificacoes, junta_turnos, limite_tardias  # noqa: E402

PASTA = os.path.join(RAIZ, "docs", "graficos")
# Paleta validada (dataviz): azul = Lula, laranja = adversário, cinza = referência.
LULA, ADV, CINZA, TEXTO, TEXTO2, FUNDO = "#2a78d6", "#eb6834", "#8a8984", "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "savefig.facecolor": FUNDO,
    "axes.edgecolor": "#d6d5d0", "axes.labelcolor": TEXTO2, "xtick.color": TEXTO2, "ytick.color": TEXTO2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#ecebe7",
    "grid.linewidth": 0.8, "axes.axisbelow": True, "font.size": 10.5, "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.titlecolor": TEXTO, "axes.titlelocation": "left",
})
MARGEM = 4_430_191


def br(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mil(n):
    return f"{br(n / 1e6)} mi" if abs(n) >= 1e6 else f"{br(n / 1e3, 0)} mil"


def salvar(fig, nome):
    os.makedirs(PASTA, exist_ok=True)
    fig.savefig(os.path.join(PASTA, nome), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("ok", nome)


def titulo(fig, texto):
    fig.suptitle(texto, x=0.01, ha="left", fontsize=13, weight="bold", color=TEXTO, y=1.04)


ROT4 = ["até\n17:00:59", "17:01 a\n17:15", "17:16 a\n18:59", "19h ou\ndepois"]


def faixa4(serie):
    f = faixa_horario(serie).astype(str)
    return f.replace({"até 17:00:59": ROT4[0], "17:01 a 17:15:59": ROT4[1], "17:16 a 18:59:59": ROT4[2],
                      "19:00 a 19:59:59": ROT4[3], "20:00 ou depois": ROT4[3]})


def ler_logs_tardias():
    cache = os.path.join(RAIZ, "dados", "derivados", "logs_tardias_2t_2026.csv.gz")
    if not os.path.exists(cache):
        return None
    from logs_tardias import corrigir_fuso
    r = corrigir_fuso(pd.read_csv(cache, dtype={"CD_MUNICIPIO": str, "NR_ZONA": str, "NR_SECAO": str}))
    return r[r.grupo == "fechou 19h ou depois"]


def g1_duas_eleicoes(d26, d22):
    fig, eixos = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, (ano, d, adv) in zip(eixos, [(2026, d26, "Flávio"), (2022, d22, "Bolsonaro")]):
        g = d.assign(f=faixa4(d.ENC_LOCAL)).groupby("f").agg(s=("NR_SECAO", "size"), l=("V_13", "sum"), a=("V_22", "sum")).reindex(ROT4)
        p = g.l / (g.l + g.a) * 100
        x = np.arange(4)
        ax.bar(x, p, color=[LULA if v >= 50 else ADV for v in p], width=0.6)
        ax.axhline(50, color=TEXTO2, lw=1, ls="--")
        for i, (v, sal) in enumerate(zip(p, g.l - g.a)):
            ax.text(i, v + 1.2, f"{br(v)}%", ha="center", color=TEXTO, weight="bold")
            ax.text(i, v + 6, f"{'Lula' if sal > 0 else adv} +{mil(abs(sal))}", ha="center", color=TEXTO2, fontsize=8.5)
        ax.set_xticks(x, [f"{r}\n({br(s, 0)} seções)" for r, s in zip(ROT4, g.s)], fontsize=8.8)
        ax.set_ylim(0, 75)
        ax.set_title(f"{ano}: % de Lula por horário de fechamento")
    eixos[0].set_ylabel("% de Lula (entre os dois finalistas)")
    fig.supxlabel("horário de fechamento como gravado pela urna (relógio local), o mesmo corte do relatório",
                  color=TEXTO2, fontsize=10, y=-0.06)
    titulo(fig, "O corte do relatório também mostra \"duas eleições\" em 2022")
    salvar(fig, "01_duas_eleicoes_2026_vs_2022.png")


def g2_decomposicao(d, t1):
    seg = (d.ENC_LOCAL - d.ENC_LOCAL.dt.normalize()).dt.total_seconds()
    x = d.assign(v=d.V_13 + d.V_22, g=(seg < 17 * 3600 + 60).astype(float))
    x = x[x.v > 0]
    x["p"] = x.V_13 / x.v * 100
    mun = x.SG_UF + "-" + x.CD_MUNICIPIO.astype(str)
    barras = []
    for nome, fe in [("país todo\n(como o relatório)", None), ("dentro do\nmesmo estado", x.SG_UF),
                     ("dentro do\nmesmo município", mun)]:
        b, se = coef_cluster(centrar(x.p, fe), centrar(x.g, fe), mun, peso=x.v)
        barras.append((nome, b, se))
    k = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
    j = x[k + ["g"]].merge(t1[k + ["V_13", "V_22"]], on=k)
    pg = j[j.g == 1].V_13.sum() / (j[j.g == 1].V_13.sum() + j[j.g == 1].V_22.sum()) * 100
    pr = j[j.g == 0].V_13.sum() / (j[j.g == 0].V_13.sum() + j[j.g == 0].V_22.sum()) * 100
    barras.append(("as mesmas seções,\nno 1º turno", pg - pr, 0))
    fig, ax = plt.subplots(figsize=(10, 3.8))
    for i, (nome, b, se) in enumerate(barras):
        ax.bar(i, b, color=CINZA if i == 3 else ADV, width=0.55, yerr=1.96 * se if se else None, capsize=4, ecolor=TEXTO2)
        ax.text(i + 0.3, b / 2, f"{br(b, 2)} p.p.", ha="left", va="center", color=TEXTO, weight="bold")
    ax.axhline(0, color=TEXTO2, lw=1)
    ax.set_xticks(range(len(barras)), [b[0] for b in barras])
    ax.set_ylim(-7.8, 1)
    ax.set_ylabel("% de Lula no grupo \"até 17:00:59\"\nmenos no resto (p.p.)")
    ax.set_title("A diferença do grupo \"até 17h\" é geográfica: some na mesma cidade e já existia no 1º turno")
    salvar(fig, "02_grupo_ate_17h_decomposicao.png")


def g3_horarios(t1, t2, d22):
    fig, ax = plt.subplots(figsize=(11, 4.2))
    for nome, d, cor, ls in [("2º turno 2026", t2, LULA, "-"), ("1º turno 2026", t1, ADV, "-"), ("2º turno 2022", d22, CINZA, "--")]:
        m = d.ENC_BRASILIA.dt.hour * 60 + d.ENC_BRASILIA.dt.minute
        c = m[(m >= 16 * 60 + 50) & (m < 20 * 60)].value_counts().reindex(range(16 * 60 + 50, 20 * 60), fill_value=0)
        ax.plot(c.index, c.values.clip(min=0.8), color=cor, lw=2, ls=ls, label=nome)
    m2 = t2.ENC_BRASILIA.dt.hour * 60 + t2.ENC_BRASILIA.dt.minute
    pico17, pico19 = int((m2 == 17 * 60).sum()), int((m2 == 19 * 60).sum())
    ax.annotate(f"{br(pico17, 0)} seções\nfecharam às 17h00", (17 * 60, pico17), (17 * 60 + 25, pico17 * 0.5), color=TEXTO2,
                fontsize=9, arrowprops=dict(arrowstyle="-", color=TEXTO2))
    ax.annotate(f"pico do 2º turno:\n{br(pico19, 0)} seções às 19h00", (19 * 60, pico19), (19 * 60 + 22, 8), color=LULA,
                fontsize=9, arrowprops=dict(arrowstyle="-", color=LULA))
    ax.annotate("1º turno: filas (5 cargos),\nfechamentos espalhados", (18 * 60 + 15, 900), (17 * 60 + 40, 15000),
                color=ADV, fontsize=9, arrowprops=dict(arrowstyle="-", color=ADV))
    ax.set_yscale("log")
    ticks = list(range(17 * 60, 20 * 60 + 1, 30))
    ax.set_xticks(ticks, [f"{t // 60}h{t % 60:02d}" for t in ticks])
    ax.set_ylabel("seções que fecharam naquele minuto\n(escala logarítmica: cada linha = 10×)")
    ax.set_xlabel("horário de fechamento da urna (Brasília)")
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Pico de fechamentos às 19h00 só no 2º turno de 2026 (no 1º turno houve filas espalhadas, não pico)")
    salvar(fig, "03_horario_fechamento_por_minuto.png")


def g4_logs_tardias():
    t = ler_logs_tardias()
    if t is None:
        print("pulei g4 (rode logs_tardias.py)")
        return
    janelas = {}
    for s in t.por_minuto.dropna():
        for kv in str(s).split(";"):
            if ":" in kv:
                k, v = kv.split(":")
                janelas[int(k) // 15 * 15] = janelas.get(int(k) // 15 * 15, 0) + int(v)
    ks = list(range(17 * 60, 19 * 60 + 15, 15))
    vals = [janelas.get(k, 0) for k in ks]
    total = int(t.votos_log.sum())
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.bar(range(len(ks)), vals, color=LULA, width=0.7)
    for i, v in enumerate(vals):
        ax.text(i, v + 20, br(v, 0), ha="center", color=TEXTO, fontsize=9)
    ax.set_xticks(range(len(ks)), [f"{k // 60}h{k % 60:02d}" for k in ks], fontsize=9)
    ax.set_xlabel("janela de 15 minutos (Brasília), depois das 17h")
    ax.set_ylabel("votos computados")
    ax.set_title(f"Nas {br(len(t), 0)} seções abertas até 19h, só {br(t.votos_apos_17h00.sum(), 0)} de {br(total, 0)} votos "
                 f"({br(t.votos_apos_17h00.sum() / total * 100, 2)}%) foram dados depois das 17h")
    salvar(fig, "04_votos_depois_das_17h_nas_secoes_tardias.png")


def g5_modelo(m):
    prev, _, r2 = ajustar(m, "linear")
    _, _, r2m = ajustar(m, "linear", m.mun)
    fig, ax = plt.subplots(figsize=(6.5, 6))
    hb = ax.hexbin(prev, m.lula_2 * 100, gridsize=70, bins="log", cmap="Blues", mincnt=1, linewidths=0)
    ax.plot([0, 100], [0, 100], color=ADV, lw=1.5, ls="--", label="previsão perfeita")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("% de Lula previsto a partir do 1º turno da mesma seção")
    ax.set_ylabel("% de Lula real no 2º turno")
    ax.set_title(f"O 1º turno prevê o 2º, seção por seção\n(explica {br(r2 * 100)}% da variação; {br(r2m * 100)}% comparando "
                 "só seções da mesma cidade)", fontsize=11)
    ax.legend(frameon=False, loc="upper left")
    fig.colorbar(hb, ax=ax, label="nº de seções (escala log)")
    ax.grid(False)
    salvar(fig, "05_previsto_vs_real.png")


def g6_residuo(m):
    _, rn, _ = ajustar(m, "linear")
    _, rm, _ = ajustar(m, "linear", m.mun)
    grupos = {
        "fechou às 19h\nou depois": (m.ENC_BRASILIA_2 - m.ENC_BRASILIA_2.dt.normalize()).dt.total_seconds() >= 19 * 3600,
        "fechou até 17:00:59\n(corte do relatório)": (m.ENC_LOCAL_2 - m.ENC_LOCAL_2.dt.normalize()).dt.total_seconds() < 17 * 3600 + 60,
        "liberação manual\n≥ 20% da seção": m.bio_2 >= 0.2,
        "liberação manual\nsubiu > 5 p.p.\ndo 1º para o 2º": (m.bio_2 - m.bio_1) > 0.05,
    }
    fig, ax = plt.subplots(figsize=(11, 4.4))
    w = 0.36
    for i, (nome, mask) in enumerate(grupos.items()):
        for j, (r, fe, cor, rot) in enumerate([(rn, None, CINZA, "comparando com o país todo"),
                                               (rm, m.mun, LULA, "comparando só com seções da mesma cidade")]):
            b, se = coef_cluster(centrar(r, fe), centrar(mask.astype(float), fe), m.mun)
            xx = i + (j - 0.5) * w
            ax.bar(xx, b, width=w, color=cor, yerr=1.96 * se, capsize=3, ecolor=TEXTO2, label=rot if i == 0 else None)
            topo = b + 1.96 * se + 0.04 if b >= 0 else b - 1.96 * se - 0.04
            ax.text(xx, topo, f"{b:+.2f}".replace(".", ","), ha="center", va="bottom" if b >= 0 else "top", fontsize=9, color=TEXTO)
        ax.text(i, -1.05, f"{br(mask.sum(), 0)} seções", ha="center", fontsize=8.5, color=TEXTO2)
    ax.axhline(0, color=TEXTO2, lw=1)
    ax.set_xticks(range(len(grupos)), list(grupos))
    ax.set_ylim(-1.15, 1)
    ax.set_ylabel("% real de Lula − % prevista pelo\n1º turno (p.p.; + = mais Lula)")
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    ax.set_title("Nenhum grupo \"suspeito\" se afastou de forma relevante do que o 1º turno previa "
                 "(traço = margem de erro de 95%)", fontsize=11)
    salvar(fig, "06_desvio_por_grupo.png")


def g7_logs():
    from logs_urna import FUSO as F2, auditar
    fig, eixos = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    for ax, uf in zip(eixos, ["AC", "RR", "AP"]):
        _, horas, manuais, _ = auditar(uf)
        hs = sorted(h for h in horas if horas[h] >= 100)
        hb = [int(h) + F2.get(uf, 0) for h in hs]
        taxa = [manuais.get(h, 0) / horas[h] * 100 for h in hs]
        ax.plot(hb, taxa, color=LULA, lw=2, marker="o", ms=5)
        for h, t, hh in zip(hb, taxa, hs):
            if horas[hh] < 1000:
                ax.annotate(f"última hora:\nsó {horas[hh]} votos", (h, t), (h - 2.6, t + 1.2), fontsize=8, color=TEXTO2,
                            arrowprops=dict(arrowstyle="-", color=TEXTO2))
        ax.set_title(uf)
        ax.set_xticks(hb, [f"{h}h" for h in hb], fontsize=8.5)
        ax.set_ylim(0, 9.5)
        ax.set_xlabel("hora (Brasília)")
    eixos[0].set_ylabel("% dos votos daquela hora\nliberados manualmente")
    titulo(fig, "Pelos logs das urnas, a liberação manual é maior de manhã e cai ao longo do dia "
                "(a última hora tem poucos votos e oscila)")
    salvar(fig, "07_logs_liberacao_manual_por_hora.png")


def g8_margem(d, m):
    """Quanto da margem cada suspeita poderia explicar no pior caso — tudo calculado aqui."""
    seg = (d.ENC_BRASILIA - d.ENC_BRASILIA.dt.normalize()).dt.total_seconds()
    tarde = d[seg >= 19 * 3600]
    itens = [("Anular todas as seções que fecharam às 19h\n(saldo de Lula nelas)", int(tarde.V_13.sum() - tarde.V_22.sum()))]
    residuos = {n: ajustar(m, tipo, fe, p)[1] for n, (tipo, fe, p) in especificacoes(m).items()}
    rm = residuos["linear, dentro do município"]
    itens.append(("Seções das 19h: maior desvio estatístico\nplausível em relação ao 1º turno", limite_tardias(m, residuos)[1]))
    t = ler_logs_tardias()
    if t is not None:
        itens.append(("Seções das 19h: todos os votos dados\ndepois das 17h (pelos logs das urnas)", int(t.votos_apos_17h00.sum())))
    sd = rm.std()
    sel = rm.abs() > 4 * sd
    ef = (rm[sel] / 100) * m.loc[sel, "validos_2"] * 2
    itens.append(("Seções muito fora do padrão 1º→2º turno\n(soma só dos desvios a favor de Lula)", int(ef[ef > 0].sum())))
    doc = pd.read_csv(os.path.join(RAIZ, "analise", "secoes_para_documentar.csv"))
    sem = doc[doc.categoria.str.startswith(("7.", "10."))]
    itens.append(("Seções com urna sem explicação nos dados\n(todos os votos delas)", int(sem.QT_COMPARECIMENTO.sum())))
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    for i, (nome, v) in enumerate(itens):
        ax.barh(i, v, color=ADV, height=0.55)
        ax.text(v + MARGEM * 0.01, i, f"{br(v, 0)} votos ({br(v / MARGEM * 100)}% da margem)", va="center", color=TEXTO)
    ax.axvline(MARGEM, color=LULA, lw=2)
    ax.text(MARGEM * 0.99, 1.5, "margem de Lula: 4.430.191 →", ha="right", va="center", color=LULA, weight="bold")
    ax.set_yticks(range(len(itens)), [n for n, _ in itens], fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlim(0, MARGEM * 1.02)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1e6:.0f} mi"))
    ax.set_title("Quanto da margem cada suspeita poderia explicar, no pior caso")
    salvar(fig, "08_suspeitas_vs_margem.png")
    return itens


if __name__ == "__main__":
    so = sys.argv[1:]
    t2, t1, d22 = carregar(), carregar(turno=1), carregar(ano=2022)
    mm = junta_turnos() if (not so or {"g5", "g6", "g8"} & set(so)) else None
    for nome, f in [("g1", lambda: g1_duas_eleicoes(t2, d22)), ("g2", lambda: g2_decomposicao(t2, t1)),
                    ("g3", lambda: g3_horarios(t1, t2, d22)), ("g4", g4_logs_tardias), ("g5", lambda: g5_modelo(mm)),
                    ("g6", lambda: g6_residuo(mm)), ("g7", g7_logs), ("g8", lambda: print(g8_margem(t2, mm)))]:
        if not so or nome in so:
            f()
