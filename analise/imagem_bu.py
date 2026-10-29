"""Lê as imagens de BU (imgbu.dat) dos arquivos originais das urnas e compara com a planilha BWeb.

    python3 analise/imagem_bu.py AC RR AP
"""
import os
import re
import sys
import zipfile

import pandas as pd

from carregar import RAIZ, _ler_uf, PASTA_BU

PASTA_URNA = os.path.join(RAIZ, "dados", "tse", "2026", "arquivos_urna", "2turno")
CAMPOS = {
    "aptos": r"Eleitores aptos\s+(\d+)",
    "comparecimento": r"Comparecimento\s+(\d+)",
    "hab_biometrica": r"Habilitação biométrica\s+(\d+)",
    "hab_biografica": r"Habilitação biográfica\s+(\d+)",
    "hab_sem_biometria": r"Habilitação sem biometria\s+(\d+)",
    "faltosos": r"Eleitores faltosos\s+(\d+)",
    "municipio": r"Município\s+(\d+)",
    "zona": r"Zona Eleitoral\s+(\d+)",
    "secao": r"Seção Eleitoral\s+(\d+)",
    "fechamento": r"Horário de fechamento\s+([\d:]+)",
}


def parse(texto):
    r = {k: (m.group(1) if (m := re.search(p, texto)) else None) for k, p in CAMPOS.items()}
    pres = texto.split("PRESIDENTE", 1)[-1].split("Total de votos Nominais")[0] if "PRESIDENTE" in texto else ""
    for num, votos in re.findall(r"^\s+.+?\s+(\d{2})\s+(\d{4})\s*$", pres, re.M):
        r[f"V_{int(num)}"] = int(votos)
    return r


def ler_uf(uf):
    z = zipfile.ZipFile(os.path.join(PASTA_URNA, f"bu_imgbu_logjez_rdv_vscmr_2026_2t_{uf}.zip"))
    linhas = []
    for n in z.namelist():
        if n.endswith("-imgbu.dat"):
            r = parse(z.read(n).decode("latin1"))
            r["arquivo"] = n
            linhas.append(r)
    df = pd.DataFrame(linhas)
    for c in ["aptos", "comparecimento", "hab_biometrica", "hab_biografica", "hab_sem_biometria", "faltosos",
              "municipio", "zona", "secao"]:
        df[c] = pd.to_numeric(df[c])
    return df


def comparar(uf):
    img = ler_uf(uf)
    bweb = _ler_uf(next(os.path.join(PASTA_BU, f) for f in os.listdir(PASTA_BU)
                        if f.startswith(f"bweb_2t_{uf}_") and f.endswith(".zip")))
    for c in ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]:
        bweb[c] = bweb[c].astype(int)
    m = img.merge(bweb, left_on=["municipio", "zona", "secao"], right_on=["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"],
                  how="outer", indicator=True)
    res = {"UF": uf, "imagens de BU": len(img), "seções na BWeb": len(bweb),
           "sem par": int((m._merge != "both").sum())}
    b = m[m._merge == "both"]
    res["comparecimento difere"] = int((b.comparecimento != b.QT_COMPARECIMENTO).sum())
    res["votos Lula diferem"] = int((b.V_13_x.fillna(0) != b.V_13_y).sum())
    res["votos Flávio diferem"] = int((b.V_22_x.fillna(0) != b.V_22_y).sum())
    res["soma hab. = comparecimento"] = int((b.hab_biometrica + b.hab_biografica + b.hab_sem_biometria == b.comparecimento).sum())
    res["BWeb 'sem biometria' = hab. biográfica"] = int((b.QT_BIOM_SEM_HAB == b.hab_biografica).sum())
    res["BWeb 'sem biometria' = hab. sem biometria"] = int((b.QT_BIOM_SEM_HAB == b.hab_sem_biometria).sum())
    res["total hab. biográfica"] = int(b.hab_biografica.sum())
    res["total hab. sem biometria (digital falhou)"] = int(b.hab_sem_biometria.sum())
    res["total campo BWeb"] = int(b.QT_BIOM_SEM_HAB.sum())
    return res, b


if __name__ == "__main__":
    out = []
    for uf in sys.argv[1:] or ["AC"]:
        r, _ = comparar(uf)
        out.append(r)
    print(pd.DataFrame(out).set_index("UF").T.to_markdown())
