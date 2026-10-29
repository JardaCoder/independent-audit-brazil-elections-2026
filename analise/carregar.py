"""Carrega os Boletins de Urna (BWeb) de Presidente numa tabela com uma linha por seção.

Lê os arquivos em dados/tse/<ano>/presidente/<turno>turno/, que são as linhas de Presidente copiadas
sem alteração dos .zip oficiais do TSE (ver scripts/extrair_presidente.py)."""
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


def _ler_uf(caminho):
    # Em 2022 o campo de eleitores não habilitados por biometria chamava-se QT_ELEITORES_BIOMETRIA_NH.
    usar = lambda c: c in COLS or c == "QT_ELEITORES_BIOMETRIA_NH"  # noqa: E731
    if caminho.endswith(".csv.gz"):
        df = pd.read_csv(caminho, sep=";", encoding="latin1", dtype=str, usecols=usar)
    else:  # .zip oficial com todos os cargos
        with zipfile.ZipFile(caminho) as zf:
            nome = next(n for n in zf.namelist() if n.endswith(".csv"))
            with zf.open(nome) as f:
                blocos = pd.read_csv(f, sep=";", encoding="latin1", dtype=str, chunksize=2_000_000, usecols=usar)
                df = pd.concat(b[b["CD_CARGO_PERGUNTA"] == "1"] for b in blocos)
    df = df.rename(columns={"QT_ELEITORES_BIOMETRIA_NH": "QT_ELEI_BIOM_SEM_HABILITACAO"})
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


def carregar(usar_cache=True, ano=2026, turno=2):
    pasta = os.path.join(RAIZ, "dados", "tse", str(ano), "presidente", f"{turno}turno")
    cache = CACHE.replace("2026", str(ano)).replace("_2t_", f"_{turno}t_")
    if usar_cache and os.path.exists(cache):
        df = pd.read_csv(cache, dtype={"CD_MUNICIPIO": str, "NR_ZONA": str, "NR_SECAO": str})
        df[[c for c in df if c.startswith("V_")]] = df[[c for c in df if c.startswith("V_")]].fillna(0)
    else:
        partes = [_ler_uf(z) for z in sorted(glob.glob(os.path.join(pasta, f"bweb_presidente_{turno}t_*.csv.gz")))]
        df = pd.concat(partes, ignore_index=True)
        df[[c for c in df if c.startswith("V_")]] = df[[c for c in df if c.startswith("V_")]].fillna(0).astype(int)
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        df.to_csv(cache, index=False, compression="gzip")
    df["ENC_LOCAL"] = pd.to_datetime(df["DT_ENCERRAMENTO"], errors="coerce", format="mixed", dayfirst=True)
    df["ENC_BRASILIA"] = df["ENC_LOCAL"] + pd.to_timedelta(df["SG_UF"].map(FUSO).fillna(0), unit="h")
    return df


if __name__ == "__main__":
    d = carregar(usar_cache=False)
    print(d.shape)
    print(d.head().T)
