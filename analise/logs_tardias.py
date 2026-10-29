"""Lê, direto do servidor do TSE, o log das urnas das seções que fecharam às 19h ou depois no 2º turno
(e de uma amostra de seções vizinhas, do mesmo local de votação, que fecharam às 17h) e conta quantos
votos foram computados depois das 17h, minuto a minuto. Gera analise/LOGS_TARDIAS.md.

Os pacotes de arquivos das urnas têm de 2 a 25 GB por UF. Em vez de baixar tudo, o script lê o índice
do .zip e baixa só os logs necessários, por "download parcial" (HTTP Range).

    python3 analise/logs_tardias.py
"""
import io
import os
import random
import struct
import sys
import urllib.request
import zipfile
import zlib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carregar import FUSO, RAIZ, carregar, fuso  # noqa: E402
from logs_urna import linhas_log  # noqa: E402

URL = "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2026_2t_{}.zip"
SAIDA = os.path.join(RAIZ, "analise", "LOGS_TARDIAS.md")
CACHE = os.path.join(RAIZ, "dados", "derivados", "logs_tardias_2t_2026.csv.gz")
DIA = "25/10/2026"


def baixar_faixa(url, ini, fim, tentativas=5):
    for t in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={ini}-{fim}"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception:
            if t == tentativas - 1:
                raise


class ArquivoRemoto(io.RawIOBase):
    """Arquivo somente-leitura sobre HTTP Range, suficiente para o zipfile ler o índice (central directory)."""

    def __init__(self, url):
        self.url, self.pos = url, 0
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=60) as r:
            self.tamanho = int(r.headers["Content-Length"])

    def seekable(self):
        return True

    def readable(self):
        return True

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.tamanho + off)
        return self.pos

    def tell(self):
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.tamanho - self.pos
        if n == 0:
            return b""
        dados = baixar_faixa(self.url, self.pos, min(self.pos + n, self.tamanho) - 1)
        self.pos += len(dados)
        return dados

    def readinto(self, b):
        d = self.read(len(b))
        b[:len(d)] = d
        return len(d)


def ler_membro(url, info):
    """Baixa um único arquivo de dentro do .zip remoto (cabeçalho local + dados) e descompacta."""
    bruto = baixar_faixa(url, info.header_offset, info.header_offset + 30 + 1024 + info.compress_size)
    n_nome, n_extra = struct.unpack("<HH", bruto[26:30])
    ini = 30 + n_nome + n_extra
    dados = bruto[ini:ini + info.compress_size]
    if info.compress_type == zipfile.ZIP_STORED:
        return dados
    return zlib.decompressobj(-15).decompress(dados)


def analisar_log(jez, fuso):
    """Votos computados por minuto (horário de Brasília) e o momento do comando de encerramento."""
    votos = Counter()
    encerrou = None
    for ln in dict.fromkeys(linhas_log(jez)):
        if not ln.startswith(DIA):
            continue
        p = ln.split("\t")
        if len(p) < 5:
            continue
        h, m = int(p[0][11:13]) + fuso, int(p[0][14:16])
        if p[4] == "O voto do eleitor foi computado":
            votos[h * 60 + m] += 1
        elif p[4].startswith("Encerrar votação") or p[4].startswith("Procedimento de encerramento"):
            encerrou = encerrou or f"{h:02d}:{m:02d}"
    depois = lambda t: sum(v for k, v in votos.items() if k >= t)  # noqa: E731
    ult = max(votos) if votos else None
    return {"votos_log": sum(votos.values()), "votos_apos_17h00": depois(17 * 60), "votos_apos_17h15": depois(17 * 60 + 15),
            "votos_apos_17h30": depois(17 * 60 + 30), "votos_apos_18h00": depois(18 * 60),
            "votos_apos_18h30": depois(18 * 60 + 30),
            "ultimo_voto_brasilia": f"{ult // 60:02d}:{ult % 60:02d}" if ult is not None else None,
            "encerramento_log_brasilia": encerrou,
            "por_minuto": ";".join(f"{k}:{v}" for k, v in sorted(votos.items()) if k >= 17 * 60)}


