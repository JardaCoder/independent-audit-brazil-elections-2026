"""Confere se cada BU do 2º turno veio da urna (e da carga) que o TSE publicou como esperada em 24/10/2026,
ou de uma urna de contingência publicada na mesma lista. Gera analise/CORRESPONDENCIA.md."""
import glob
import os
import zipfile

import pandas as pd

from carregar import PASTA_BU, RAIZ

PASTA = os.path.join(RAIZ, "dados", "tse", "2026", "correspondencias", "2turno")
SAIDA = os.path.join(RAIZ, "analise", "CORRESPONDENCIA.md")
CHAVE = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]


def ler_csv(zf, prefixo, cols=None):
    nome = next(n for n in zf.namelist() if n.startswith(prefixo) and n.endswith(".csv"))
    with zf.open(nome) as f:
        return pd.read_csv(f, sep=";", encoding="latin1", dtype=str, usecols=cols)


def so_digitos(s):
    return s.fillna("").str.replace(r"\D", "", regex=True).str.zfill(24)


def main():
    linhas, extras, semreg, cargadif = [], [], [], []
    for z in sorted(glob.glob(os.path.join(PASTA, "CESP_2t_*.zip"))):
        with zipfile.ZipFile(z) as zf:
            esp = ler_csv(zf, "csec_")
            cont = ler_csv(zf, "ccont_")
        uf = esp.SG_UF.iloc[0]
        bu_zip = next(glob.iglob(os.path.join(PASTA_BU, f"bweb_2t_{uf}_*.zip")))
        with zipfile.ZipFile(bu_zip) as zf:
            bu = ler_csv(zf, "bweb_", CHAVE + ["CD_CARGO_PERGUNTA", "NR_URNA_EFETIVADA", "CD_CARGA_1_URNA_EFETIVADA", "CD_CARGA_2_URNA_EFETIVADA", "DT_CARGA_URNA_EFETIVADA", "DS_SECOES_AGREGADAS"])
        bu = bu[bu.CD_CARGO_PERGUNTA == "1"].drop_duplicates(CHAVE)
        for df in (esp, bu):
            for c in ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]:
                df[c] = df[c].astype(int)
        m = bu.merge(esp, on=CHAVE, how="outer", indicator=True)
        par = m[m._merge == "both"].copy()
        # O código de carga de 24 dígitos vem dividido em CD_CARGA_1 (18) + CD_CARGA_2 (6)
        par["carga_bu"] = (par.CD_CARGA_1_URNA_EFETIVADA.str.replace(r"\D", "", regex=True)
                           + par.CD_CARGA_2_URNA_EFETIVADA.str.replace(r"\D", "", regex=True)).str.zfill(24)
        par["carga_esp"] = so_digitos(par.CD_CARGA_URNA_ESPERADA)
        mesma_urna = par.NR_URNA_EFETIVADA == par.NR_URNA_ESPERADA
        mesma_carga = par.carga_bu == par.carga_esp
        cont_urnas = set(cont[[c for c in cont.columns if "URNA" in c and c.startswith("NR_")][0]])
        cont_cargas = set(so_digitos(cont[[c for c in cont.columns if c.startswith("CD_CARGA")][0]]))
        trocada = par[~mesma_urna]
        sem_esp = m[m._merge == "left_only"]
        extras.append(sem_esp[CHAVE + ["NR_URNA_EFETIVADA", "DS_SECOES_AGREGADAS"]])
        carga_dif = par[mesma_urna & ~mesma_carga]
        cargadif.append(carga_dif[CHAVE + ["NR_URNA_EFETIVADA", "DT_CARGA_URNA_ESPERADA", "DT_CARGA_URNA_EFETIVADA"]])
        semreg.append(trocada[~trocada.NR_URNA_EFETIVADA.isin(cont_urnas) & ~trocada.carga_bu.isin(cont_cargas)]
                      [CHAVE + ["NR_URNA_ESPERADA", "NR_URNA_EFETIVADA", "DT_CARGA_URNA_ESPERADA", "DT_CARGA_URNA_EFETIVADA"]])
        linhas.append({
            "UF": uf, "seções esperadas": len(esp), "seções com BU": len(bu),
            "BU sem seção esperada": int((m._merge == "left_only").sum()),
            "seção esperada sem BU": int((m._merge == "right_only").sum()),
            "urna = esperada": int(mesma_urna.sum()),
            "carga = esperada": int((mesma_urna & mesma_carga).sum()),
            "urna trocada": len(trocada),
            "…por urna de contingência listada": int(trocada.NR_URNA_EFETIVADA.isin(cont_urnas).sum()),
            "…com carga de contingência listada": int(trocada.carga_bu.isin(cont_cargas).sum()),
            "…urna sem registro prévio": int((~trocada.NR_URNA_EFETIVADA.isin(cont_urnas) & ~trocada.carga_bu.isin(cont_cargas)).sum()),
        })
    t = pd.DataFrame(linhas).set_index("UF")
    t.loc["Total"] = t.sum()
    txt = ("# Correspondência esperada × BU — 2º turno 2026\n\n"
           "Fonte: arquivos CESP publicados pelo TSE em 24/10/2026, véspera da eleição, com a urna e o código "
           "de carga esperados em cada seção, mais a lista das urnas de contingência.\n\n" + t.to_markdown() + "\n")
    ex = pd.concat(extras)
    sr = pd.concat(semreg)
    cd = pd.concat(cargadif)
    flag = pd.concat([ex.assign(motivo="BU de seção fora da lista esperada"),
                      sr.assign(motivo="urna trocada por urna fora da lista de contingência"),
                      cd.assign(motivo="mesma urna, código de carga diferente do esperado")])
    from carregar import carregar
    sec = carregar()
    for c in ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]:
        sec[c] = sec[c].astype(int)
    flag = flag.merge(sec[CHAVE + ["NM_MUNICIPIO", "QT_COMPARECIMENTO", "V_13", "V_22"]], on=CHAVE, how="left")
    flag.to_csv(os.path.join(RAIZ, "analise", "secoes_para_documentar.csv"), index=False)
    r = flag.groupby("motivo").agg(secoes=("NR_SECAO", "size"), comparecimento=("QT_COMPARECIMENTO", "sum"),
                                   lula=("V_13", "sum"), flavio=("V_22", "sum"))
    r.loc["Total"] = r.sum()
    r["saldo Lula"] = r.lula - r.flavio
    txt += ("\n## Seções que pedem documentação (lista completa em secoes_para_documentar.csv)\n\n"
            + r.astype(int).to_markdown() + "\n")
    txt += ("\n## Data de carga das urnas trocadas sem registro prévio\n\n"
            + pd.to_datetime(sr.DT_CARGA_URNA_EFETIVADA).dt.date.value_counts().sort_index().to_frame("urnas").to_markdown() + "\n")
    txt += ("\n## BUs sem seção na lista esperada\n\n" + ex.to_markdown(index=False) + "\n"
            "\n## Urnas trocadas sem registro prévio como contingência (amostra)\n\n"
            + sr.head(30).to_markdown(index=False) + "\n")
    print(r.astype(int).to_markdown())
    open(SAIDA, "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
