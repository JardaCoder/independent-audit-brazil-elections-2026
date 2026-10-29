"""Auditoria de consistência interna dos BUs do 2º turno de 2026 (todas as linhas, todos os cargos).
Gera analise/CONSISTENCIA.md."""
import glob
import os
import zipfile

import pandas as pd

from carregar import PASTA_BU, RAIZ

SAIDA = os.path.join(RAIZ, "analise", "CONSISTENCIA.md")
CHAVE = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
NUM = ["QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES", "QT_VOTOS", "QT_ELEI_BIOM_SEM_HABILITACAO"]
DATAS = ["DT_ABERTURA", "DT_ENCERRAMENTO", "DT_EMISSAO_BU", "DT_BU_RECEBIDO", "DT_CARGA_URNA_EFETIVADA"]


def ler(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        nome = next(n for n in zf.namelist() if n.endswith(".csv"))
        with zf.open(nome) as f:
            df = pd.read_csv(f, sep=";", encoding="latin1", dtype=str)
    for c in NUM:
        df[c] = pd.to_numeric(df[c].replace("#NULO#", None), errors="coerce")
    for c in DATAS:
        df[c] = pd.to_datetime(df[c].replace("#NULO#", None), errors="coerce")
    return df


def main():
    checks = {}
    exemplos = []
    secoes_cargo = []
    for z in sorted(glob.glob(os.path.join(PASTA_BU, "bweb_2t_*.zip"))):
        df = ler(z)
        # Uma linha por seção e cargo
        s = df.groupby(CHAVE + ["CD_CARGO_PERGUNTA"], as_index=False).agg(
            aptos=("QT_APTOS", "first"), comp=("QT_COMPARECIMENTO", "first"), abst=("QT_ABSTENCOES", "first"),
            votos=("QT_VOTOS", "sum"), bio=("QT_ELEI_BIOM_SEM_HABILITACAO", "first"),
            n_aptos=("QT_APTOS", "nunique"), n_comp=("QT_COMPARECIMENTO", "nunique"),
            abertura=("DT_ABERTURA", "first"), encerramento=("DT_ENCERRAMENTO", "first"),
            emissao=("DT_EMISSAO_BU", "first"), recebido=("DT_BU_RECEBIDO", "first"),
            carga=("DT_CARGA_URNA_EFETIVADA", "first"), urna=("NR_URNA_EFETIVADA", "first"),
            n_urna=("NR_URNA_EFETIVADA", "nunique"))
        secoes_cargo.append(s)
        regras = {
            "aptos = comparecimento + abstenções": s.aptos != s.comp + s.abst,
            "comparecimento <= aptos": s.comp > s.aptos,
            "soma dos votos (nominais+brancos+nulos) = comparecimento": s.votos != s.comp,
            "sem biometria <= comparecimento": s.bio > s.comp,
            "valores únicos de aptos/comparecimento por BU": (s.n_aptos > 1) | (s.n_comp > 1),
            "abertura < encerramento < emissão do BU": ~((s.abertura < s.encerramento) & (s.encerramento <= s.emissao)),
            "BU recebido depois de emitido": s.recebido < s.emissao - pd.Timedelta(hours=2),
            "carga da urna antes do dia da eleição": s.carga >= pd.Timestamp("2026-10-25"),
            "abertura no dia da eleição": s.abertura.dt.date.astype(str) != "2026-10-25",
            "uma urna por seção": s.n_urna > 1,
        }
        for nome, m in regras.items():
            checks[nome] = checks.get(nome, 0) + int(m.sum())
            if m.any():
                exemplos.append(s[m].head(3).assign(regra=nome))
    todas = pd.concat(secoes_cargo)
    pres = todas[todas.CD_CARGO_PERGUNTA == "1"]
    # Mesma urna em duas seções diferentes (fora seções agregadas, que compartilham urna)
    dup_urna = pres.groupby("urna").size()
    gov = todas[todas.CD_CARGO_PERGUNTA == "3"].merge(pres, on=CHAVE, suffixes=("_gov", "_pres"))

    L = ["# Consistência interna dos BUs — 2º turno 2026", "",
         f"{len(pres):,} seções (Presidente) e {len(todas):,} pares seção×cargo verificados.".replace(",", "."), "",
         "| Regra | Violações |", "|---|---|"]
    for k, v in checks.items():
        L.append(f"| {k} | {v} |")
    L.append(f"| comparecimento igual para Presidente e Governador (UFs com 2º turno estadual) | "
             f"{int((gov.comp_gov != gov.comp_pres).sum())} de {len(gov)} |")
    L.append(f"| mesmo nº de urna em mais de uma seção | {int((dup_urna > 1).sum())} |")
    L += ["", "Horários vêm do relógio local da urna (ver RESULTADOS.md).", ""]
    L += ["## Carga das urnas (DT_CARGA_URNA_EFETIVADA)", "",
          f"De {pres.carga.min()} a {pres.carga.max()}.", ""]
    L += ["## Abertura (relógio local)", "", pres.abertura.dt.strftime("%H").value_counts().sort_index().to_frame("seções").to_markdown(), ""]
    if exemplos:
        L += ["## Exemplos de violações", "", pd.concat(exemplos).head(40).to_markdown(index=False), ""]
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
