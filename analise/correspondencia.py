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
    from carregar import carregar, fuso
    sec = carregar()
    for c in ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]:
        sec[c] = sec[c].astype(int)
    partes, resumo = [], []
    for z in sorted(glob.glob(os.path.join(PASTA, "CESP_2t_*.zip"))):
        with zipfile.ZipFile(z) as zf:
            esp = ler_csv(zf, "csec_")
            cont = ler_csv(zf, "ccont_")
        uf = esp.SG_UF.iloc[0]
        gerada = pd.to_datetime(esp.DT_GERACAO.iloc[0] + " " + esp.HH_GERACAO.iloc[0], dayfirst=True)
        bu_zip = next(glob.iglob(os.path.join(PASTA_BU, f"bweb_2t_{uf}_*.zip")))
        with zipfile.ZipFile(bu_zip) as zf:
            bu = ler_csv(zf, "bweb_", CHAVE + ["CD_CARGO_PERGUNTA", "NR_URNA_EFETIVADA", "CD_CARGA_1_URNA_EFETIVADA",
                                               "CD_CARGA_2_URNA_EFETIVADA", "CD_FLASHCARD_URNA_EFETIVADA",
                                               "DT_CARGA_URNA_EFETIVADA"])
        bu = bu[bu.CD_CARGO_PERGUNTA == "1"].drop_duplicates(CHAVE)
        for df in (esp, bu):
            for c in ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]:
                df[c] = df[c].astype(int)
        m = bu.merge(esp.drop(columns=["NM_MUNICIPIO"]), on=CHAVE, how="left", indicator=True).merge(
            sec[CHAVE + ["NM_MUNICIPIO", "DT_ABERTURA", "QT_COMPARECIMENTO", "V_13", "V_22"]], on=CHAVE, how="left")
        # O código de carga de 24 dígitos vem dividido em CD_CARGA_1 (18 dígitos) + CD_CARGA_2 (6); a lista perde zeros à esquerda.
        m["carga_bu"] = (m.CD_CARGA_1_URNA_EFETIVADA.str.replace(r"\D", "", regex=True)
                         + m.CD_CARGA_2_URNA_EFETIVADA.str.replace(r"\D", "", regex=True)).str.zfill(24)
        m["carga_esp"] = so_digitos(m.CD_CARGA_URNA_ESPERADA)
        col_urna = [c for c in cont.columns if "URNA" in c and c.startswith("NR_")][0]
        col_carga = [c for c in cont.columns if c.startswith("CD_CARGA")][0]
        cont_urnas, cont_cargas = set(cont[col_urna]), set(so_digitos(cont[col_carga]))
        # DT_CARGA está no relógio local da urna: converte para Brasília para comparar com a hora de geração da lista.
        carga_bsb = pd.to_datetime(m.DT_CARGA_URNA_EFETIVADA, errors="coerce") + pd.to_timedelta(fuso(m).fillna(0), unit="h")
        listada = m._merge == "both"
        mesma_urna = m.NR_URNA_EFETIVADA == m.NR_URNA_ESPERADA
        mesma_carga = m.carga_bu == m.carga_esp
        urna_cont = m.NR_URNA_EFETIVADA.isin(cont_urnas)
        carga_cont = m.carga_bu.isin(cont_cargas)
        depois = carga_bsb > gerada
        mesmo_cartao = m.CD_FLASHCARD_URNA_EFETIVADA == m.CD_FLASHCARD_URNA_ESPERADA
        cat = pd.Series("", index=m.index)
        regras = [
            (listada & mesma_urna & mesma_carga, "1. urna e carga exatamente as previstas"),
            (listada & mesma_urna & ~mesma_carga, "2. urna prevista, carga diferente da lista"),
            (listada & ~mesma_urna & urna_cont & carga_cont, "3. urna de contingência da lista, com a carga da lista"),
            (listada & ~mesma_urna & urna_cont & ~carga_cont, "4. urna de contingência da lista, recarregada (carga fora da lista)"),
            (listada & ~mesma_urna & ~urna_cont & carga_cont, "3. urna de contingência da lista, com a carga da lista"),
            (listada & ~mesma_urna & ~urna_cont & ~carga_cont & depois, "5. urna fora das listas, carregada DEPOIS que a lista foi gerada"),
            (listada & ~mesma_urna & ~urna_cont & ~carga_cont & ~depois & mesmo_cartao, "6. urna fora das listas, mesmo cartão de carga da urna prevista"),
            (listada & ~mesma_urna & ~urna_cont & ~carga_cont & ~depois & ~mesmo_cartao, "7. urna fora das listas, sem explicação nos dados"),
            (~listada & m.DT_ABERTURA.isna() & (m.SG_UF == "ZZ"), "8. seção fora da lista: exterior, apurada em cédula"),
            (~listada & m.DT_ABERTURA.notna() & (urna_cont | carga_cont), "9. seção fora da lista, urna de contingência da lista"),
            (~listada & m.DT_ABERTURA.notna() & ~urna_cont & ~carga_cont, "10. seção fora da lista, urna fora das listas"),
        ]
        for mask, nome in regras:
            cat[mask & (cat == "")] = nome
        m["categoria"] = cat.replace("", "11. outros")
        m["lista_gerada_em"] = gerada
        m["carga_brasilia"] = carga_bsb
        partes.append(m)
    t = pd.concat(partes)
    r = t.groupby("categoria").agg(secoes=("NR_SECAO", "size"), comparecimento=("QT_COMPARECIMENTO", "sum"),
                                   lula=("V_13", "sum"), flavio=("V_22", "sum"))
    r = r.reindex(sorted(r.index, key=lambda x: int(x.split(".")[0])))
    r["saldo Lula"] = r.lula - r.flavio
    r = r.fillna(0).astype(int)
    doc = t[t.categoria.str[:2].isin(["2.", "4.", "5.", "6.", "7.", "9.", "10"])]
    cols = CHAVE + ["NM_MUNICIPIO", "categoria", "NR_URNA_ESPERADA", "NR_URNA_EFETIVADA", "DT_CARGA_URNA_ESPERADA",
                    "DT_CARGA_URNA_EFETIVADA", "carga_brasilia", "lista_gerada_em", "QT_COMPARECIMENTO", "V_13", "V_22"]
    doc[cols].sort_values(["categoria"] + CHAVE).to_csv(os.path.join(RAIZ, "analise", "secoes_para_documentar.csv"), index=False)
    sem_exp = t[t.categoria.str.startswith(("7.", "10."))]
    txt = ("# Urnas usadas × urnas previstas antes da eleição — 2º turno 2026\n\n"
           "Fonte: arquivos CESP do TSE, gerados em 24/10/2026 (véspera da eleição), com a urna e o código de carga previstos "
           "para cada seção e a lista de urnas de contingência (reservas). Cada seção entra em **uma** categoria.\n\n"
           f"Lista gerada em: {t.lista_gerada_em.iloc[0]} (horário de Brasília). As datas de carga das urnas estão no relógio local e "
           "foram convertidas para Brasília antes da comparação.\n\n" + r.to_markdown() + "\n\n"
           "- Categorias 1, 3 e 8 estão de acordo com a lista ou explicadas (cédula no exterior).\n"
           "- Categorias 2, 4, 5, 6 e 9 têm explicação provável nos próprios dados (recarga, troca feita depois da lista, mesmo "
           "cartão de carga), mas pedem confirmação nas atas da seção.\n"
           f"- Categorias 7 e 10 (**{len(sem_exp)} seções**, {fmt_int(sem_exp.QT_COMPARECIMENTO.sum())} votos, saldo de Lula "
           f"{fmt_int(sem_exp.V_13.sum() - sem_exp.V_22.sum())}) não têm explicação nos dados.\n\n"
           "Lista completa das categorias 2, 4, 5, 6, 7, 9 e 10: `secoes_para_documentar.csv`.\n\n"
           "## Seções sem explicação nos dados (categorias 7 e 10)\n\n"
           + sem_exp[cols].astype(str).to_markdown(index=False, disable_numparse=True) + "\n")
    open(SAIDA, "w", encoding="utf-8").write(txt)
    print(txt)


def fmt_int(n):
    return f"{int(n):,}".replace(",", ".")


if __name__ == "__main__":
    main()
