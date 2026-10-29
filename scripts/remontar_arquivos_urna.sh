#!/usr/bin/env bash
# Remonta os pacotes de arquivos originais das urnas (divididos em partes de 90 MB por causa do
# limite de 100 MB por arquivo do GitHub) e confere o SHA-512 contra o MANIFESTO.csv.
set -euo pipefail
cd "$(dirname "$0")/../dados/tse/2026/arquivos_urna/2turno"
tail -n +2 MANIFESTO.csv | while IFS=';' read -r arq tam sha _; do
  if [ ! -f "$arq" ]; then
    cat partes/"$arq".parte-* > "$arq"
  fi
  if [ "$(sha512sum "$arq" | cut -d' ' -f1)" = "$sha" ] && [ "$(stat -c%s "$arq")" = "$tam" ]; then
    echo "OK    $arq"
  else
    echo "FALHA $arq" >&2; exit 1
  fi
done
