"""Ferramentas estatísticas usadas pelas análises: junção 1º × 2º turno, modelos de previsão do 2º turno
a partir do 1º, centragem dentro de grupos (efeito fixo) e erro-padrão agrupado (cluster)."""
import os

import numpy as np
import pandas as pd

from carregar import RAIZ, carregar

CHAVE = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
NULO_TECNICO_1T = ["V_28"]  # candidato com registro anulado: votos viraram "nulos técnicos" no oficial


def fmt(n):
    return f"{n:,.0f}".replace(",", ".")


def md(df, index=True):
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_integer_dtype(df[c]):
            df[c] = df[c].map(fmt)
    return df.to_markdown(index=index, disable_numparse=True)


def centrar(x, grupos, peso=None):
    """Subtrai a média do grupo (equivale a um efeito fixo), ponderada por `peso` se houver. x: Series ou DataFrame."""
    w = pd.Series(1.0 if peso is None else np.asarray(peso, float), index=x.index)
    g = np.zeros(len(x)) if grupos is None else np.asarray(grupos)
    soma = lambda v: v.groupby(g).transform("sum")  # noqa: E731
    return x - soma(x.mul(w, axis=0)).div(soma(w), axis=0)


def coef_cluster(y, x, cluster, peso=None):
    """Regressão simples y ~ x (já centrados) com erro-padrão agrupado por `cluster`."""
    w = np.ones(len(y)) if peso is None else np.asarray(peso, float)
    y, x = np.asarray(y, float), np.asarray(x, float)
    sxx = (w * x * x).sum()
    b = (w * x * y).sum() / sxx
    u = y - b * x
    s = pd.Series(w * x * u).groupby(np.asarray(cluster)).sum()
    se = np.sqrt((s ** 2).sum()) / sxx
    return b, se


def junta_turnos():
    """Uma linha por seção com o 1º turno (sufixo _1) e o 2º turno (_2) de 2026."""
    t1, t2 = carregar(turno=1), carregar(turno=2)
    for d in (t1, t2):
        for c in ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]:
            d[c] = d[c].astype(int)
    v1 = [c for c in t1 if c.startswith("V_")]
    t1 = t1.rename(columns={c: c + "_1" for c in v1 + ["QT_APTOS", "QT_COMPARECIMENTO", "QT_BIOM_SEM_HAB",
                                                       "ENC_LOCAL", "ENC_BRASILIA", "DT_ABERTURA", "DT_ENCERRAMENTO"]})
    t2 = t2.rename(columns={c: c + "_2" for c in ["V_13", "V_22", "V_BRANCO", "V_NULO", "QT_APTOS", "QT_COMPARECIMENTO",
                                                   "QT_BIOM_SEM_HAB", "ENC_LOCAL", "ENC_BRASILIA", "DT_ABERTURA",
                                                   "DT_ENCERRAMENTO"]})
    m = t1.drop(columns=["NM_MUNICIPIO", "DS_TIPO_URNA", "DT_BU_RECEBIDO"]).merge(t2, on=CHAVE)
    m["mun"] = m.SG_UF + "-" + m.CD_MUNICIPIO.astype(str)
    m["validos_2"] = m.V_13_2 + m.V_22_2
    m["lula_2"] = m.V_13_2 / m.validos_2
    m["lula_1"] = m.V_13_1 / (m.V_13_1 + m.V_22_1)
    m["bio_1"] = m.QT_BIOM_SEM_HAB_1 / m.QT_COMPARECIMENTO_1
    m["bio_2"] = m.QT_BIOM_SEM_HAB_2 / m.QT_COMPARECIMENTO_2
    return m[(m.validos_2 > 0) & (m.QT_COMPARECIMENTO_1 > 0) & ((m.V_13_1 + m.V_22_1) > 0)].copy()


def regressores(m):
    """Fatias do 1º turno + o próprio Lula × Flávio do 1º turno (sozinho já prevê melhor que as fatias).
    Linear: frações dos aptos (somam 1) + lula_1. Logit: frações do comparecimento + abstenção + log(Lula/Flávio)."""
    nominais = [c for c in m if c.startswith("V_") and c.endswith("_1") and c not in ("V_BRANCO_1", "V_NULO_1")
                and c[:-2] not in NULO_TECNICO_1T]
    principais = list(m[nominais].sum().sort_values(ascending=False).index[:6])
    outros = [c for c in nominais if c not in principais]
    base = pd.DataFrame({c[:-2].replace("V_", "nº "): m[c] for c in principais})
    base["outros"] = m[outros].sum(axis=1)
    base["branco+nulo"] = m.V_BRANCO_1 + m.V_NULO_1 + m[[c + "_1" for c in NULO_TECNICO_1T if c + "_1" in m]].sum(axis=1)
    lin = base.assign(abstencao=m.QT_APTOS_1 - m.QT_COMPARECIMENTO_1).div(m.QT_APTOS_1, axis=0)
    lin["lula_1"] = m.lula_1
    lgt = base.div(m.QT_COMPARECIMENTO_1, axis=0)
    lgt["abstencao"] = 1 - m.QT_COMPARECIMENTO_1 / m.QT_APTOS_1
    lgt["log_lula_flavio_1"] = np.log((m.V_13_1 + 0.5) / (m.V_22_1 + 0.5))
    return lin, lgt


