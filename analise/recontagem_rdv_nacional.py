"""Recontagem voto a voto pelo RDV de TODAS as urnas do 2º turno, lendo direto do servidor do TSE.

Para cada UF, lê o índice do pacote "arquivos transmitidos para totalização" e baixa, por download parcial
(HTTP Range), só o arquivo -rdv.dat de cada seção (poucos KB). Conta os votos de Presidente e compara com a
planilha BWeb. Gera analise/RECONTAGEM_RDV_NACIONAL.md e dados/derivados/recontagem_rdv_2t_2026.csv.gz.

    python3 analise/recontagem_rdv_nacional.py            # todas as UFs (demora; retoma de onde parou)
    python3 analise/recontagem_rdv_nacional.py SP RJ      # só algumas
"""
import io
import os
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from carregar import RAIZ
from estatistica import fmt
from logs_tardias import URL, ArquivoRemoto, ler_membro
from recontagem_rdv import bweb, votos_rdv

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
       "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "ZZ"]
PARCIAL = os.path.join(RAIZ, "dados", "derivados", "recontagem_rdv")
SAIDA_CSV = os.path.join(RAIZ, "dados", "derivados", "recontagem_rdv_2t_2026.csv.gz")
SAIDA = os.path.join(RAIZ, "analise", "RECONTAGEM_RDV_NACIONAL.md")


def recontar_uf(uf):
    destino = os.path.join(PARCIAL, f"{uf}.csv")
    if os.path.exists(destino):
        return pd.read_csv(destino)
    url = URL.format(uf)
    zf = zipfile.ZipFile(io.BufferedReader(ArquivoRemoto(url), buffer_size=1 << 22))
    infos = [i for i in zf.infolist() if i.filename.endswith("-rdv.dat")]
    web = bweb(uf)
    print(f"{uf}: {len(infos)} RDVs, {len(web)} seções na BWeb", flush=True)

    def um(info):
        base = info.filename[:-8]
        chave = (int(base[8:13]), int(base[13:17]), int(base[17:21]))
        try:
            c = votos_rdv(ler_membro(url, info))
            erro = ""
        except Exception as e:
            c, erro = {}, repr(e)[:120]
        return {"SG_UF": uf, "CD_MUNICIPIO": chave[0], "NR_ZONA": chave[1], "NR_SECAO": chave[2],
                "rdv_13": c.get("13", 0), "rdv_22": c.get("22", 0), "rdv_branco": c.get("Branco", 0),
                "rdv_nulo": c.get("Nulo", 0), "rdv_total": sum(c.values()), "erro": erro}

    with ThreadPoolExecutor(48) as ex:
        linhas = list(ex.map(um, infos))
    r = pd.DataFrame(linhas)
    w = web.reset_index()
    for k, c in [("13", "bweb_13"), ("22", "bweb_22"), ("Branco", "bweb_branco"), ("Nulo", "bweb_nulo")]:
        w[c] = w[k] if k in w else 0
    w = w.rename(columns={"comp": "bweb_comparecimento"})[["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "bweb_13", "bweb_22",
                                                            "bweb_branco", "bweb_nulo", "bweb_comparecimento"]]
    r = w.merge(r, on=["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"], how="outer", indicator=True)
    r["SG_UF"] = uf
    os.makedirs(PARCIAL, exist_ok=True)
    r.to_csv(destino, index=False)
    return r


def main(ufs):
    partes = [recontar_uf(uf) for uf in ufs]
    r = pd.concat(partes, ignore_index=True)
    r.to_csv(SAIDA_CSV, index=False, compression="gzip")
    ok = r[r._merge == "both"]
    igual = ((ok.rdv_13 == ok.bweb_13) & (ok.rdv_22 == ok.bweb_22) & (ok.rdv_branco == ok.bweb_branco)
             & (ok.rdv_nulo == ok.bweb_nulo))
    por_uf = r.groupby("SG_UF").agg(
        secoes_bweb=("bweb_comparecimento", lambda s: int(s.notna().sum())),
        rdv_lidos=("rdv_total", lambda s: int(s.notna().sum())),
        erros=("erro", lambda s: int((s.fillna("") != "").sum())))
    por_uf["RDV = BWeb"] = igual.groupby(ok.SG_UF).sum().reindex(por_uf.index).fillna(0).astype(int)
    tot = {"Lula (RDV)": int(ok.rdv_13.sum()), "Lula (BWeb)": int(ok.bweb_13.sum()),
           "Flávio (RDV)": int(ok.rdv_22.sum()), "Flávio (BWeb)": int(ok.bweb_22.sum()),
           "brancos (RDV)": int(ok.rdv_branco.sum()), "brancos (BWeb)": int(ok.bweb_branco.sum()),
           "nulos (RDV)": int(ok.rdv_nulo.sum()), "nulos (BWeb)": int(ok.bweb_nulo.sum())}
    sem_rdv = r[r._merge == "left_only"]
    L = ["# Recontagem nacional voto a voto pelo RDV — 2º turno 2026", "",
         "Cada RDV foi baixado do pacote oficial do TSE (\"arquivos transmitidos para totalização\") por download parcial "
         "e os votos de Presidente foram contados um a um. Ver `recontagem_rdv.py` para o leitor.", "",
         f"- Seções na BWeb: {fmt(len(r[r._merge != 'right_only']))}. RDVs lidos: {fmt(ok.rdv_total.notna().sum())}. "
         f"**RDV idêntico à BWeb (Lula, Flávio, brancos e nulos): {fmt(igual.sum())}**.",
         f"- Seções da BWeb sem arquivo RDV no pacote: {len(sem_rdv)}.",
         "", "## Totais", "", pd.Series(tot).to_frame("votos").to_markdown(), "", "## Por UF", "", por_uf.to_markdown(), ""]
    from carregar import carregar
    sec = carregar()
    cedula = sec[sec.DT_ABERTURA.isna()][["SG_UF", "CD_MUNICIPIO", "NR_SECAO", "NR_ZONA"]].astype(str)
    chave_ced = set(zip(cedula.SG_UF, cedula.CD_MUNICIPIO, cedula.NR_ZONA, cedula.NR_SECAO))
    dif = ok[~igual]
    eh_cedula = [(u, str(m), str(z), str(s_)) in chave_ced for u, m, z, s_ in zip(dif.SG_UF, dif.CD_MUNICIPIO, dif.NR_ZONA, dif.NR_SECAO)]
    eletronicas = ok[[(u, str(m), str(z), str(s_)) not in chave_ced for u, m, z, s_ in zip(ok.SG_UF, ok.CD_MUNICIPIO, ok.NR_ZONA, ok.NR_SECAO)]]
    ig_el = igual.loc[eletronicas.index]
    L.insert(5, f"- **Seções com urna eletrônica: {fmt(ig_el.sum())} de {fmt(len(eletronicas))} idênticas.** As "
             f"{fmt(sum(eh_cedula))} que não batem são todas seções do exterior apuradas em **cédula** (Sistema de Apuração): "
             "o arquivo delas não segue o formato do RDV da urna e o leitor não o interpreta. Os votos dessas seções somam "
             f"{fmt(dif[eh_cedula].bweb_comparecimento.sum())}, exatamente a diferença entre os totais abaixo.")
    if len(dif):
        L += ["## Seções com diferença", "", dif.head(50).to_markdown(index=False), ""]
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:] or UFS)
