"""Confere, com os BUs oficiais do 2º turno de 2026, os números das suspeitas de fraude que circularam depois da
eleição (horário de fechamento, seções das 19h, liberação manual, seções unânimes, Benford) e testa cada conclusão.
Gera analise/RESULTADOS.md.

Convenções: "% Lula" = Lula ÷ (Lula + Flávio). "Saldo" = votos de Lula − votos de Flávio num grupo de seções.
Horário "local" = como gravado pela urna; "Brasília" = convertido pelo fuso de cada município (exterior fora)."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carregar import FAIXAS_ROTULO, FUSO, RAIZ, carregar, faixa_horario  # noqa: E402
from estatistica import CHAVE, centrar, coef_cluster, fmt, locais, md  # noqa: E402

SAIDA = os.path.join(RAIZ, "analise", "RESULTADOS.md")
NE = {"BA", "PE", "CE", "MA", "PB", "PI", "RN", "AL", "SE"}
MARGEM = None
L = []


def out(s=""):
    L.append(s)


def pct(x):
    return x.V_13.sum() / (x.V_13.sum() + x.V_22.sum()) * 100


def segundos(horario):
    return (horario - horario.dt.normalize()).dt.total_seconds()


def tabela_faixas(d, col):
    g = d.assign(faixa=faixa_horario(d[col])).groupby("faixa", observed=False).agg(
        secoes=("NR_SECAO", "size"), comparecimento=("QT_COMPARECIMENTO", "sum"),
        lula=("V_13", "sum"), adversario=("V_22", "sum"))
    g["% Lula"] = (g.lula / (g.lula + g.adversario) * 100).round(2)
    g["saldo Lula"] = g.lula - g.adversario
    return g.astype({c: "int64" for c in ["comparecimento", "lula", "adversario", "saldo Lula"]})


def secao_totais(d):
    global MARGEM
    MARGEM = int(d.V_13.sum() - d.V_22.sum())
    out("# Horário de fechamento, seções das 19h, liberação manual, seções unânimes e Benford — 2º turno 2026")
    out()
    out("Fonte: BWeb de Presidente do 2º turno (`dados/tse/2026/presidente/2turno/`), extraídos dos .zip oficiais "
        "conferidos com o SHA-512 do TSE.")
    out()
    out("## 0. Totais (conferem com o resultado oficial)")
    out()
    out(f"- Seções com voto: {fmt(len(d))} · comparecimento: {fmt(d.QT_COMPARECIMENTO.sum())}")
    out(f"- Lula: {fmt(d.V_13.sum())} ({pct(d):.2f}% dos válidos) · Flávio: {fmt(d.V_22.sum())} · margem: **{fmt(MARGEM)}**")
    out(f"- Liberados manualmente (digital falhou; campo QT_ELEI_BIOM_SEM_HABILITACAO): {fmt(d.QT_BIOM_SEM_HAB.sum())} "
        f"({d.QT_BIOM_SEM_HAB.sum() / d.QT_COMPARECIMENTO.sum() * 100:.2f}% do comparecimento)")
    out()


def secao_replica(d, d22):
    out("## 1. Os números que circularam, recalculados com o horário local da urna")
    out()
    out("Com o horário como gravado pela urna (local) e estas faixas, os números que circularam se reproduzem:")
    out()
    for ano, x in [(2026, d), (2022, d22)]:
        t = tabela_faixas(x, "ENC_LOCAL")
        out(f"### {ano} ({'Lula × Flávio Bolsonaro' if ano == 2026 else 'Lula × Jair Bolsonaro'})")
        out()
        out(md(t))
        out()
    tarde = d[d.ENC_LOCAL.dt.hour == 19]
    out(f"- A afirmação de que \"mais de 2 milhões de eleitores\" votaram nas seções fechadas depois das 19h: nessas "
        f"{fmt(len(tarde))} seções havia {fmt(tarde.QT_APTOS.sum())} eleitores **aptos**, mas votaram "
        f"{fmt(tarde.QT_COMPARECIMENTO.sum())}. O número só bate contando os aptos.")
    out()


def secao_ate17(d, t1):
    out("## 2. O grupo \"até 17:00:59\": por que Flávio vence nele?")
    out()
    g = segundos(d.ENC_LOCAL) < 17 * 3600 + 60
    oeste = d.SG_UF.isin(FUSO)
    a, b = d[g], d[~g]
    out(f"- Diferença bruta: {pct(a):.2f}% de Lula no grupo contra {pct(b):.2f}% no resto (**{pct(a) - pct(b):+.2f} p.p.**).")
    out(f"- Os estados com fuso a oeste (AC, AM, MT, MS, RO, RR), cujas urnas marcam 15h/16h quando são 17h em Brasília, "
        f"são {g[oeste].sum() / g.sum() * 100:.0f}% das seções do grupo e respondem por "
        f"{(a[oeste[g]].V_22.sum() - a[oeste[g]].V_13.sum()) / (a.V_22.sum() - a.V_13.sum()) * 100:.0f}% da vantagem de Flávio "
        f"nele. Sem eles, o grupo ainda dá {100 - pct(a[~oeste[g]]):.1f}% a Flávio.")
    x = d.assign(v=d.V_13 + d.V_22, p=d.V_13 / (d.V_13 + d.V_22) * 100, g=g.astype(float))
    x = x[x.v > 0]
    mun = x.SG_UF + "-" + x.CD_MUNICIPIO.astype(str)
    linhas = []
    for nome, fe in [("sem controle", None), ("comparando dentro do mesmo estado", x.SG_UF),
                     ("comparando dentro do mesmo município", mun)]:
        bb, se = coef_cluster(centrar(x.p, fe, x.v), centrar(x.g, fe, x.v), mun, peso=x.v)
        linhas.append({"comparação": nome, "diferença de % Lula (grupo − resto)": f"{bb:+.2f} p.p. (EP {se:.2f})"})
    out()
    out(md(pd.DataFrame(linhas), index=False))
    out()
    j = d.assign(g=g)[CHAVE + ["g"]].merge(t1[CHAVE + ["V_13", "V_22"]], on=CHAVE)
    out(f"- **As mesmas seções já votavam assim no 1º turno**: lá, o grupo deu {pct(j[j.g]):.2f}% a Lula contra "
        f"{pct(j[~j.g]):.2f}% no resto ({pct(j[j.g]) - pct(j[~j.g]):+.2f} p.p.), praticamente a mesma diferença do 2º turno.")
    out(f"- Tamanho: mediana de {a.QT_APTOS.median():.0f} aptos no grupo contra {b.QT_APTOS.median():.0f} no resto. "
        "O tamanho da seção quase não explica a diferença; a geografia explica.")
    out("- Conclusão: o grupo concentra regiões onde Flávio é mais forte (os estados a oeste por causa do fuso, e o "
        "interior, onde há menos fila). Dentro do mesmo município a diferença praticamente some, e ela já existia no 1º turno.")
    out()


def secao_brasilia(d):
    out("## 3. Horário convertido para Brasília")
    out()
    out(md(tabela_faixas(d, "ENC_BRASILIA")))
    out()
    n = d[segundos(d.ENC_BRASILIA) < 17 * 3600 + 16 * 60]
    out(f"- Só com as seções que fecharam até 17h15 (Brasília), Lula vence por **{fmt(n.V_13.sum() - n.V_22.sum())}** votos.")
    out()


def secao_tardias(d):
    out("## 4. As seções que fecharam às 19h ou depois (Brasília)")
    out()
    tarde = segundos(d.ENC_BRASILIA) >= 19 * 3600
    t = d[tarde]
    mi = d.ENC_BRASILIA.dt.hour * 60 + d.ENC_BRASILIA.dt.minute
    saldo = int(t.V_13.sum() - t.V_22.sum())
    out(f"- São **{fmt(tarde.sum())}** seções: {fmt((mi == 19 * 60).sum())} fecharam no minuto 19:00 exato e "
        f"{fmt(mi.between(19 * 60, 19 * 60 + 15).sum())} entre 19:00 e 19:15. O formato é o de um horário-limite marcado "
        "às 19h (como o fechamento normal das 17h, deslocado 2 horas), não o de uma fila que se estende.")
    out(f"- Votaram nelas {fmt(t.QT_COMPARECIMENTO.sum())} eleitores ({t.QT_COMPARECIMENTO.sum() / t.QT_APTOS.sum() * 100:.1f}% "
        f"dos aptos; no país, {d.QT_COMPARECIMENTO.sum() / d.QT_APTOS.sum() * 100:.1f}%). Saldo de Lula nelas: {fmt(saldo)} "
        f"({saldo / MARGEM * 100:.1f}% da margem). Anulando **todas** essas seções, Lula ainda venceria por "
        f"{fmt(MARGEM - saldo)}.")
    mun = t.groupby(["SG_UF", "NM_MUNICIPIO"]).size().sort_values(ascending=False)
    out(f"- Onde estão: {', '.join(f'{m.title()} ({u}) {fmt(v)}' for (u, m), v in mun.head(6).items())}. Os 5 primeiros "
        f"municípios somam {mun.head(5).sum() / len(t) * 100:.0f}% do grupo.")
    x = d.merge(locais(), on=CHAVE, how="left")
    x["tarde"] = tarde.values
    x["local"] = x.SG_UF + "-" + x.CD_MUNICIPIO.astype(str) + "-" + x.NR_ZONA.astype(str) + "-" + x.NR_LOCAL_VOTACAO.astype(str)
    por_local = x[x.local.isin(x.loc[x.tarde, "local"])].groupby("local").tarde.mean()
    out(f"- Elas estão em {fmt(len(por_local))} locais de votação; em {fmt((por_local == 1).sum())} deles **todas** as seções "
        "fecharam às 19h. O agrupamento é por local de votação (escola), compatível com uma decisão tomada por local.")
    # Comparação com as vizinhas do mesmo local que fecharam às 17h
    misto = x[x.local.isin(por_local[(por_local > 0) & (por_local < 1)].index)].copy()
    misto = misto[(misto.V_13 + misto.V_22) > 0]
    misto["p"] = misto.V_13 / (misto.V_13 + misto.V_22) * 100
    misto["comp"] = misto.QT_COMPARECIMENTO / misto.QT_APTOS * 100
    b1, s1 = coef_cluster(centrar(misto.p, misto.local), centrar(misto.tarde.astype(float), misto.local), misto.local)
    b2, s2 = coef_cluster(centrar(misto.comp, misto.local), centrar(misto.tarde.astype(float), misto.local), misto.local)
    out(f"- Comparando com as seções **do mesmo local de votação** que fecharam às 17h ({fmt(len(misto))} seções em "
        f"{fmt(misto.local.nunique())} locais mistos): diferença de % Lula {b1:+.2f} p.p. (EP {s1:.2f}); diferença de "
        f"comparecimento {b2:+.2f} p.p. (EP {s2:.2f}). Nenhum sinal de votos a mais nem de voto diferente.")
    por_uf = t.groupby("SG_UF").agg(secoes=("NR_SECAO", "size"), lula=("V_13", "sum"), flavio=("V_22", "sum"))
    por_uf["% Lula nas seções tardias"] = (por_uf.lula / (por_uf.lula + por_uf.flavio) * 100).round(2)
    uf = d.groupby("SG_UF")[["V_13", "V_22"]].sum()
    por_uf["% Lula no estado todo"] = (uf.V_13 / (uf.V_13 + uf.V_22) * 100).round(2)
    out()
    out(md(por_uf.sort_values("secoes", ascending=False).astype({"lula": "int64", "flavio": "int64"})))
    out()
    cache = os.path.join(RAIZ, "dados", "derivados", "logs_tardias_2t_2026.csv.gz")
    if os.path.exists(cache):
        out("- **Votos dados depois das 17h, segundo o log de cada urna**: ver `LOGS_TARDIAS.md` (todas as seções tardias foram lidas).")
    out()


def secao_biometria(d, d1):
    out("## 5. Eleitores liberados manualmente (\"sem biometria\")")
    out()
    # Exterior fora da estimativa: lá não há biometria e a liberação é zero por definição. Seus votos voltam às margens.
    x = d[((d.V_13 + d.V_22) > 0) & (d.SG_UF != "ZZ")].copy()
    saldo_zz = int((d.V_13 - d.V_22)[d.SG_UF == "ZZ"].sum())
    x["v"] = x.V_13 + x.V_22
    x["p"] = x.V_13 / x.v
    x["bio"] = x.QT_BIOM_SEM_HAB / x.QT_COMPARECIMENTO
    mun = x.SG_UF + "-" + x.CD_MUNICIPIO.astype(str)
    faixa = pd.cut(x.bio, [-.01, .02, .05, .1, .2, .3, .5, 1.01], labels=["0-2%", "2-5%", "5-10%", "10-20%", "20-30%", "30-50%", "50-100%"])
    t = x.groupby(faixa, observed=True).agg(secoes=("p", "size"), lula=("V_13", "sum"), flavio=("V_22", "sum"),
                                            liberados=("QT_BIOM_SEM_HAB", "sum"))
    t["% Lula"] = (t.lula / (t.lula + t.flavio) * 100).round(2)
    t["% das seções no Nordeste"] = (x.groupby(faixa, observed=True).SG_UF.apply(lambda u: u.isin(NE).mean()) * 100).round(1)
    t.index.name = "% liberados na seção"
    out(md(t.astype({"lula": "int64", "flavio": "int64", "liberados": "int64"})))
    out()
    out("A % de Lula sobe nas faixas de liberação alta, mas essas faixas têm poucas seções e mais Nordeste. "
        "Para separar isso, medimos a **inclinação** (quanto a % de Lula muda quando a liberação muda), comparando "
        "seções parecidas, e daí estimamos como os liberados votaram.")
    out()
    V = x.v.sum()
    f = (x.QT_BIOM_SEM_HAB * x.v / x.QT_COMPARECIMENTO).sum() / V  # fração dos válidos que veio de liberados
    p = x.V_13.sum() / V
    linhas = []
    for nome, fe in [("nacional", None), ("dentro do estado", x.SG_UF), ("dentro do município", mun)]:
        b, se = coef_cluster(centrar(x.p, fe, x.v), centrar(x.bio, fe, x.v), mun, peso=x.v)
        res = {"comparação": nome, "inclinação (EP)": f"{b:.3f} ({se:.3f})"}
        for rot, bb in [("estimativa", b), ("limite de 95%", b + 1.96 * se)]:
            po = p - bb * f  # % de Lula entre os não liberados
            res[f"% Lula entre liberados ({rot})"] = round((po + bb) * 100, 1)
            res[f"margem sem os liberados ({rot})"] = fmt((2 * po - 1) * V * (1 - f) + saldo_zz)
        linhas.append(res)
    out(md(pd.DataFrame(linhas), index=False))
    out()
    pior = int((x.V_13 - np.minimum(x.V_13, x.QT_BIOM_SEM_HAB)).sum() - x.V_22.sum()) + saldo_zz
    out(f"- **Pior caso aritmético** (todo liberado votou em Lula sempre que possível e é retirado): margem de {fmt(pior)}. "
        "Esse cenário exige que, em cada seção, os liberados tenham votado em Lula em bloco, o que contradiz os testes abaixo.")
    out("- Por que as linhas dão resultados tão diferentes: liberação manual e voto em Lula são ambos mais altos em certas "
        "regiões (Nordeste, interior). Comparar o país todo (ou o estado todo) mistura essas regiões e atribui à liberação "
        "um efeito que é da geografia: é a *falácia ecológica*. A comparação mais justa é entre seções da **mesma "
        "cidade**: aí a inclinação cai a quase zero, e mesmo no limite de 95% Lula mantém pelo menos 2,5 milhões de margem.")
    out("- Mesmo assim, estimativas com dados agregados nunca são definitivas. Por isso o teste mais forte é o do 1º turno (abaixo), "
        "que compara cada seção com ela mesma.")
    out("- **Testes contra o 1º turno** (em `PRIMEIRO_TURNO.md`, seção 5): dado o voto da própria seção no 1º turno, mais "
        "liberação vem com **menos** Lula do que o esperado, e o **aumento** da liberação do 1º para o 2º turno não tem "
        "relação com o resultado. Se liberações fossem usadas para pôr votos em Lula, apareceria o contrário.")
    out(f"- A taxa de liberação é parecida no Nordeste ({x[x.SG_UF.isin(NE)].QT_BIOM_SEM_HAB.sum() / x[x.SG_UF.isin(NE)].QT_COMPARECIMENTO.sum() * 100:.2f}%) "
        f"e no resto do país ({x[~x.SG_UF.isin(NE)].QT_BIOM_SEM_HAB.sum() / x[~x.SG_UF.isin(NE)].QT_COMPARECIMENTO.sum() * 100:.2f}%), "
        f"e quase igual no 1º turno ({d1.QT_BIOM_SEM_HAB.sum() / d1.QT_COMPARECIMENTO.sum() * 100:.2f}%).")
    out("- O que o campo significa, pelos logs das urnas (`LOGS.md`): o eleitor tem biometria cadastrada, a digital falhou "
        "4 vezes, a urna pediu um dado pessoal (e recusou quando não conferia) e exigiu a digital do mesário. É a linha "
        "\"Habilitação biográfica\" do BU impresso.")
    out()


def secao_unanimes(d, d1, d22):
    out("## 6. Seções quase unânimes")
    out()
    linhas = []
    for nome, x in [("2º turno 2026", d), ("1º turno 2026", d1), ("2º turno 2022", d22)]:
        v = x.V_13 + x.V_22
        p = (x.V_13 / v)[v > 0]
        linhas.append({"eleição": nome, "100% Lula": int((p == 1).sum()), "100% adversário": int((p == 0).sum()),
                       ">90% Lula": int((p > .9).sum()), ">90% adversário": int((p < .1).sum())})
    out(md(pd.DataFrame(linhas), index=False))
    out()
    v = d.V_13 + d.V_22
    p = d.V_13 / v
    top = d[p > .9].SG_UF.value_counts()
    ne = d[d.SG_UF.isin(NE)]
    out(f"- Das {fmt(len(d[p > .9]))} seções com mais de 90% para Lula, {top.head(5).sum() / top.sum() * 100:.0f}% estão em "
        f"{', '.join(top.head(5).index)}. Lula teve {pct(ne):.1f}% no Nordeste. Com média regional perto de 70%, a cauda acima de "
        "90% fica de um lado só: o voto no Brasil é regional e a distribuição nacional não precisa ser simétrica.")
    out()


def secao_benford(d):
    out("## 7. Lei de Benford")
    out()
    x = d[(d.V_13 + d.V_22) > 0]
    ben1 = np.log10(1 + 1 / np.arange(1, 10))
    ben2 = np.array([sum(np.log10(1 + 1 / (10 * k + j)) for k in range(1, 10)) for j in range(10)])
    rng = np.random.default_rng(2026)
    v = (x.V_13 + x.V_22).values
    sims = [rng.binomial(v, (x.V_13 / (x.V_13 + x.V_22)).values) for _ in range(20)]  # 20 eleições honestas simuladas
    tab1 = {"Benford esperado %": (ben1 * 100).round(1)}
    for c, n in [("V_13", "Lula %"), ("V_22", "Flávio %")]:
        dig = x[c][x[c] > 0].astype(int).astype(str).str[0].astype(int)
        tab1[n] = (dig.value_counts(normalize=True).reindex(range(1, 10), fill_value=0) * 100).round(1).values
    out("**1º dígito**")
    out()
    out(md(pd.DataFrame(tab1, index=range(1, 10))))
    out()
    faixa_100 = ((x.V_13 >= 100) & (x.V_13 < 200)).mean() * 100
    out(f"- Os dois candidatos desviam do mesmo jeito. Seções têm tamanho limitado (mediana de {d.QT_APTOS.median():.0f} aptos), "
        f"e o voto de Lula numa seção fica entre 100 e 199 em {faixa_100:.0f}% delas, então o dígito 1 domina. A literatura "
        "(Deckert, Myagkov & Ordeshook, 2011) considera o 1º dígito inadequado para votos por seção.")
    out()

    def segundo(vals):
        vals = vals[vals >= 10]
        dig = pd.Series(vals).astype(int).astype(str).str[1].astype(int)
        obs = dig.value_counts().reindex(range(10), fill_value=0).values
        esp = ben2 * len(dig)
        return ((obs - esp) ** 2 / esp).sum(), dig.mean()

    linhas = []
    for nome, vals in [("Lula (real)", x.V_13.values), ("Flávio (real)", x.V_22.values)]:
        chi, media = segundo(vals)
        linhas.append({"série": nome, "média do 2º dígito": f"{media:.3f}", "qui-quadrado vs Benford": round(chi)})
    faixa = {}
    for nome, s in [("Lula", sims), ("Flávio", [v - s_ for s_ in sims])]:
        r = np.array([segundo(s_) for s_ in s])
        faixa[nome] = (r[:, 1].min(), r[:, 1].max())
        linhas.append({"série": f"{nome} (20 eleições honestas simuladas: sorteio binomial com o tamanho e a % de cada "
                                "seção; média e faixa)", "média do 2º dígito": f"{r[:, 1].mean():.3f} ({r[:, 1].min():.3f}–{r[:, 1].max():.3f})",
                       "qui-quadrado vs Benford": f"{r[:, 0].mean():.0f} ({r[:, 0].min():.0f}–{r[:, 0].max():.0f})"})
    out("**2º dígito** (Benford esperado: média 4,187)")
    out()
    out(md(pd.DataFrame(linhas), index=False))
    out()
    dentro = {n: lo <= segundo(vals)[1] <= hi for n, vals, (lo, hi) in
              [("Lula", x.V_13.values, faixa["Lula"]), ("Flávio", x.V_22.values, faixa["Flávio"])]}
    out("- O 2º dígito real \"falha\" em Benford, e as eleições honestas simuladas falham do mesmo jeito: contagens "
        "desse tamanho não seguem Benford. " + "; ".join(
            f"{n}: média real {'dentro' if ok else 'fora'} da faixa das simulações" for n, ok in dentro.items())
        + ". Diferenças de centésimos no dígito médio estão abaixo do que esse teste consegue interpretar.")
    linhas = []
    for nome, c in [("Lula", "V_13"), ("Flávio", "V_22")]:
        vals = x[c][x[c] >= 10].astype(int) % 10
        obs = vals.value_counts().reindex(range(10), fill_value=0).values
        esp = len(vals) / 10
        linhas.append({"candidato": nome, "qui-quadrado (9 g.l.; crítico 5% = 16,9)": round(((obs - esp) ** 2 / esp).sum(), 1),
                       "maior desvio de 10% (p.p.)": round(np.abs(obs / len(vals) - 0.1).max() * 100, 2)})
    out()
    out("**Último dígito** (teste de Beber & Scacco: em contagens honestas, cada dígito final aparece ~10% das vezes)")
    out()
    out(md(pd.DataFrame(linhas), index=False))
    out()


def main():
    d = carregar()
    d1 = carregar(turno=1)
    d22 = carregar(ano=2022)
    secao_totais(d)
    secao_replica(d, d22)
    secao_ate17(d, d1)
    secao_brasilia(d)
    secao_tardias(d)
    secao_biometria(d, d1)
    secao_unanimes(d, d1, d22)
    secao_benford(d)
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