def selecionar(n_controle=1500, semente=2026):
    d = carregar(turno=2)
    # NR_LOCAL_VOTACAO não está na tabela por seção; vem dos BWeb de Presidente.
    locs = []
    for f in sorted(os.listdir(os.path.join(RAIZ, "dados", "tse", "2026", "presidente", "2turno"))):
        if f.endswith(".csv.gz"):
            x = pd.read_csv(os.path.join(RAIZ, "dados", "tse", "2026", "presidente", "2turno", f), sep=";",
                            encoding="latin1", dtype=str, usecols=["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_LOCAL_VOTACAO"])
            locs.append(x.drop_duplicates())
    loc = pd.concat(locs)
    d = d.merge(loc, on=["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"], how="left")
    seg = (d.ENC_BRASILIA - d.ENC_BRASILIA.dt.normalize()).dt.total_seconds()
    d["grupo"] = None
    d.loc[seg >= 19 * 3600, "grupo"] = "fechou 19h ou depois"
    tardios = d[d.grupo.notna()]
    chave_loc = set(zip(tardios.SG_UF, tardios.CD_MUNICIPIO, tardios.NR_ZONA, tardios.NR_LOCAL_VOTACAO))
    viz = d[d.grupo.isna() & (seg < 17 * 3600 + 15 * 60) &
            pd.Series(list(zip(d.SG_UF, d.CD_MUNICIPIO, d.NR_ZONA, d.NR_LOCAL_VOTACAO)), index=d.index).isin(chave_loc)]
    viz = viz.sample(min(n_controle, len(viz)), random_state=semente)
    d.loc[viz.index, "grupo"] = "vizinha que fechou até 17h15"
    d = d[d.grupo.notna()]
    d = d[d.SG_UF != "ZZ"]
    d["fuso"] = fuso(d)
    d["arquivo"] = ("o03221" + d.SG_UF.str.lower() + d.CD_MUNICIPIO.astype(int).map("{:05d}".format)
                    + d.NR_ZONA.astype(int).map("{:04d}".format) + d.NR_SECAO.astype(int).map("{:04d}".format) + "-log.jez")
    return d


def processar():
    sel = selecionar()
    linhas = []
    for uf, g in sel.groupby("SG_UF"):
        url = URL.format(uf)
        zf = zipfile.ZipFile(io.BufferedReader(ArquivoRemoto(url), buffer_size=1 << 22))
        infos = {i.filename: i for i in zf.infolist()}
        print(f"{uf}: {len(g)} seções, índice com {len(infos)} arquivos", flush=True)

        def um(row):
            info = infos.get(row.arquivo)
            if info is None:
                return {"arquivo": row.arquivo, "erro": "log não encontrado"}
            try:
                r = analisar_log(ler_membro(url, info), int(row.fuso))
            except Exception as e:  # registra e segue
                return {"arquivo": row.arquivo, "erro": repr(e)[:200]}
            r["arquivo"] = row.arquivo
            return r

        with ThreadPoolExecutor(16) as ex:
            for r in ex.map(um, g.itertuples()):
                linhas.append(r)
    res = sel.merge(pd.DataFrame(linhas), on="arquivo", how="left")
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    res.drop(columns=["ENC_LOCAL", "ENC_BRASILIA"]).to_csv(CACHE, index=False, compression="gzip")
    return res


def fmt(n):
    return f"{n:,.0f}".replace(",", ".")


def corrigir_fuso(res):
    """O cache pode ter sido gerado com o fuso por UF (versão antiga). Recalcula grupo e contagens com o fuso por
    município (oeste do AM em UTC-5, Fernando de Noronha em UTC-2) a partir dos votos por minuto."""
    if "fuso" in res and res.fuso.notna().all():
        return res
    res = res.copy()
    novo = fuso(res)
    antigo = res.SG_UF.map(FUSO).fillna(0)
    enc = pd.to_datetime(res.DT_ENCERRAMENTO, format="mixed") + pd.to_timedelta(novo, unit="h")
    seg = (enc - enc.dt.normalize()).dt.total_seconds()
    res.loc[(res.grupo == "fechou 19h ou depois") & (seg < 19 * 3600), "grupo"] = "deixou de ser tardia com o fuso corrigido"
    for i in res.index[novo != antigo]:
        desloc = int((novo[i] - antigo[i]) * 60)
        mins = {int(k) + desloc: int(v) for k, v in (kv.split(":") for kv in str(res.at[i, "por_minuto"]).split(";") if ":" in kv)}
        for col, t in [("votos_apos_17h00", 1020), ("votos_apos_17h15", 1035), ("votos_apos_17h30", 1050),
                       ("votos_apos_18h00", 1080), ("votos_apos_18h30", 1110)]:
            res.at[i, col] = sum(v for k, v in mins.items() if k >= t)
        res.at[i, "por_minuto"] = ";".join(f"{k}:{v}" for k, v in sorted(mins.items()) if k >= 1020)
    res["fuso"] = novo
    return res[res.grupo != "deixou de ser tardia com o fuso corrigido"]


