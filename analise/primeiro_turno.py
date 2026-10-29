"""1º turno de 2026 e comparação seção a seção com o 2º turno. Gera analise/PRIMEIRO_TURNO.md.

Ideia: a mesma seção, com os mesmos eleitores, votou duas vezes com 3 semanas de intervalo. Um modelo que
prevê o 2º turno a partir do 1º mostra se algum grupo de seções (fechamento tardio, muita liberação manual)
se afastou do padrão no 2º turno. O teste só enxerga desvios DIFERENCIAIS entre grupos de seções (ver limites)."""
import os

import numpy as np
import pandas as pd

from carregar import RAIZ, carregar, faixa_horario
from estatistica import (NULO_TECNICO_1T, ajustar, centrar, coef_cluster, desvio_grupo, especificacoes, fmt, junta_turnos,
                         limite_tardias, md)

SAIDA = os.path.join(RAIZ, "analise", "PRIMEIRO_TURNO.md")
L = []


def out(s=""):
    L.append(s)


def grupos_teste(m):
    seg_b = (m.ENC_BRASILIA_2 - m.ENC_BRASILIA_2.dt.normalize()).dt.total_seconds()
    seg_l = (m.ENC_LOCAL_2 - m.ENC_LOCAL_2.dt.normalize()).dt.total_seconds()
    return {
        "fechou às 19h ou depois (Brasília)": seg_b >= 19 * 3600,
        "fechou até 17:00:59 (relógio local)": seg_l < 17 * 3600 + 60,
        "liberação manual ≥ 20% da seção (2º turno)": m.bio_2 >= 0.20,
    }


