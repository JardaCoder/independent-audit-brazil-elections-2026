"""Extrai dos BWeb oficiais só as linhas de Presidente (CD_CARGO_PERGUNTA = 1), sem alterar nenhum byte
das linhas copiadas. Gera um .csv.gz por UF e um MANIFESTO.csv que liga cada arquivo extraído ao .zip
oficial do TSE (com o SHA-512 publicado pelo TSE) e informa quantas linhas foram copiadas.

    python3 scripts/extrair_presidente.py            # 1º e 2º turno 2026 e 2º turno 2022

Qualquer pessoa pode conferir: baixe o .zip oficial, rode este script e compare o SHA-512 dos .csv.gz
(a compressão é determinística: mtime=0)."""
import glob
import gzip
import hashlib
import io
import os
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONJUNTOS = [("2026", "1"), ("2026", "2"), ("2022", "2")]


def sha512(caminho):
    h = hashlib.sha512()
    with open(caminho, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def extrair(zip_path, destino):
    with zipfile.ZipFile(zip_path) as zf:
        nome = next(n for n in zf.namelist() if n.endswith(".csv"))
        with zf.open(nome) as f:
            cab = f.readline()
            cols = cab.decode("latin1").rstrip("\r\n").split(";")
            i = cols.index('"CD_CARGO_PERGUNTA"')
            total = copiadas = 0
            with open(destino, "wb") as bruto, gzip.GzipFile(filename="", mode="wb", fileobj=bruto, mtime=0) as gz:
                gz.write(cab)
                for linha in f:
                    total += 1
                    # Os campos que vêm antes do cargo não contêm ";". Em 2022 o código do cargo vem entre aspas.
                    if linha.split(b";", i + 1)[i].strip(b"\"") == b"1":
                        gz.write(linha)
                        copiadas += 1
    return nome, total, copiadas


def main():
    for ano, turno in CONJUNTOS:
        origem = os.path.join(RAIZ, "dados", "tse", ano, "boletim_urna", f"{turno}turno")
        saida = os.path.join(RAIZ, "dados", "tse", ano, "presidente", f"{turno}turno")
        os.makedirs(saida, exist_ok=True)
        linhas = ["arquivo_extraido;sha512_extraido;linhas_presidente;linhas_totais_no_original;"
                  "zip_oficial;csv_dentro_do_zip;sha512_zip_oficial_publicado_pelo_TSE;sha512_zip_conferido"]
        for z in sorted(glob.glob(os.path.join(origem, f"bweb_{turno}t_*.zip"))):
            uf = os.path.basename(z).split("_")[2]
            dest = os.path.join(saida, f"bweb_presidente_{turno}t_{uf}_{ano}.csv.gz")
            nome, total, copiadas = extrair(z, dest)
            oficial = open(z + ".sha512").read().split()[0]
            conferido = sha512(z)
            linhas.append(";".join([os.path.basename(dest), sha512(dest), str(copiadas), str(total),
                                    os.path.basename(z), nome, oficial, "SIM" if oficial == conferido else "NAO"]))
            print(f"{ano} {turno}t {uf}: {copiadas:>9} de {total:>10} linhas  {os.path.getsize(dest) / 1e6:6.1f} MB")
        open(os.path.join(saida, "MANIFESTO.csv"), "w").write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    main()
