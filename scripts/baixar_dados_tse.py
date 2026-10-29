"""Baixa conjuntos de dados das eleições 2026 do Portal de Dados Abertos do TSE.

Cada conjunto vai para dados/tse/2026/<pasta>/. Quando o TSE publica um .sha512,
o arquivo é conferido.

    python3 scripts/baixar_dados_tse.py                 # lista os conjuntos
    python3 scripts/baixar_dados_tse.py bu_2t           # BUs do 2º turno (~150 MB, já versionado)
    python3 scripts/baixar_dados_tse.py bu_1t votacao_secao
    python3 scripts/baixar_dados_tse.py arquivos_urna_2t AC RR AP   # BU/RDV/log assinados de cada urna (grande!)
"""
import hashlib
import json
import os
import sys
import urllib.request

API = "https://dadosabertos.tse.jus.br/api/3/action/package_show?id="
RAIZ = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados", "tse", "2026")

# nome: (pacote CKAN, pasta de destino, filtro no nome do arquivo)
CONJUNTOS = {
    "bu_2t": ("resultados-2026-boletim-de-urna", "boletim_urna/2turno", "bweb_2t_"),
    "bu_1t": ("resultados-2026-boletim-de-urna", "boletim_urna/1turno", "bweb_1t_"),
    "votacao_secao": ("resultados-2026", "votacao_secao", "votacao_secao_"),
    "detalhe_secao": ("resultados-2026", "detalhe_votacao_secao", "detalhe_votacao_secao_"),
    "detalhe_munzona": ("resultados-2026", "detalhe_votacao_munzona", "detalhe_votacao_munzona_"),
    "candidato_munzona": ("resultados-2026", "votacao_candidato_munzona", "votacao_candidato_munzona_"),
    "partido_munzona": ("resultados-2026", "votacao_partido_munzona", "votacao_partido_munzona_"),
    "totalizacao": ("resultados-2026", "relatorio_totalizacao", "Relatorio_Resultado_Totalizacao_"),
    "comparecimento": ("comparecimento-e-abstencao-2026", "comparecimento_abstencao", "perfil_comparecimento"),
    "eleitorado": ("eleitorado-2026", "eleitorado", ""),
    "mesarios": ("mesarias-mesarios-e-funcoes-especiais-2026", "mesarios", ""),
    "correspondencias_esperadas_2t": ("resultados-2026-correspondencias-esperadas-e-efetivadas-2-turno",
                                      "correspondencias/2turno", "CESP_2t_"),
    "bu_2t_2022": ("resultados-2022-boletim-de-urna", "../2022/boletim_urna/2turno", "bweb_2t_"),
    "logs_gedai_2t": ("resultados-2026-logs-do-sistema-de-preparacao-das-urnas-eletronicas-gedai-2-turno",
                      "logs_gedai/2turno", ""),
}


def recursos(pacote):
    with urllib.request.urlopen(API + pacote, timeout=60) as r:
        return [x["url"] for x in json.load(r)["result"]["resources"]]


def baixar(url, destino):
    if os.path.exists(destino):
        return
    tmp = destino + ".part"
    urllib.request.urlretrieve(url, tmp)
    os.replace(tmp, destino)


def sha512(caminho):
    h = hashlib.sha512()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


URNA_2T = "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2026_2t_{}.zip"


def arquivos_urna_2t(ufs):
    """O catálogo ainda não lista o 2º turno destes pacotes; a URL segue o padrão do 1º turno."""
    destino = os.path.join(RAIZ, "arquivos_urna", "2turno")
    os.makedirs(destino, exist_ok=True)
    for uf in ufs:
        url = URNA_2T.format(uf.upper())
        print("baixando", url)
        baixar(url, os.path.join(destino, url.rsplit("/", 1)[-1]))


def main(nomes):
    if nomes and nomes[0] == "arquivos_urna_2t":
        return arquivos_urna_2t(nomes[1:])
    if not nomes:
        for k, (pac, pasta, _) in CONJUNTOS.items():
            print(f"{k:30} -> dados/tse/2026/{pasta}  ({pac})")
        print(f"{'arquivos_urna_2t <UF> ...':30} -> dados/tse/2026/arquivos_urna/2turno  (BU, RDV, log e assinatura de cada urna)")
        return
    for nome in nomes:
        pacote, pasta, filtro = CONJUNTOS[nome]
        destino = os.path.join(RAIZ, pasta)
        os.makedirs(destino, exist_ok=True)
        urls = [u for u in recursos(pacote) if filtro in u.rsplit("/", 1)[-1]]
        # O CKAN às vezes lista o .sha512 sem o .zip correspondente (ex.: RR no 2º turno).
        urls += [u[:-7] for u in urls if u.endswith(".sha512") and u[:-7] not in urls]
        for url in sorted(set(urls)):
            arq = os.path.join(destino, url.rsplit("/", 1)[-1])
            print("baixando", url)
            baixar(url, arq)
        for arq in sorted(os.listdir(destino)):
            if arq.endswith(".sha512") and os.path.exists(os.path.join(destino, arq[:-7])):
                esperado = open(os.path.join(destino, arq)).read().split()[0].lower()
                ok = sha512(os.path.join(destino, arq[:-7])) == esperado
                print(("OK   " if ok else "FALHA"), arq[:-7])


if __name__ == "__main__":
    main(sys.argv[1:])