def ajustar(m, tipo="linear", grupos=None, peso=False):
    """Prevê a % de Lula (entre Lula e Flávio) no 2º turno a partir do 1º turno da mesma seção.

    tipo: 'linear' (% direto) ou 'logit' (log(Lula/Flávio), com 0,5 somado às contagens).
    grupos: None (nacional), Series de UF ou de município (efeito fixo: compara só dentro do grupo).
    Devolve (previsto em %, resíduo em pontos percentuais, R²)."""
    lin, lgt = regressores(m)
    w = m.validos_2.values if peso else np.ones(len(m))
    if tipo == "linear":
        X, y = lin.values, m.lula_2.values
    else:
        X = lgt.values
        y = np.log((m.V_13_2 + 0.5) / (m.V_22_2 + 0.5)).values
    if grupos is not None:
        Xc = centrar(pd.DataFrame(X, index=m.index), grupos, w).values
        yc = centrar(pd.Series(y, index=m.index), grupos, w).values
    else:
        Xc, yc = X, y
    sw = np.sqrt(w)
    coef, *_ = np.linalg.lstsq(Xc * sw[:, None], yc * sw, rcond=None)
    ajuste = y - (yc - Xc @ coef)  # previsão no nível original (média do grupo + parte explicada)
    prev = ajuste if tipo == "linear" else 1 / (1 + np.exp(-ajuste))
    res = m.lula_2.values - prev
    base = centrar(m.lula_2, grupos, w).values
    r2 = 1 - (res ** 2 * w).sum() / (base ** 2 * w).sum()
    return pd.Series(prev * 100, index=m.index), pd.Series(res * 100, index=m.index), r2


def locais(ano=2026, turno=2):
    """Número do local de votação (NR_LOCAL_VOTACAO) de cada seção, lido dos BWeb de Presidente (com cache)."""
    cache = os.path.join(RAIZ, "dados", "derivados", f"locais_{turno}t_{ano}.csv.gz")
    if os.path.exists(cache):
        return pd.read_csv(cache, dtype=str)
    pasta = os.path.join(RAIZ, "dados", "tse", str(ano), "presidente", f"{turno}turno")
    partes = [pd.read_csv(os.path.join(pasta, f), sep=";", encoding="latin1", dtype=str,
                          usecols=CHAVE + ["NR_LOCAL_VOTACAO"]).drop_duplicates()
              for f in sorted(os.listdir(pasta)) if f.endswith(".csv.gz")]
    d = pd.concat(partes)
    d.to_csv(cache, index=False, compression="gzip")
    return d


def especificacoes(m):
    """As seis formas do modelo usadas nos testes (nome -> (tipo, efeito fixo, ponderado))."""
    return {
        "linear, nacional": ("linear", None, False), "linear, nacional, ponderado": ("linear", None, True),
        "linear, dentro da UF": ("linear", m.SG_UF, False), "linear, dentro do município": ("linear", m.mun, False),
        "logit, nacional": ("logit", None, True), "logit, dentro do município": ("logit", m.mun, True),
    }


def desvio_grupo(m, resid, nome_spec, mask, peso=None, cluster=None):
    """Diferença média do resíduo entre o grupo e as demais seções, com EP agrupado (por município, salvo aviso)."""
    fe = m.mun if "município" in nome_spec else (m.SG_UF if "UF" in nome_spec else None)
    return coef_cluster(centrar(resid, fe, peso), centrar(mask.astype(float), fe, peso),
                        m.mun if cluster is None else cluster, peso=peso)


def limite_tardias(m, residuos):
    """Maior efeito plausível das seções que fecharam às 19h+ sobre a margem: limite superior de 95% da
    especificação mais desfavorável × válidos do grupo × 2. Testa média simples e ponderada por válidos, e EP
    agrupado por município e por UF: as seções tardias se concentram em poucos municípios, e o EP por UF é mais largo."""
    mask = (m.ENC_BRASILIA_2 - m.ENC_BRASILIA_2.dt.normalize()).dt.total_seconds() >= 19 * 3600
    lim = max(b + 1.96 * se for b, se in (desvio_grupo(m, r, n, mask, p, c) for n, r in residuos.items()
                                          for p in (None, m.validos_2) for c in (m.mun, m.SG_UF)))
    return lim, int(lim / 100 * m.loc[mask, "validos_2"].sum() * 2)
