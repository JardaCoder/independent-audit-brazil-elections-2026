"""Remonta os pacotes de arquivos originais das urnas (divididos em partes de 90 MB por causa do
limite de 100 MB por arquivo do GitHub) e confere tamanho e SHA-512 contra o MANIFESTO.csv.

    python3 scripts/remontar_arquivos_urna.py
"""
import csv
import glob
import hashlib
import os
import shutil
import sys

PASTA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados", "tse", "2026", "arquivos_urna", "2turno")

with open(os.path.join(PASTA, "MANIFESTO.csv"), newline="") as f:
    manifesto = list(csv.DictReader(f, delimiter=";"))
for item in manifesto:
    arq = os.path.join(PASTA, item["arquivo"])
    if not os.path.exists(arq):
        partes = sorted(glob.glob(os.path.join(PASTA, "partes", item["arquivo"] + ".parte-*")))
        if not partes:
            sys.exit(f"FALHA {item['arquivo']}: nenhuma parte em partes/")
        with open(arq + ".part", "wb") as saida:
            for p in partes:
                with open(p, "rb") as f:
                    shutil.copyfileobj(f, saida)
        os.replace(arq + ".part", arq)  # um arquivo interrompido no meio não fica com o nome final
    with open(arq, "rb") as f:
        sha = hashlib.file_digest(f, "sha512").hexdigest()
    if os.path.getsize(arq) != int(item["tamanho_bytes"]) or sha != item["sha512"]:
        sys.exit(f"FALHA {item['arquivo']}")
    print("OK   ", item["arquivo"])
