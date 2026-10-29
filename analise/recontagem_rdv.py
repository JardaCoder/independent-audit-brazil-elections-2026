"""Recontagem voto a voto a partir do RDV (Registro Digital do Voto) de cada urna, e leitura dos totais do
bu.dat (o boletim de urna digital, assinado). Compara os dois com a planilha BWeb do TSE.
Gera analise/RECONTAGEM_RDV.md.

O RDV guarda cada voto digitado (embaralhado, sem ordem de votação). Os dois arquivos estão em ASN.1/DER.
Não usamos a especificação oficial: um leitor DER mínimo percorre a estrutura. Votos nominais aparecem com o
número digitado; brancos e nulos com o tipo de voto.

    python3 analise/recontagem_rdv.py AC RR AP
"""
import collections
import os
import re
import sys
import zipfile

import pandas as pd

from carregar import RAIZ

PASTA_URNA = os.path.join(RAIZ, "dados", "tse", "2026", "arquivos_urna", "2turno")
PASTA_PRES = os.path.join(RAIZ, "dados", "tse", "2026", "presidente", "2turno")
SAIDA = os.path.join(RAIZ, "analise", "RECONTAGEM_RDV.md")
CARGO_PRESIDENTE = 1


def tlv(b, i):
    """Lê um cabeçalho DER (tag, comprimento) na posição i. Devolve (classe, construída, número, início, tamanho)."""
    t = b[i]
    i += 1
    cls, cons, num = t >> 6, bool(t & 0x20), t & 0x1F
    if num == 0x1F:
        num = 0
        while True:
            x = b[i]
            i += 1
            num = (num << 7) | (x & 0x7F)
            if not x & 0x80:
                break
    n = b[i]
    i += 1
    if n & 0x80:
        k = n & 0x7F
        n = int.from_bytes(b[i:i + k], "big")
        i += k
    return cls, cons, num, i, n


def filhos(b, ini, fim):
    out, i = [], ini
    while i < fim:
        c = tlv(b, i)
        out.append(c)
        i = c[3] + c[4]
    return out


def inteiro(b, c):
    return int.from_bytes(b[c[3]:c[3] + c[4]], "big")


def votos_rdv(b):
    """Conta os votos de Presidente no RDV: {'13': n, '22': n, 'Branco': n, 'Nulo': n}."""
    _, _, _, s, n = tlv(b, 0)
    corpo = filhos(b, s, s + n)[2]
    eleicoes = [c for c in filhos(b, corpo[3], corpo[3] + corpo[4]) if c[0] == 2 and c[2] == 1][0]
    cont = collections.Counter()
    for e in filhos(b, eleicoes[3], eleicoes[3] + eleicoes[4]):
        ec = filhos(b, e[3], e[3] + e[4])
        for cargo in filhos(b, ec[1][3], ec[1][3] + ec[1][4]):
            cc = filhos(b, cargo[3], cargo[3] + cargo[4])
            if inteiro(b, cc[0]) != CARGO_PRESIDENTE:
                continue
            for v in filhos(b, cc[2][3], cc[2][3] + cc[2][4]):
                vc = filhos(b, v[3], v[3] + v[4])
                tipo = b[vc[0][3]]  # 2 nominal, 3 branco, 4 nulo
                digitado = b[vc[1][3]:vc[1][3] + vc[1][4]].decode() if len(vc) > 1 else ""
                if tipo == 2:
                    cont[digitado] += 1
                elif tipo == 3:
                    cont["Branco"] += 1
                else:
                    cont["Nulo"] += 1  # inclui números inválidos digitados ("00", "10"...)
    return cont


def votos_bu(b):
    """Totais de Presidente gravados no bu.dat (dentro de um envelope: último OCTET STRING da raiz)."""
    _, _, _, s, n = tlv(b, 0)
    env = filhos(b, s, s + n)[-1]
    bu = b[env[3]:env[3] + env[4]]
    _, _, _, s, n = tlv(bu, 0)
    resultados = [c for c in filhos(bu, s, s + n) if c[0] == 0 and c[2] == 16 and c[4] > 200][0]
    cont = collections.Counter()
    for e in filhos(bu, resultados[3], resultados[3] + resultados[4]):
        ec = filhos(bu, e[3], e[3] + e[4])
        for rv in filhos(bu, ec[4][3], ec[4][3] + ec[4][4]):
            rc = filhos(bu, rv[3], rv[3] + rv[4])
            for tv in filhos(bu, rc[2][3], rc[2][3] + rc[2][4]):
                tc = filhos(bu, tv[3], tv[3] + tv[4])
                if bu[tc[0][3]] != CARGO_PRESIDENTE:
                    continue
                for v in filhos(bu, tc[2][3], tc[2][3] + tc[2][4]):
                    vc = filhos(bu, v[3], v[3] + v[4])
                    tipo, q = bu[vc[0][3]], inteiro(bu, vc[1])  # 1 nominal, 2 branco, 3 nulo
                    if tipo == 1:
                        ic = filhos(bu, vc[2][3], vc[2][3] + vc[2][4])
                        cont[str(inteiro(bu, ic[1]))] += q
                    else:
                        cont["Branco" if tipo == 2 else "Nulo"] += q
    return cont, b


