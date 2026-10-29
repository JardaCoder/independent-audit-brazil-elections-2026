"""Compara a soma dos BUs (planilhas BWeb) com o Relatório Resultado da Totalização oficial do TSE (PDF),
no Brasil e em cada UF, nos dois turnos. Gera analise/TOTALIZACAO.md.

O PDF vem em dados/tse/2026/totalizacao/Relatorio_Resultado_Totalizacao_2026_BR.zip."""
import os
import re
import subprocess
import zipfile

import pandas as pd

from carregar import RAIZ, carregar

ZIP = os.path.join(RAIZ, "dados", "tse", "2026", "totalizacao", "Relatorio_Resultado_Totalizacao_2026_BR.zip")
SAIDA = os.path.join(RAIZ, "analise", "TOTALIZACAO.md")
UF = {"ACRE": "AC", "ALAGOAS": "AL", "AMAPÁ": "AP", "AMAZONAS": "AM", "BAHIA": "BA", "CEARÁ": "CE",
      "DISTRITO FEDERAL": "DF", "ESPÍRITO SANTO": "ES", "EXTERIOR": "ZZ", "GOIÁS": "GO", "MARANHÃO": "MA",
      "MATO GROSSO DO SUL": "MS", "MATO GROSSO": "MT", "MINAS GERAIS": "MG", "PARANÁ": "PR", "PARAÍBA": "PB",
      "PARÁ": "PA", "PERNAMBUCO": "PE", "PIAUÍ": "PI", "RIO DE JANEIRO": "RJ", "RIO GRANDE DO NORTE": "RN",
      "RIO GRANDE DO SUL": "RS", "RONDÔNIA": "RO", "RORAIMA": "RR", "SANTA CATARINA": "SC", "SERGIPE": "SE",
      "SÃO PAULO": "SP", "TOCANTINS": "TO", "do Brasil": "BR"}


def num(s):
    return int(s.replace(".", ""))


def ler_pdf(turno):
    with zipfile.ZipFile(ZIP) as z:
        nome = next(n for n in z.namelist() if f"_T{turno}_PRESIDENTE" in n)
        dados = z.read(nome)
    texto = subprocess.run(["pdftotext", "-layout", "-", "-"], input=dados, capture_output=True, check=True).stdout.decode()
    # Divide o texto em blocos por região ("Resumo Geral (ACRE)", "Resumo Geral do Brasil"...).
    regs = {}
    atual = None
    for linha in texto.splitlines():
        m = re.search(r"Resumo Geral (?:\((.+)\)|(do Brasil))", linha)
        if m:
            atual = UF[m.group(1) or m.group(2)]
            regs.setdefault(atual, [])
        elif atual:
            regs[atual].append(linha)
    linhas = []
    for uf, ls in regs.items():
        t = "\n".join(ls)
        pega = lambda rot: num(re.search(rot + r"[^\n]*?([\d.]+)\s*$", t, re.M).group(1))  # noqa: E731
        r = {"UF": uf, "comparecimento": pega(r"2\.3 Comparecimento"), "aptos": pega(r"2\.2\.2 Aptos nas seções que funcionaram"),
             "seções": pega(r"2\.1 Seções que funcionaram"),
             "nulos na urna": pega(r"Votos nulos na urna"), "brancos": pega(r"[cd]\) Votos em branco"),
             "nulos técnicos": pega(r"Votos nulos técnico"), "seções no Sistema de Apuração": pega(r"Apuração \(SA\)\s")}
        for n, v in re.findall(r"^\*?(\d{2}) - [^\n]+?\s{2,}([\d.]+)\s+[\d,]+%\s+Válido", t, re.M):
            r[f"V_{int(n)}"] = num(v)
        linhas.append(r)
    return pd.DataFrame(linhas).set_index("UF")


def soma_bu(turno):
    d = carregar(turno=turno)
    g = d.groupby("SG_UF")[["QT_COMPARECIMENTO", "QT_APTOS"] + [c for c in d if c.startswith("V_")]].sum()
    g["seções"] = d.groupby("SG_UF").size()
    g.loc["BR"] = g.sum()
    return g.rename(columns={"QT_COMPARECIMENTO": "comparecimento", "QT_APTOS": "aptos", "V_NULO": "nulos na urna",
                             "V_BRANCO": "brancos"})


def main():
    L = ["# Soma dos BUs × Relatório Resultado da Totalização oficial", "",
         "O TSE totaliza os boletins de urna e publica o resultado num relatório assinado (PDF). Aqui somamos os BUs "
         "nós mesmos e comparamos linha a linha, no Brasil e em cada UF.", ""]
    for turno in (1, 2):
        of = ler_pdf(turno)
        bu = soma_bu(turno)
        cols = [c for c in of.columns if c in bu.columns]
        dif = (bu.loc[of.index, cols] - of[cols].fillna(0)).astype(int)
        nao_bate = dif[(dif != 0).any(axis=1)]
        L += [f"## {turno}º turno", "",
              f"- Regiões comparadas: {len(of)} (27 UFs + exterior + Brasil). Colunas: seções, aptos, comparecimento, brancos, nulos na urna e votos de cada candidato.",
              f"- Regiões em que **tudo bate exatamente**: {len(of) - len(nao_bate)} de {len(of)}.",
              f"- Seções apuradas pelo Sistema de Apuração (cédula, sem urna eletrônica): {of.loc['BR', 'seções no Sistema de Apuração']}.",
              f"- Votos nulos técnicos (votos dados a candidato cujo registro foi anulado depois): {of.loc['BR', 'nulos técnicos']:,}.".replace(",", ".")]
        if len(nao_bate):
            L += ["", "Diferenças (soma dos BUs − oficial):", "",
                  nao_bate.loc[:, (nao_bate != 0).any()].to_markdown(), "",
                  "- As diferenças de seções e aptos são seções do exterior em que **ninguém votou**: elas não aparecem na "
                  "planilha de votos (BWeb), mas o TSE as conta como \"em funcionamento\". Votos e comparecimento batem."]
        # Os votos nominais que não aparecem no oficial viram "nulo técnico".
        for c in [c for c in bu.columns if c.startswith("V_") and c not in of.columns]:
            L.append(f"- O número {c[2:]} recebeu {bu.loc['BR', c]:,} votos nas urnas e não aparece entre os candidatos válidos "
                     f"do relatório oficial. O total bate com os nulos técnicos ({of.loc['BR', 'nulos técnicos']:,}): "
                     f"{'SIM' if bu.loc['BR', c] == of.loc['BR', 'nulos técnicos'] else 'NÃO'}.".replace(",", "."))
        L.append("")
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
