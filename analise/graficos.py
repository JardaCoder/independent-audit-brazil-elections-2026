"""Gera os gráficos do README em docs/graficos/*.png. Todos os números vêm dos dados (nada digitado à mão).

    python3 analise/graficos.py            # todos
    python3 analise/graficos.py g3 g8      # só alguns
"""
import os
import sys
from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from biometria import por_hora  # noqa: E402
from carregar import RAIZ, carregar, faixa_horario  # noqa: E402
from estatistica import (CHAVE, ajustar, centrar, coef_cluster, especificacoes, junta_turnos,  # noqa: E402
                         limite_tardias)

PASTA = os.path.join(RAIZ, "docs", "graficos")
# Cores dos partidos: vermelho = Lula, azul = adversário; cinza = referência.
LULA, ADV, CINZA, TEXTO, TEXTO2, FUNDO = "#d1302b", "#2a78d6", "#8a8984", "#0b0b0b", "#52514e", "#fcfcfb"
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
    fig.supxlabel("horário de fechamento como gravado pela urna (relógio local)",
                  color=TEXTO2, fontsize=10, y=-0.06)
    titulo(fig, "O corte por horário local também mostra \"duas eleições\" em 2022")
    salvar(fig, "01_duas_eleicoes_2026_vs_2022.png")


def g2_decomposicao(d, t1):
    seg = (d.ENC_LOCAL - d.ENC_LOCAL.dt.normalize()).dt.total_seconds()
    x = d.assign(v=d.V_13 + d.V_22, g=(seg < 17 * 3600 + 60).astype(float))
    x = x[x.v > 0]
    x["p"] = x.V_13 / x.v * 100
    mun = x.SG_UF + "-" + x.CD_MUNICIPIO.astype(str)
    barras = []
    for nome, fe in [("país todo\n(sem controle)", None), ("dentro do\nmesmo estado", x.SG_UF),
                     ("dentro do\nmesmo município", mun)]:
        b, se = coef_cluster(centrar(x.p, fe), centrar(x.g, fe), mun, peso=x.v)
        barras.append((nome, b, se))
    j = x[CHAVE + ["g"]].merge(t1[CHAVE + ["V_13", "V_22"]], on=CHAVE)
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
        "fechou até 17:00:59\n(relógio local)": (m.ENC_LOCAL_2 - m.ENC_LOCAL_2.dt.normalize()).dt.total_seconds() < 17 * 3600 + 60,
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


def g9_biometria_estados(t2):
    d = t2[t2.SG_UF != "ZZ"]
    g = d.groupby("SG_UF")[["QT_BIOM_SEM_HAB", "QT_COMPARECIMENTO", "V_13", "V_22"]].sum()
    taxa = g.QT_BIOM_SEM_HAB / g.QT_COMPARECIMENTO * 100
    lula = g.V_13 / (g.V_13 + g.V_22) * 100
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.scatter(taxa, lula, s=g.QT_COMPARECIMENTO / 2e4, color=[LULA if v >= 50 else ADV for v in lula], alpha=0.85,
               edgecolor=FUNDO, linewidth=1.5)
    for uf in g.index:
        ax.annotate(uf, (taxa[uf], lula[uf]), (5, 3), textcoords="offset points", fontsize=8.5, color=TEXTO2)
    ax.axhline(50, color=TEXTO2, lw=1, ls="--")
    ax.set_xlabel("% dos eleitores liberados manualmente (digital falhou), 2º turno")
    ax.set_ylabel("% de Lula (entre os dois finalistas)")
    ax.set_title("Liberação manual por estado: alta tanto onde Lula venceu (PI, BA)\n"
                 "quanto onde Flávio venceu (RS, SC). Tamanho do círculo = nº de votantes", fontsize=11)
    salvar(fig, "09_biometria_por_estado.png")


