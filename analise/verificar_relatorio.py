"""Confere, com os BUs oficiais do 2º turno de 2026, cada número do
"Relatório Pericial Independente" que circulou nas redes. Gera analise/RESULTADOS.md."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carregar import FUSO, carregar  # noqa: E402

SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RESULTADOS.md")
NE = {"BA", "PE", "CE", "MA", "PB", "PI", "RN", "AL", "SE"}
linhas = []


def out(s=""):
    linhas.append(s)


def fmt(n):
    return f"{n:,.0f}".replace(",", ".")


def md(df):
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_integer_dtype(df[c]):
            df[c] = df[c].map(fmt)
    return df.to_markdown(disable_numparse=True)


def janelas(d, col):
    seg = (d[col] - d[col].dt.normalize()).dt.total_seconds()
    bins = [0, 17 * 3600 + 1, 17 * 3600 + 15 * 60 + 1, 19 * 3600, 86400]
    lab = ["até 17h00", "17h00 a 17h15", "17h15 a 18h59", "19h00 ou depois"]
    g = d.assign(janela=pd.cut(seg, bins, labels=lab, right=False)).groupby("janela", observed=False).agg(
        secoes=("NR_SECAO", "size"), comparecimento=("QT_COMPARECIMENTO", "sum"),
        lula=("V_13", "sum"), flavio=("V_22", "sum"))
    g["% Lula"] = (g.lula / (g.lula + g.flavio) * 100).round(2)
    g["saldo Lula"] = g.lula - g.flavio
    return g.astype({c: "int64" for c in ["comparecimento", "lula", "flavio", "saldo Lula"]})


def main():
    d = carregar()
    validos = d.V_13 + d.V_22
    lula, flavio = d.V_13.sum(), d.V_22.sum()
    margem = lula - flavio
    bio = d.QT_BIOM_SEM_HAB.sum()

    out("# Verificação do \"Relatório Pericial Independente\" — 2º turno 2026")
    out()
    out("Fonte: Boletins de Urna (BWeb) do 2º turno, `dados/tse/2026/boletim_urna/2turno/`, "
        "conferidos com os hashes SHA-512 publicados pelo TSE. Cargo: Presidente.")
    out()
    out("## Totais (conferem com o relatório)")
    out()
    out(f"- Seções: {fmt(len(d))}")
    out(f"- Comparecimento: {fmt(d.QT_COMPARECIMENTO.sum())}")
    out(f"- Lula (13): {fmt(lula)} ({lula / (lula + flavio) * 100:.2f}% dos válidos)")
    out(f"- Flávio Bolsonaro (22): {fmt(flavio)}")
    out(f"- Margem: {fmt(margem)}")
    out(f"- Eleitores liberados sem biometria (QT_ELEI_BIOM_SEM_HABILITACAO): {fmt(bio)} "
        f"({bio / d.QT_COMPARECIMENTO.sum() * 100:.2f}% do comparecimento)")
    out()

    out("## Réplica exata das tabelas do relatório (Cap. 1 e 2)")
    out()
    out("O relatório usa o relógio local da urna e as faixas até 17:00:59, 17:01–17:15:59, "
        "17:16–18:59:59 e 19:00–19:59:59. Com esse corte, todos os números dele se reproduzem:")
    out()
    H = lambda h, m=0: h * 3600 + m * 60  # noqa: E731
    faixas = [0, H(17, 1), H(17, 16), H(19), H(20), 86400]
    rot = ["até 17:00:59", "17:01–17:15", "17:16–18:59", "19:00–19:59", "20h ou depois"]
    for ano in (2026, 2022):
        x = d if ano == 2026 else carregar(ano=2022)
        seg = (x.ENC_LOCAL - x.ENC_LOCAL.dt.normalize()).dt.total_seconds()
        t = x.assign(faixa=pd.cut(seg, faixas, right=False, labels=rot)).groupby("faixa", observed=False).agg(
            secoes=("NR_SECAO", "size"), comparecimento=("QT_COMPARECIMENTO", "sum"),
            lula=("V_13", "sum"), adversario=("V_22", "sum"),
            pct_estados_oeste=("SG_UF", lambda u: round(u.isin(set(FUSO)).mean() * 100, 1)))
        t["% Lula"] = (t.lula / (t.lula + t.adversario) * 100).round(2)
        t["saldo Lula"] = t.lula - t.adversario
        t = t.astype({c: "int64" for c in ["comparecimento", "lula", "adversario", "saldo Lula"]})
        out(f"### {ano} ({'Lula × Flávio Bolsonaro' if ano == 2026 else 'Lula × Jair Bolsonaro, grupo de controle'})")
        out()
        out(md(t))
        out()
    out("O mesmo corte aplicado a 2022 mostra o mesmo padrão de \"duas eleições\": o candidato 22 vence "
        "nas urnas que fecham até 17:00:59 e Lula vence nas que fecham depois. A explicação é a composição "
        "dos grupos, não o horário. O primeiro grupo concentra as urnas dos estados a oeste (relógio local "
        "15h/16h, onde o candidato 22 é forte) e as seções menores, sem fila. A faixa 17:01–17:15 não é "
        "prorrogação: é o fechamento normal de quem ainda estava na fila às 17h, e reúne 68% das seções do país.")
    out()
    out("## Cap. 1 e 2 — horário de encerramento")
    out()
    out("`DT_ENCERRAMENTO` é gravado no **relógio local da urna**. AC, AM, MT, MS, RO e RR "
        "estão 1 ou 2 horas atrás de Brasília. Por isso as urnas desses estados aparecem "
        "\"fechando antes das 17h\", mas na verdade fecharam às 17h de Brasília.")
    out()
    out("### Relógio local (como está no arquivo)")
    out()
    out(md(janelas(d, "ENC_LOCAL")))
    seg_loc = (d.ENC_LOCAL - d.ENC_LOCAL.dt.normalize()).dt.total_seconds()
    cedo = d[seg_loc < 17 * 3600 + 1].SG_UF.value_counts()
    out()
    out("Seções no grupo \"até 17h00\" (relógio local), por UF: "
        + ", ".join(f"{k} {fmt(v)}" for k, v in cedo.items()) + ".")
    out()
    out("### Convertido para horário de Brasília")
    out()
    out(md(janelas(d, "ENC_BRASILIA")))
    out()
    seg_bsb = (d.ENC_BRASILIA - d.ENC_BRASILIA.dt.normalize()).dt.total_seconds()
    normal = d[seg_bsb <= 17 * 3600 + 15 * 60]
    out(f"- Considerando só as seções que fecharam até 17h15 (Brasília), Lula ainda vence por "
        f"**{fmt(normal.V_13.sum() - normal.V_22.sum())}** votos.")
    tarde = d[d.ENC_LOCAL.dt.hour >= 19]
    out(f"- As {fmt(len(tarde))} seções que fecharam às 19h ou depois deram a Lula um saldo de "
        f"{fmt(tarde.V_13.sum() - tarde.V_22.sum())} votos, ou "
        f"{(tarde.V_13.sum() - tarde.V_22.sum()) / margem * 100:.1f}% da margem final.")
    out("- O \"grupo que fechou até 17h\" em que Flávio vence é efeito de fuso horário: "
        "são as urnas de AC, AM, MT, MS, RO e RR, que fecharam às 15h ou 16h no relógio "
        "local, ou seja, 17h de Brasília. São estados em que Flávio vence. "
        "Não existe \"eleição até as 17h\" separada de uma \"eleição depois das 17h\".")
    out()
    por_uf = tarde.groupby("SG_UF").agg(secoes=("NR_SECAO", "size"), lula=("V_13", "sum"),
                                         flavio=("V_22", "sum"))
    por_uf["% Lula nas seções tardias"] = (por_uf.lula / (por_uf.lula + por_uf.flavio) * 100).round(2)
    uf = d.groupby("SG_UF")[["V_13", "V_22"]].sum()
    por_uf["% Lula no estado todo"] = (uf.V_13 / (uf.V_13 + uf.V_22) * 100).round(2)
    out("### Seções encerradas às 19h ou depois, por UF")
    out()
    out(md(por_uf.sort_values("secoes", ascending=False)))
    out()
    sp = tarde[tarde.SG_UF == "SP"].NM_MUNICIPIO.value_counts().head(5)
    out(f"Em SP, {fmt(sp.iloc[0])} das {fmt((tarde.SG_UF == 'SP').sum())} seções tardias "
        f"ficam na capital ({sp.index[0]}). Ou seja, comparar com \"o restante do estado\" "
        "mistura a capital com o interior. No RJ, que tem mais seções tardias que qualquer "
        "outro estado, Flávio venceu nessas seções.")
    out()

    out("## Cap. 3 — biometria")
    out()
    d = d[validos > 0].copy()
    d["pl"] = d.V_13 / (d.V_13 + d.V_22)
    d["bio"] = d.QT_BIOM_SEM_HAB / d.QT_COMPARECIMENTO
    c_nac = np.corrcoef(d.bio, d.pl)[0, 1]
    dm = d.groupby(["SG_UF", "CD_MUNICIPIO"])
    c_mun = np.corrcoef(d.bio - dm.bio.transform("mean"), d.pl - dm.pl.transform("mean"))[0, 1]
    out(f"- Correlação (seção) entre % liberado sem biometria e % Lula: **{c_nac:.3f}** no país; "
        f"**{c_mun:.3f}** comparando seções dentro do mesmo município. Na prática, nenhuma.")
    faixa = pd.cut(d.bio, [-.01, .02, .05, .1, .2, .3, .5, 1.01])
    t = d.groupby(faixa, observed=True).agg(secoes=("pl", "size"), lula=("V_13", "sum"),
                                            flavio=("V_22", "sum"), sem_biometria=("QT_BIOM_SEM_HAB", "sum"))
    t["% Lula"] = (t.lula / (t.lula + t.flavio) * 100).round(2)
    t = t.astype({c: "int64" for c in ["lula", "flavio", "sem_biometria"]})
    t.index = ["0-2%", "2-5%", "5-10%", "10-20%", "20-30%", "30-50%", "50-100%"]
    t.index.name = "% sem biometria na seção"
    out()
    out(md(t))
    out()
    ne, re = d[d.SG_UF.isin(NE)], d[~d.SG_UF.isin(NE)]
    out(f"- Taxa sem biometria: Nordeste {ne.QT_BIOM_SEM_HAB.sum() / ne.QT_COMPARECIMENTO.sum() * 100:.2f}%, "
        f"resto do país {re.QT_BIOM_SEM_HAB.sum() / re.QT_COMPARECIMENTO.sum() * 100:.2f}%. "
        "A taxa é parecida em todo o país, inclusive onde Flávio venceu.")
    lb = (d.QT_BIOM_SEM_HAB * d.pl).sum()
    fb = (d.QT_BIOM_SEM_HAB * (1 - d.pl)).sum()
    out(f"- Tirando todos os eleitores sem biometria, supondo que votaram como o resto da "
        f"própria seção, Lula ainda venceria por **{fmt((lula - lb) - (flavio - fb))}** votos.")
    out("- Comparar 8,6 milhões com a margem de 4,4 milhões só faria sentido se esses votos "
        "fossem todos de um candidato. Os dados mostram que não são.")
    out("- O campo da BWeb corresponde à linha \"Habilitação biográfica\" do BU impresso: o eleitor "
        "tinha biometria cadastrada e a digital falhou 4 vezes. Pelos logs das urnas (LOGS.md), nesse caso "
        "a urna pede um dado pessoal do eleitor, recusa se ele não confere e depois exige a digital do "
        "mesário. Não é a \"simples digitação do ano de nascimento\" descrita no relatório. Digitar o ano "
        "de nascimento sozinho é o caminho de outro grupo, o dos eleitores sem biometria cadastrada, que o "
        "BU conta em outra linha.")
    d22 = carregar(ano=2022)
    out(f"- Em 2022 o campo mais próximo (QT_ELEITORES_BIOMETRIA_NH, \"não habilitados por biometria\"; nome e talvez definição diferentes) somou {fmt(d22.QT_BIOM_SEM_HAB.sum())} "
        f"eleitores, {d22.QT_BIOM_SEM_HAB.sum() / (d22.V_13.sum() - d22.V_22.sum()):.1f} vezes a margem "
        f"daquele ano ({fmt(d22.V_13.sum() - d22.V_22.sum())}). A razão \"quase o dobro da margem\" de "
        "2026 é menor que a de 2022.")
    out()

    out("## Cap. 4 — seções quase unânimes")
    out()
    out(f"- 100% dos válidos: Lula {(d.pl == 1).sum()}, Flávio {(d.pl == 0).sum()}. "
        f"Acima de 90%: Lula {(d.pl > .9).sum()}, Flávio {(d.pl < .1).sum()}.")
    top = d[d.pl > .9].SG_UF.value_counts().head(5)
    out(f"- As seções com mais de 90% para Lula se concentram em {', '.join(f'{k} ({v})' for k, v in top.items())}. "
        f"Lula teve {ne.V_13.sum() / (ne.V_13.sum() + ne.V_22.sum()) * 100:.1f}% dos válidos no Nordeste "
        "como um todo. Quando a média regional é perto de 70%, a cauda acima de 90% "
        "fica toda de um lado. A distribuição não é \"gaussiana em torno de 50%\" porque "
        "o voto no Brasil é fortemente regional.")
    out()

    out("## Cap. 5 — Lei de Benford (o relatório não mostrou o resultado)")
    out()
    ben = np.log10(1 + 1 / np.arange(1, 10)) * 100
    tab = {"Benford esperado %": ben.round(1)}
    for c, n in [("V_13", "Lula %"), ("V_22", "Flávio %")]:
        x = d[c][d[c] > 0].astype(int).astype(str).str[0].astype(int)
        tab[n] = (x.value_counts(normalize=True).sort_index().reindex(range(1, 10), fill_value=0) * 100).round(1).values
    out(md(pd.DataFrame(tab, index=range(1, 10))))
    out()
    out("Os dois candidatos \"falham\" do mesmo jeito. Isso é esperado: a seção tem um teto "
        "de cerca de 400 eleitores, então a contagem por seção cai quase sempre entre 100 e "
        "199 e o dígito 1 domina. A literatura considera o 1º dígito de Benford inadequado "
        "para contagens por seção eleitoral (Deckert, Myagkov & Ordeshook, 2011). Esse "
        "teste não serve como evidência para nenhum dos lados.")
    out()

    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