def bweb(uf):
    f = next(os.path.join(PASTA_PRES, x) for x in os.listdir(PASTA_PRES) if f"_2t_{uf}_" in x)
    d = pd.read_csv(f, sep=";", encoding="latin1", dtype=str)
    for c in ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "QT_VOTOS", "QT_COMPARECIMENTO"]:
        d[c] = d[c].astype(int)
    d["k"] = d.NR_VOTAVEL.where(d.DS_TIPO_VOTAVEL == "Nominal", d.DS_TIPO_VOTAVEL)
    chave = ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
    votos = d.pivot_table(index=chave, columns="k", values="QT_VOTOS", aggfunc="sum", fill_value=0)
    meta = d.groupby(chave).agg(comp=("QT_COMPARECIMENTO", "first"), urna=("NR_URNA_EFETIVADA", "first"),
                                c1=("CD_CARGA_1_URNA_EFETIVADA", "first"), c2=("CD_CARGA_2_URNA_EFETIVADA", "first"))
    return votos.join(meta)


def recontar(uf):
    web = bweb(uf)
    z = zipfile.ZipFile(os.path.join(PASTA_URNA, f"bu_imgbu_logjez_rdv_vscmr_2026_2t_{uf}.zip"))
    st, tot, dif = collections.Counter(), collections.Counter(), []
    for nome in sorted(z.namelist()):
        if not nome.endswith("-rdv.dat"):
            continue
        base = nome[:-8]
        chave = (int(base[8:13]), int(base[13:17]), int(base[17:21]))
        rdv = votos_rdv(z.read(nome))
        bu, bruto = votos_bu(z.read(base + "-bu.dat"))
        linha = web.loc[chave]
        oficial = {k: int(linha.get(k, 0)) for k in ["13", "22", "Branco", "Nulo"]}
        r = {k: rdv.get(k, 0) for k in oficial}
        u = {k: bu.get(k, 0) for k in oficial}
        st["seções"] += 1
        st["RDV = BWeb (Lula, Flávio, brancos, nulos)"] += r == oficial
        st["bu.dat = BWeb"] += u == oficial
        st["total de votos no RDV = comparecimento"] += sum(rdv.values()) == linha.comp
        carga = re.findall(rb"\x1b\x18(\d{24})", bruto)
        carga_web = re.sub(r"\D", "", linha.c1) + re.sub(r"\D", "", linha.c2)
        st["código de carga no bu.dat = BWeb"] += bool(carga) and carga[0].decode() == carga_web
        for k in oficial:
            tot[f"RDV {k}"] += r[k]
            tot[f"BWeb {k}"] += oficial[k]
        if r != oficial:
            dif.append((base, r, oficial))
    return st, tot, dif


def main(ufs):
    L = ["# Recontagem voto a voto pelo RDV — 2º turno 2026", "",
         "Para cada urna, contamos os votos de Presidente um a um no **RDV** (o registro de cada voto digitado) e lemos "
         "os totais gravados no **bu.dat** (o boletim digital). Comparamos com a planilha BWeb publicada pelo TSE.", ""]
    tabela, totais = {}, {}
    for uf in ufs:
        st, tot, dif = recontar(uf)
        tabela[uf] = dict(st)
        totais[uf] = dict(tot)
        if dif:
            L += [f"Divergências em {uf}:", "", "\n".join(str(x) for x in dif[:20]), ""]
    L += [pd.DataFrame(tabela).to_markdown(), "", "## Totais", "", pd.DataFrame(totais).to_markdown(), ""]
    L.append("Os votos nulos aparecem no RDV como números digitados que não correspondem a candidato (\"00\", \"10\" etc.).")
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1:] or ["AC", "RR", "AP"])