def g10_biometria_por_hora():
    cache = os.path.join(RAIZ, "dados", "derivados", "biometria_logs_2t_2026.csv.gz")
    if not os.path.exists(cache):
        print("pulei g10 (rode biometria.py)")
        return
    r = pd.read_csv(cache)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    estilos = {"amostra aleatória do Brasil": (CINZA, "-"), "fechou 19h ou depois": (LULA, "-"),
               "vizinha que fechou até 17h15": (ADV, "--")}
    for grupo, (cor, ls) in estilos.items():
        x = r[r.grupo == grupo]
        cont, tot = por_hora(x.por_hora), Counter()
        for (h, _), n in cont.items():
            tot[h] += n
        man = {h: n for (h, tp), n in cont.items() if tp == "manual"}
        hs = [h for h in sorted(tot) if 8 <= h <= 18 and tot[h] >= 200]
        ax.plot(hs, [man.get(h, 0) / tot[h] * 100 for h in hs], color=cor, ls=ls, lw=2, marker="o", ms=4,
                label=f"{grupo} ({br(len(x), 0)} seções)")
    ax.set_xticks(range(8, 19), [f"{h}h" for h in range(8, 19)])
    ax.set_ylim(0, 10)
    ax.set_xlabel("hora do voto (Brasília), pelo log de cada urna")
    ax.set_ylabel("% dos votos daquela hora\nliberados manualmente")
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.set_title("A liberação manual é maior de manhã em todos os grupos; não sobe no horário estendido "
                 "(horas com ≥ 200 votos)", fontsize=11)
    salvar(fig, "10_liberacao_manual_por_hora_logs.png")


# Municípios cujo nome no TSE difere do IBGE (grafia antiga ou variante). Chave: (UF, nome no TSE).
NOME_IBGE = {("GO", "BOM JESUS"): "Bom Jesus de Goiás", ("MG", "BARÃO DE MONTE ALTO"): "Barão do Monte Alto",
             ("MG", "DONA EUSÉBIA"): "Dona Euzébia", ("MG", "SÃO THOMÉ DAS LETRAS"): "São Tomé das Letras",
             ("MT", "SANTO ANTÔNIO DO LEVERGER"): "Santo Antônio de Leverger",
             ("PA", "ELDORADO DOS CARAJÁS"): "Eldorado do Carajás", ("PR", "MUNHOZ DE MELLO"): "Munhoz de Melo",
             ("RN", "BOA SAÚDE"): "Januário Cicco", ("RO", "ESPIGÃO DO OESTE"): "Espigão D'Oeste",
             ("RO", "ALVORADA DO OESTE"): "Alvorada D'Oeste", ("RR", "SÃO LUIZ"): "São Luiz do Anauá",
             ("SE", "AMPARO DE SÃO FRANCISCO"): "Amparo do São Francisco",
             ("SP", "SÃO LUÍS DO PARAITINGA"): "São Luiz do Paraitinga"}


def malha(nome):
    import geopandas as gpd
    return gpd.read_file("/vsigzip/" + os.path.join(RAIZ, "dados", "ibge", nome))


def malha_uf():
    ufs = malha("malha_uf.json.gz")
    sigla = pd.read_json(os.path.join(RAIZ, "dados", "ibge", "municipios.json.gz")).drop_duplicates("UF-id")
    return ufs.assign(SG_UF=ufs.codarea.astype(int).map(dict(zip(sigla["UF-id"], sigla["UF-sigla"]))))


def pct_disputa(d, chave):
    """% de Lula entre os votos dos dois finalistas (Lula + Flávio), por `chave`; exterior fora."""
    g = d[d.SG_UF != "ZZ"].groupby(chave)[["V_13", "V_22"]].sum()
    return g.V_13 / (g.V_13 + g.V_22) * 100


def sinal(x):
    return f"{'+' if x >= 0 else '−'}{br(abs(x))}"


def enquadrar(ax, oeste=-74.2, leste=-34.6):
    ax.set_xlim(oeste, leste)  # corta Fernando de Noronha, que deixaria o mapa encolhido
    ax.set_ylim(-34, 5.5)
    ax.set_axis_off()


# Estados pequenos: rótulo fora do contorno, ligado por uma linha (lon, lat do rótulo).
ROTULO_FORA = {"RN": (-33.4, -4.4), "PB": (-32.6, -6.6), "PE": (-32.6, -8.6), "AL": (-33.4, -10.4),
               "SE": (-35.0, -12.4), "ES": (-36.6, -20.6), "RJ": (-39.6, -24.6), "DF": (-43.6, -16.4)}


def rotular(ax, g, norm, tamanho=7.5, com_uf=True):
    for _, r in g.iterrows():
        texto = f"{r.SG_UF}\n{sinal(r['var'])}" if com_uf else sinal(r["var"])
        p = r.geometry.representative_point()
        if r.SG_UF in ROTULO_FORA:
            ax.annotate(texto, (p.x, p.y), ROTULO_FORA[r.SG_UF], fontsize=tamanho * 0.85, ha="center", va="center",
                        color=TEXTO, arrowprops=dict(arrowstyle="-", color=TEXTO2, lw=0.6))
        else:
            escuro = norm(r["var"]) > 0.6
            ax.text(p.x, p.y, texto, fontsize=tamanho, ha="center", va="center", weight="bold",
                    color="white" if escuro else TEXTO)