def relatorio(res):
    res = corrigir_fuso(res)
    L = ["# Votos depois das 17h nas seções que fecharam às 19h (2º turno 2026)", "",
         "Fonte: log de cada urna (`logd.dat`), lido direto do pacote oficial \"arquivos transmitidos para totalização\" "
         "do TSE por download parcial. O horário foi convertido para Brasília. Grupo de controle: amostra aleatória "
         "(semente 2026) de seções do **mesmo local de votação** que fecharam até 17h15.", ""]
    ok = res[res.get("erro").isna()] if "erro" in res else res
    erros = len(res) - len(ok)
    L.append(f"Seções analisadas: {fmt(len(ok))} ({fmt(erros)} com erro de leitura ou sem log).")
    L.append("")
    t = ok.groupby("grupo").agg(secoes=("arquivo", "size"), comparecimento_BU=("QT_COMPARECIMENTO", "sum"),
                                votos_no_log=("votos_log", "sum"), apos_17h00=("votos_apos_17h00", "sum"),
                                apos_17h15=("votos_apos_17h15", "sum"), apos_17h30=("votos_apos_17h30", "sum"),
                                apos_18h00=("votos_apos_18h00", "sum"), apos_18h30=("votos_apos_18h30", "sum"))
    t["% dos votos após 17h"] = (t.apos_17h00 / t.votos_no_log * 100).round(2)
    t["% dos votos após 17h15"] = (t.apos_17h15 / t.votos_no_log * 100).round(2)
    L += ["## Quantos votos depois das 17h", "", t.astype({c: "int64" for c in t.columns if not c.startswith("%")}).to_markdown(), ""]
    tard = ok[ok.grupo == "fechou 19h ou depois"]
    L.append(f"- Log = comparecimento do BU: {fmt((ok.votos_log == ok.QT_COMPARECIMENTO).sum())} de {fmt(len(ok))} seções.")
    L.append(f"- Seções tardias **sem nenhum voto** depois das 17h15: {fmt((tard.votos_apos_17h15 == 0).sum())} de {fmt(len(tard))}.")
    L.append(f"- Votos dados depois das 17h00 nas seções tardias: **{fmt(tard.votos_apos_17h00.sum())}** de {fmt(tard.votos_log.sum())} "
             f"({tard.votos_apos_17h00.sum() / tard.votos_log.sum() * 100:.2f}%). Mesmo que **todos** fossem ilegítimos e todos de "
             f"Lula, o efeito máximo sobre a margem de 4.430.191 seria de {fmt(tard.votos_apos_17h00.sum())} votos "
             f"({tard.votos_apos_17h00.sum() / 4430191 * 100:.2f}%).")
    L.append("- Votos entre 17h00 e 17h15 são normais: é quem estava na fila às 17h. As vizinhas de controle também os têm.")
    L.append(f"- Seções tardias com mais de 10% dos votos depois das 17h15: {fmt((tard.votos_apos_17h15 > 0.1 * tard.votos_log).sum())}.")
    # Lula/Flávio nas tardias por intensidade de voto tardio
    tard = tard.assign(frac=tard.votos_apos_17h15 / tard.votos_log)
    tard["faixa"] = pd.cut(tard.frac, [-0.001, 0, 0.02, 0.05, 0.1, 1], labels=["0", "até 2%", "2–5%", "5–10%", "mais de 10%"])
    f = tard.groupby("faixa", observed=True).agg(secoes=("arquivo", "size"), votos_apos_17h15=("votos_apos_17h15", "sum"),
                                                  lula=("V_13", "sum"), flavio=("V_22", "sum"))
    f["% Lula"] = (f.lula / (f.lula + f.flavio) * 100).round(2)
    L += ["", "## Seções tardias por fração de votos dados depois das 17h15", "", f.to_markdown(), ""]
    # Distribuição por minuto
    por_min = Counter()
    for s in tard.por_minuto.dropna():
        for kv in s.split(";"):
            if kv:
                k, v = kv.split(":")
                por_min[int(k) // 15 * 15] += int(v)
    dist = pd.Series(por_min).sort_index()
    dist.index = [f"{k // 60:02d}h{k % 60:02d}" for k in dist.index]
    L += ["## Votos depois das 17h nas seções tardias, por janela de 15 minutos (Brasília)", "",
          dist.to_frame("votos").to_markdown(), ""]
    uf = tard.groupby("SG_UF").agg(secoes=("arquivo", "size"), votos=("votos_log", "sum"), apos_17h15=("votos_apos_17h15", "sum"))
    uf["%"] = (uf.apos_17h15 / uf.votos * 100).round(2)
    L += ["## Por UF (seções tardias)", "", uf.sort_values("secoes", ascending=False).to_markdown(), ""]
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if os.path.exists(CACHE) and "--refazer" not in sys.argv:
        res = pd.read_csv(CACHE, dtype={"CD_MUNICIPIO": str, "NR_ZONA": str, "NR_SECAO": str})
    else:
        res = processar()
    relatorio(res)
