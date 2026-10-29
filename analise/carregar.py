"""Carrega os Boletins de Urna (BWeb) do 2º turno de 2026 numa tabela por seção."""
import glob
import os
import zipfile

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_BU = os.path.join(RAIZ, "dados", "tse", "2026", "boletim_urna", "2turno")
CACHE = os.path.join(RAIZ, "dados", "derivados", "secoes_presidente_2t_2026.csv.gz")

# Fuso local da urna em relação a Brasília (horas a somar para obter horário de Brasília).
# DT_ABERTURA/DT_ENCERRAMENTO são gravados no relógio local da urna.
FUSO = {"AC": 2, "AM": 1, "MT": 1, "MS": 1, "RO": 1, "RR": 1}

COLS = ["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "CD_CARGO_PERGUNTA",
        "QT_APTOS", "QT_COMPARECIMENTO", "DS_TIPO_URNA", "DS_TIPO_VOTAVEL", "NR_VOTAVEL", "QT_VOTOS",
        "DT_ABERTURA", "DT_ENCERRAMENTO", "QT_ELEI_BIOM_SEM_HABILITACAO", "DT_BU_RECEBIDO"]


def _ler_uf(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        nome = next(n for n in zf.namelist() if n.endswith(".csv"))
        with zf.open(nome) as f:
            df = pd.read_csv(f, sep=";", encoding="latin1", usecols=COLS, dtype=str)
    df = df[df["CD_CARGO_PERGUNTA"] == "1"]  # Presidente
    for c in ["QT_APTOS", "QT_COMPARECIMENTO", "QT_VOTOS", "NR_VOTAVEL"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["QT_ELEI_BIOM_SEM_HABILITACAO"] = pd.to_numeric(
        df["QT_ELEI_BIOM_SEM_HABILITACAO"].str.replace("#NULO#", "", regex=False), errors="coerce")
    chave = ["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
    meta = df.groupby(chave, as_index=False).agg(
        QT_APTOS=("QT_APTOS", "first"), QT_COMPARECIMENTO=("QT_COMPARECIMENTO", "first"),
        DS_TIPO_URNA=("DS_TIPO_URNA", "first"), DT_ABERTURA=("DT_ABERTURA", "first"),
        DT_ENCERRAMENTO=("DT_ENCERRAMENTO", "first"), DT_BU_RECEBIDO=("DT_BU_RECEBIDO", "first"),
        QT_BIOM_SEM_HAB=("QT_ELEI_BIOM_SEM_HABILITACAO", "first"))
    nom = df[df["DS_TIPO_VOTAVEL"] == "Nominal"]
    votos = nom.pivot_table(index=chave, columns="NR_VOTAVEL", values="QT_VOTOS",
                            aggfunc="sum", fill_value=0)
    votos.columns = [f"V_{int(c)}" for c in votos.columns]
    outros = df[df["DS_TIPO_VOTAVEL"] != "Nominal"].pivot_table(
        index=chave, columns="DS_TIPO_VOTAVEL", values="QT_VOTOS", aggfunc="sum", fill_value=0)
    outros.columns = [f"V_{c.upper()}" for c in outros.columns]
    return meta.merge(votos.reset_index(), on=chave, how="left").merge(
        outros.reset_index(), on=chave, how="left").fillna({c: 0 for c in list(votos.columns) + list(outros.columns)})


def carregar(usar_cache=True):
    if usar_cache and os.path.exists(CACHE):
        df = pd.read_csv(CACHE, dtype={"CD_MUNICIPIO": str, "NR_ZONA": str, "NR_SECAO": str})
    else:
        partes = [_ler_uf(z) for z in sorted(glob.glob(os.path.join(PASTA_BU, "bweb_2t_*.zip")))]
        df = pd.concat(partes, ignore_index=True)
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        df.to_csv(CACHE, index=False, compression="gzip")
    df["ENC_LOCAL"] = pd.to_datetime(df["DT_ENCERRAMENTO"], errors="coerce")
    df["ENC_BRASILIA"] = df["ENC_LOCAL"] + pd.to_timedelta(df["SG_UF"].map(FUSO).fillna(0), unit="h")
    return df


if __name__ == "__main__":
    d = carregar(usar_cache=False)
    print(d.shape)
    print(d.head().T)