def g11_mapa_municipios(t1, t2):
    """Quem ganhou terreno na disputa direta, por município: variação da % de Lula entre Lula e Flávio."""
    import unicodedata

    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

    def chave(uf, nome):
        s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().upper()
        return uf + "".join(ch for ch in s if ch.isalpha())

    k = ["SG_UF", "NM_MUNICIPIO"]
    mun = (pct_disputa(t2, k) - pct_disputa(t1, k)).rename("var").reset_index()
    ibge = pd.read_json(os.path.join(RAIZ, "dados", "ibge", "municipios.json.gz"))
    cod = dict(zip([chave(u, n) for u, n in zip(ibge["UF-sigla"], ibge["municipio-nome"])], ibge["municipio-id"]))
    mun["codarea"] = [cod.get(chave(u, NOME_IBGE.get((u, n), n))) for u, n in zip(mun.SG_UF, mun.NM_MUNICIPIO)]
    assert mun.codarea.notna().all(), mun[mun.codarea.isna()]
    mun["codarea"] = mun.codarea.astype(int).astype(str)
    geo = malha("malha_municipios.json.gz").merge(mun, on="codarea")
    # A malha do IBGE ainda não tem Boa Esperança do Norte (MT, instalado em 2025); a área fica em Sorriso e Nova Ubiratã.
    assert mun[~mun.codarea.isin(geo.codarea)].codarea.tolist() == ["5101837"]

    norm = TwoSlopeNorm(vmin=-6, vcenter=0, vmax=6)
    cmap = LinearSegmentedColormap.from_list("disputa", ["#163f75", ADV, "#f4f3ef", LULA, "#7a1512"])
    fig, ax = plt.subplots(figsize=(8, 8.8), layout="constrained")
    geo.plot(column="var", cmap=cmap, norm=norm, ax=ax, linewidth=0)
    malha_uf().boundary.plot(ax=ax, color=TEXTO2, linewidth=0.5)
    enquadrar(ax)
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), ax=ax, orientation="horizontal", fraction=0.035,
                      pad=0.01, extend="both", shrink=0.8)
    cb.set_label("← Flávio ganhou terreno · variação da % de Lula entre os dois, em p.p. · Lula ganhou terreno →",
                 color=TEXTO2)
    cb.outline.set_visible(False)
    n_flavio = int((mun["var"] < 0).sum())
    fig.suptitle(f"Lula ganhou terreno sobre Flávio em {br(len(mun) - n_flavio, 0)} dos {br(len(mun), 0)} municípios",
                 x=0.02, ha="left", fontsize=13, weight="bold", color=TEXTO)
    ax.set_title(f"Mediana dos municípios: {sinal(mun['var'].median())} p.p. Em azul, os {n_flavio} em que Flávio "
                 "avançou.", fontsize=10.5, weight="normal", loc="left", color=TEXTO2)
    cb.ax.text(0, -3.4, "Malha municipal do IBGE. Boa Esperança do Norte (MT), criado em 2025, ainda não tem polígono\n"
               "e aparece dentro dos municípios de origem. Fernando de Noronha fora do recorte.",
               transform=cb.ax.transAxes, fontsize=8, color=TEXTO2)
    salvar(fig, "11_mapa_municipios_disputa.png")
    return mun


def g12_mapa_estados_disputa(t1, t2):
    """Quanto Lula ganhou de terreno sobre Flávio em cada estado (variação da % de Lula entre os dois)."""
    from matplotlib.colors import LinearSegmentedColormap, Normalize

    var = pct_disputa(t2, "SG_UF") - pct_disputa(t1, "SG_UF")
    br1 = pct_disputa(t1.assign(X=0), "X").iloc[0]
    br2 = pct_disputa(t2.assign(X=0), "X").iloc[0]
    g = malha_uf().assign(var=lambda u: u.SG_UF.map(var))
    norm = Normalize(0, 5)
    cmap = LinearSegmentedColormap.from_list("lula", ["#f4f3ef", "#f2a59c", LULA, "#7a1512"])
    fig, ax = plt.subplots(figsize=(8.5, 9), layout="constrained")
    g.plot(column="var", cmap=cmap, norm=norm, ax=ax, edgecolor="white", linewidth=1)
    rotular(ax, g, norm, tamanho=10)
    enquadrar(ax, leste=-31.5)
    fig.suptitle("Do 1º para o 2º turno, Lula ganhou terreno\nsobre Flávio em todos os estados", x=0.5, ha="center",
                 fontsize=16, weight="bold", color=TEXTO)
    ax.set_title(f"Variação da % de Lula entre os votos dos dois, em pontos percentuais. "
                 f"Brasil: {br(br1)}% → {br(br2)}% ({sinal(br2 - br1)} p.p.)", fontsize=10, weight="normal",
                 color=TEXTO2)
    mx, mn = var.idxmax(), var.idxmin()
    ax.text(-73.5, -29.5, f"Lula avançou mais em {mx} ({sinal(var[mx])}) e\nmenos em {mn} ({sinal(var[mn])}), "
            f"onde já tinha\n{br(pct_disputa(t1, 'SG_UF')[mn], 0)}% no 1º turno.", fontsize=9, color=TEXTO2,
            bbox=dict(boxstyle="square,pad=0.6", fc=FUNDO, ec=CINZA, lw=0.8))
    fig.text(0.02, -0.01, "Exterior fora. Malha: IBGE.", fontsize=8, color=TEXTO2)
    salvar(fig, "12_mapa_estados_disputa.png")