def main():
    t1 = carregar(turno=1)
    t2 = carregar(turno=2)
    out("# 1º turno de 2026 e comparação com o 2º turno")
    out()
    out("Fonte: BWeb de Presidente do 1º turno (04/10/2026) e do 2º turno (25/10/2026), extraídos dos .zip oficiais "
        "conferidos com o SHA-512 do TSE (`dados/tse/2026/presidente/`).")
    out()

    # ---------------- 1. resultado
    nominais = [c for c in t1 if c.startswith("V_") and c not in ("V_BRANCO", "V_NULO")]
    validos = [c for c in nominais if c not in NULO_TECNICO_1T]
    tot = t1[validos].sum().sort_values(ascending=False)
    nt = int(t1[[c for c in NULO_TECNICO_1T if c in t1]].sum().sum())
    out("## 1. Resultado do 1º turno (soma dos BUs)")
    out()
    out(f"Seções com voto: {fmt(len(t1))} · comparecimento: {fmt(t1.QT_COMPARECIMENTO.sum())} · válidos: {fmt(tot.sum())} · "
        f"brancos: {fmt(t1.V_BRANCO.sum())} · nulos na urna: {fmt(t1.V_NULO.sum())} · nulos técnicos (nº 28, registro anulado): {fmt(nt)}")
    out()
    res = pd.DataFrame({"votos": tot.astype(int)})
    res["% válidos"] = (res.votos / tot.sum() * 100).round(2)
    res.index = [i.replace("V_", "nº ") for i in res.index]
    out(md(res.head(8)))
    out()
    out("O TSE conta 499.207 seções em funcionamento. A diferença é a seção 91 de Ciudad Guayana (exterior, 72 aptos), "
        "que não aparece no BWeb do 1º turno (ninguém votou).")
    out()

    # ---------------- 2. horários e biometria
    out("## 2. Horário de fechamento e liberação manual nos dois turnos")
    out()
    out("Faixas pelo horário de **Brasília** (exterior fora: cada país tem seu fuso). % Lula = Lula ÷ (Lula + Flávio).")
    out()
    linhas = []
    for nome, d in [("1º turno", t1), ("2º turno", t2)]:
        g = d.assign(f=faixa_horario(d.ENC_BRASILIA)).groupby("f", observed=False).agg(
            secoes=("V_13", "size"), lula=("V_13", "sum"), flavio=("V_22", "sum"))
        for f, r in g.iterrows():
            linhas.append({"turno": nome, "faixa (Brasília)": f, "seções": int(r.secoes),
                           "% Lula": round(r.lula / (r.lula + r.flavio) * 100, 2)})
    out(md(pd.DataFrame(linhas), index=False))
    out()
    for nome, d in [("1º turno", t1), ("2º turno", t2)]:
        mi = d.ENC_BRASILIA.dt.hour * 60 + d.ENC_BRASILIA.dt.minute
        out(f"- {nome}: fecharam no minuto 19:00 exato {fmt((mi == 19 * 60).sum())} seções; entre 18:50 e 19:10, "
            f"{fmt(mi.between(18 * 60 + 50, 19 * 60 + 10).sum())}; liberação manual: {fmt(d.QT_BIOM_SEM_HAB.sum())} "
            f"({d.QT_BIOM_SEM_HAB.sum() / d.QT_COMPARECIMENTO.sum() * 100:.2f}% do comparecimento).")
    out("- No 1º turno houve **mais** seções fechando às 19h ou depois do que no 2º, mas como uma cauda contínua de filas "
        "(5 cargos para votar). O que só existe no 2º turno é o **pico concentrado às 19h00**.")
    out()

    # ---------------- 3. mesmas seções
    m = junta_turnos()
    tarde1 = m.ENC_BRASILIA_1.dt.hour >= 19
    tarde2 = m.ENC_BRASILIA_2.dt.hour >= 19
    out("## 3. As mesmas seções nos dois turnos")
    out()
    out(f"- Seções comparáveis: {fmt(len(m))}. Aptos iguais nos dois turnos: {(m.QT_APTOS_1 == m.QT_APTOS_2).mean() * 100:.1f}% "
        "(a diferença vem do voto em trânsito, que muda entre os turnos).")
    out(f"- Seções que fecharam às 19h ou depois nos dois turnos: {fmt((tarde1 & tarde2).sum())}. Se não houvesse relação "
        f"nenhuma, o esperado ao acaso seria {tarde1.sum() * tarde2.sum() / len(m):.0f}. São outros locais.")
    out(f"- Correlação, por seção, entre a taxa de liberação manual do 1º e do 2º turno: **{np.corrcoef(m.bio_1, m.bio_2)[0, 1]:.2f}**. "
        "A taxa é uma característica estável da seção.")
    out()

    # ---------------- 4. modelo
    out("## 4. Modelo: o 2º turno é previsível pelo 1º?")
    out()
    out("Para cada seção, prevemos a % de Lula (entre Lula e Flávio) no 2º turno usando só o 1º turno da mesma seção: "
        "fatia de cada candidato, de branco+nulo e de abstenção. Duas formas: **linear** (frações dos aptos) e **logit** "
        "(log da razão Lula/Flávio; frações do comparecimento + taxa de abstenção). \"Dentro do município\" = compara "
        "só seções da mesma cidade (efeito fixo), o que tira a diferença entre regiões.")
    out()
    specs = especificacoes(m)
    resid, r2s = {}, []
    for nome, (tipo, g, p) in specs.items():
        prev, r, r2 = ajustar(m, tipo, g, p)
        resid[nome] = r
        r2s.append({"modelo": nome, "variação explicada (R²)": round(r2, 3), "erro típico (p.p.)": round(r.std(), 2)})
        if nome == "linear, nacional":
            m["prev"] = prev
    out(md(pd.DataFrame(r2s), index=False))
    out()
    r2_1 = np.corrcoef(m.lula_1, m.lula_2)[0, 1] ** 2  # R² da reta com uma variável
    out(f"- Só com a % de Lula entre Lula e Flávio no 1º turno (uma variável) o R² nacional já é {r2_1:.3f}; o modelo "
        "usa essa variável mais as fatias de cada candidato, brancos, nulos e abstenção. O número que importa é o "
        "**dentro do município**: mostra quanto o 1º turno explica comparando só seções da mesma cidade.")
    out()

    # ---------------- 5. testes por grupo
    out("## 5. Algum grupo de seções se desviou da previsão?")
    out()
    out("Resíduo = % real de Lula − % prevista, em pontos percentuais (p.p.). A tabela mostra a diferença média do resíduo "
        "entre o grupo e as demais seções, com o erro-padrão (EP) agrupado por município entre parênteses. Um valor "
        "positivo e grande indicaria Lula acima do esperado no grupo.")
    out()
    tabela = []
    for gnome, mask in grupos_teste(m).items():
        lin = {"grupo": gnome, "seções": int(mask.sum())}
        for snome, r in resid.items():
            b, se = desvio_grupo(m, r, snome, mask)
            lin[snome] = f"{b:+.2f} ({se:.2f})"
        tabela.append(lin)
    out(md(pd.DataFrame(tabela), index=False))
    out()
    mask = grupos_teste(m)["fechou às 19h ou depois (Brasília)"]
    lim, votos = limite_tardias(m, resid)
    sig = [n for n, r in resid.items() if (lambda b, se: b - 1.96 * se > 0)(*desvio_grupo(m, r, n, mask))]
    out(f"- Seções tardias: desvio a favor de Lula distinguível de zero em {len(sig)} das {len(resid)} formas"
        f"{' (' + ', '.join(sig) + ')' if sig else ''}. "
        f"No pior caso (limite superior de 95% da especificação mais desfavorável, {lim:+.2f} p.p.), o efeito sobre a "
        f"margem seria de no máximo **{fmt(votos)} votos** (2 × {lim:.2f}% × {fmt(m.loc[mask, 'validos_2'].sum())} válidos).")
    for nome, var in [("nível da liberação manual no 2º turno", m.bio_2), ("variação da liberação manual do 1º para o 2º turno", m.bio_2 - m.bio_1)]:
        cols = []
        for snome in ["linear, dentro do município", "logit, dentro do município"]:
            b, se = coef_cluster(centrar(resid[snome], m.mun), centrar(var * 10, m.mun), m.mun)
            cols.append(f"{snome}: {b:+.3f} p.p. (EP {se:.3f})")
        out(f"- Efeito no resíduo de +10 p.p. de **{nome}**: " + "; ".join(cols) + ".")
    out("- Se a liberação manual fosse usada para pôr votos em Lula, mais liberação deveria vir com resíduo positivo, "
        "sobretudo onde ela **aumentou** do 1º para o 2º turno. Não é o que aparece.")
    out()

    # ---------------- 6. diferença-em-diferenças
    out("## 6. Comparação simples: o grupo já votava diferente no 1º turno?")
    out()
    def p(x, t):
        return x[f"V_13_{t}"].sum() / (x[f"V_13_{t}"] + x[f"V_22_{t}"]).sum() * 100

    linhas = []
    for gnome, mask in grupos_teste(m).items():
        a, b = m[mask], m[~mask & m.mun.isin(m.loc[mask, "mun"])]
        linhas.append({"grupo": gnome, "Lula 1º turno (grupo)": round(p(a, 1), 2), "Lula 2º turno (grupo)": round(p(a, 2), 2),
                       "variação grupo": round(p(a, 2) - p(a, 1), 2),
                       "Lula 1º (demais, mesmos municípios)": round(p(b, 1), 2), "Lula 2º (demais)": round(p(b, 2), 2),
                       "variação demais": round(p(b, 2) - p(b, 1), 2)})
    out(md(pd.DataFrame(linhas), index=False))
    out()
    out("Lula entre Lula e Flávio (somando os votos do grupo). Se a variação do grupo é igual à das demais seções dos "
        "mesmos municípios, o grupo não teve nada de especial no 2º turno: já votava diferente antes.")
    out()

    # ---------------- 7. seções fora do padrão
    out("## 7. Seções muito fora do padrão")
    out()
    r = resid["linear, dentro do município"]
    sd = r.std()
    z_bin = (r / 100) / np.sqrt((m.prev / 100 * (1 - m.prev / 100)).clip(lower=0.01) / m.validos_2)
    linhas = []
    for k in (2, 3, 4, 5):
        for nome, sel in [("resíduo > k desvios", r.abs() > k * sd), ("resíduo padronizado pelo tamanho da seção > k", z_bin.abs() > k)]:
            x = m[sel]
            efeito = (r[sel] / 100) * x.validos_2 * 2
            linhas.append({"critério": nome, "k": k, "seções": int(sel.sum()), "a favor de Lula": int((r[sel] > 0).sum()),
                           "a favor de Flávio": int((r[sel] < 0).sum()), "efeito bruto a favor de Lula (votos)": int(efeito[efeito > 0].sum()),
                           "efeito líquido (votos)": int(efeito.sum())})
    out(md(pd.DataFrame(linhas), index=False))
    out()
    out("Efeito = quanto a margem mudaria se todo o desvio dessas seções fosse removido (2 × resíduo × válidos). "
        "\"Bruto\" soma só os desvios a favor de Lula, sem descontar os a favor de Flávio.")
    fora = m[r.abs() > 4 * sd].assign(residuo=r, residuo_nacional=resid["linear, nacional"])
    fora[["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "QT_COMPARECIMENTO_2", "V_13_2", "V_22_2",
          "residuo", "residuo_nacional"]].sort_values("residuo").to_csv(
        os.path.join(RAIZ, "analise", "secoes_fora_do_padrao_1t_2t.csv"), index=False)
    out("- Lista (critério 4 desvios): `secoes_fora_do_padrao_1t_2t.csv`.")
    zz = m[(m.SG_UF == "ZZ") & (resid["linear, nacional"] < -12)]
    out(f"- No modelo linear nacional, há um aglomerado de seções com Lula muito abaixo do previsto: {fmt(len(zz))} são do "
        f"exterior (principalmente {', '.join(zz.NM_MUNICIPIO.value_counts().head(4).index.str.title())}), com abstenção média "
        f"de {(1 - zz.QT_COMPARECIMENTO_1 / zz.QT_APTOS_1).mean() * 100:.0f}% no 1º turno. O modelo linear trata parte da "
        "abstenção como voto futuro, o que não vale no exterior. É limitação do modelo, e o desvio é contra Lula.")
    out()

    # ---------------- 8. limites
    out("## 8. O que este teste não detecta")
    out()
    out("- Manipulação **igual em todas as seções** do país (seria absorvida pelos coeficientes do modelo). "
        "Coberta por outro teste: a soma dos BUs bate com o resultado oficial e os BUs batem com os logs das urnas.")
    out("- Manipulação que também tenha ocorrido no **1º turno** (fica embutida na previsão).")
    out("- Manipulação do **município inteiro** (a coluna \"dentro do município\" não a vê; a nacional sim).")
    out("- Os coeficientes do modelo não são taxas de transferência de votos e não devem ser interpretados um a um.")
    out()

    # ---------------- 9. por UF
    out("## 9. Do 1º para o 2º turno, por UF")
    out()
    u1 = t1.groupby("SG_UF")[validos + ["QT_COMPARECIMENTO"]].sum()
    u2 = t2.groupby("SG_UF")[["V_13", "V_22", "QT_COMPARECIMENTO"]].sum()
    uf = pd.DataFrame({
        "Lula 1º (% válidos)": (u1.V_13 / u1[validos].sum(axis=1) * 100).round(1),
        "Flávio 1º (% válidos)": (u1.V_22 / u1[validos].sum(axis=1) * 100).round(1),
        "Lula 2º (% válidos)": (u2.V_13 / (u2.V_13 + u2.V_22) * 100).round(1),
        "comparecimento 1º": u1.QT_COMPARECIMENTO.astype(int), "comparecimento 2º": u2.QT_COMPARECIMENTO.astype(int)})
    uf["previsto pelo modelo"] = (m.groupby("SG_UF").apply(lambda x: np.average(x.prev, weights=x.validos_2))).round(1)
    out(md(uf))
    out()
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
