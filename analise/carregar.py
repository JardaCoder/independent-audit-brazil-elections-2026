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

# Fuso local da urna em relação a Brasília (horas a SOMAR ao relógio da urna para obter Brasília).
# DT_ABERTURA/DT_ENCERRAMENTO são gravados no relógio local da urna. Conferido pela hora de abertura:
# todas as urnas abrem às 8h de Brasília, então abrem às 7h locais em UTC-4, às 6h em UTC-5 e às 9h em UTC-2.
FUSO = {"AC": 2, "AM": 1, "MT": 1, "MS": 1, "RO": 1, "RR": 1}
# Municípios do oeste do Amazonas em UTC-5 (restabelecido pela Lei 12.876/2013) e Fernando de Noronha (UTC-2).
FUSO_MUNICIPIO = {("AM", m): 2 for m in ["AMATURÁ", "ATALAIA DO NORTE", "BENJAMIN CONSTANT", "EIRUNEPÉ", "ENVIRA",
                                          "GUAJARÁ", "IPIXUNA", "ITAMARATI", "JUTAÍ", "SÃO PAULO DE OLIVENÇA", "TABATINGA"]}
FUSO_MUNICIPIO[("PE", "FERNANDO DE NORONHA")] = -1

# Faixas de horário de encerramento usadas em todas as análises (início incluso, fim excluso).
FAIXAS_SEG = [0, 17 * 3600 + 60, 17 * 3600 + 16 * 60, 19 * 3600, 20 * 3600, 86400]
FAIXAS_ROTULO = ["até 17:00:59", "17:01 a 17:15:59", "17:16 a 18:59:59", "19:00 a 19:59:59", "20:00 ou depois"]


def fuso(df):
    """Horas a somar ao relógio da urna; NaN para o exterior (cada país tem seu fuso)."""
    f = [FUSO_MUNICIPIO.get(k, FUSO.get(k[0], 0)) for k in zip(df["SG_UF"], df["NM_MUNICIPIO"])]
    return pd.Series(f, index=df.index, dtype=float).where(df["SG_UF"] != "ZZ")


def faixa_horario(horario):
    """Classifica uma série de datetimes nas FAIXAS (pelo horário do dia)."""
    seg = (horario - horario.dt.normalize()).dt.total_seconds()
    return pd.cut(seg, FAIXAS_SEG, right=False, labels=FAIXAS_ROTULO)


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
    for c in ["QT_APTOS", "QT_COMPARECIMENTO", "QT_VOTOS", "NR_VOTAVEL", "QT_ELEI_BIOM_SEM_HABILITACAO"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")  # "#NULO#" vira NaN
    chave = ["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
    # campos da seção se repetem em cada linha de votável: um valor por seção
    meta = df.groupby(chave, as_index=False)[["QT_APTOS", "QT_COMPARECIMENTO", "DS_TIPO_URNA", "DT_ABERTURA",
                                             "DT_ENCERRAMENTO", "DT_BU_RECEBIDO", "QT_ELEI_BIOM_SEM_HABILITACAO"]].first()
    meta = meta.rename(columns={"QT_ELEI_BIOM_SEM_HABILITACAO": "QT_BIOM_SEM_HAB"})
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
        v = [c for c in df if c.startswith("V_")]
        df[v] = df[v].fillna(0)
    else:
        partes = [_ler_uf(z) for z in sorted(glob.glob(os.path.join(pasta, f"bweb_presidente_{turno}t_*.csv.gz")))]
        df = pd.concat(partes, ignore_index=True)
        v = [c for c in df if c.startswith("V_")]
        df[v] = df[v].fillna(0).astype(int)
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        df.to_csv(cache, index=False, compression="gzip")
    # 2026 vem em ISO (aaaa-mm-dd); 2022, em dd/mm/aaaa. dayfirst=True em ISO trocaria dia e mês (04/10 → 10/04).
    iso = df["DT_ENCERRAMENTO"].dropna().iloc[0][:4].isdigit()
    df["ENC_LOCAL"] = pd.to_datetime(df["DT_ENCERRAMENTO"], errors="coerce", format="ISO8601" if iso else "%d/%m/%Y %H:%M:%S")
    df["ENC_BRASILIA"] = df["ENC_LOCAL"] + pd.to_timedelta(fuso(df), unit="h")
    return df


if __name__ == "__main__":
    d = carregar(usar_cache=False)
    print(d.shape)
    print(d.head().T)