def g13_mapa_estados_validos(t1, t2):
    """Crescimento de Lula e de Flávio do 1º para o 2º turno, por estado, em p.p. dos votos válidos."""
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

    from estatistica import NULO_TECNICO_1T

    def validos(d, fora):
        cand = [c for c in d.columns if c.startswith("V_") and c not in ["V_BRANCO", "V_NULO", *fora]]
        d = d[d.SG_UF != "ZZ"].assign(VAL=lambda x: x[cand].sum(axis=1))
        return d.groupby("SG_UF")[["V_13", "V_22", "VAL"]].sum()

    a, b = validos(t1, NULO_TECNICO_1T), validos(t2, [])
    ufs = malha_uf()
    norm = TwoSlopeNorm(vmin=-2, vcenter=0, vmax=10)  # mesma escala nos dois mapas; queda em cinza
    fig, eixos = plt.subplots(1, 2, figsize=(13, 7.2), layout="constrained")
    for ax, num, nome, cor in [(eixos[0], "V_13", "Lula", LULA), (eixos[1], "V_22", "Flávio", ADV)]:
        g = ufs.assign(var=ufs.SG_UF.map((b[num] / b.VAL - a[num] / a.VAL) * 100))
        nac = (b[num].sum() / b.VAL.sum() - a[num].sum() / a.VAL.sum()) * 100
        cmap = LinearSegmentedColormap.from_list(nome, ["#b9b8b3", "#ffffff", cor])
        g.plot(column="var", cmap=cmap, norm=norm, ax=ax, edgecolor="#c9c8c3", linewidth=0.6)
        rotular(ax, g, norm)
        enquadrar(ax, leste=-31.5)
        ax.set_title(f"{nome}: {br(a[num].sum() / a.VAL.sum() * 100)}% → {br(b[num].sum() / b.VAL.sum() * 100)}% "
                     f"dos válidos ({sinal(nac)} p.p.)", color=cor, fontsize=12)
    fig.suptitle("Quanto cada candidato cresceu do 1º para o 2º turno, por estado (pontos percentuais dos votos "
                 "válidos)", x=0.01, ha="left", fontsize=13, weight="bold", color=TEXTO)
    fig.text(0.01, -0.01, "Os votos dos candidatos que ficaram fora do 2º turno se dividiram entre os dois. "
             "Em cinza, queda. Exterior fora. Malha: IBGE.", fontsize=8.5, color=TEXTO2)
    salvar(fig, "13_mapa_estados_validos.png")


if __name__ == "__main__":
    so = sys.argv[1:]
    t2, t1, d22 = carregar(), carregar(turno=1), carregar(ano=2022)
    mm = junta_turnos() if (not so or {"g5", "g6", "g8"} & set(so)) else None
    for nome, f in [("g1", lambda: g1_duas_eleicoes(t2, d22)), ("g2", lambda: g2_decomposicao(t2, t1)),
                    ("g3", lambda: g3_horarios(t1, t2, d22)), ("g4", g4_logs_tardias), ("g5", lambda: g5_modelo(mm)),
                    ("g6", lambda: g6_residuo(mm)), ("g7", g7_logs), ("g8", lambda: print(g8_margem(t2, mm))),
                    ("g9", lambda: g9_biometria_estados(t2)), ("g10", g10_biometria_por_hora),
                    ("g11", lambda: g11_mapa_municipios(t1, t2)), ("g12", lambda: g12_mapa_estados_disputa(t1, t2)),
                    ("g13", lambda: g13_mapa_estados_validos(t1, t2))]:
        if not so or nome in so:
            f()
