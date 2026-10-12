#!/usr/bin/env python3
"""Costruisce il sito: scrive le pagine HTML (italiano alla radice, inglese in en/), 404.html, sitemap.xml e robots.txt.

    python3 tools/build_site.py             # scrive i file
    python3 tools/build_site.py --verifica  # non scrive: dice se i file nel repository sono aggiornati (esce con 1 se no)

Solo libreria standard. Dopo aver cambiato un testo (tools/contenuti_*.py) o i dati (content/site.json): rilanciarlo, poi
python3 tools/check_site.py e python3 tools/test_site.py.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sitegen  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifica", action="store_true", help="non scrive niente: controlla che i file siano aggiornati")
    p.add_argument("--radice", type=Path, default=sitegen.RADICE, help="cartella del sito (di solito quella giusta già)")
    a = p.parse_args(argv)
    dati = sitegen.carica_dati(a.radice)
    file = sitegen.costruisci(dati)
    if a.verifica:
        vecchi = [nome for nome, testo in file.items() if not (a.radice / nome).exists() or (a.radice / nome).read_text(encoding="utf-8") != testo]
        if vecchi:
            print("Da rigenerare (python3 tools/build_site.py):", ", ".join(sorted(vecchi)))
            return 1
        print(f"Il sito è aggiornato ({len(file)} file).")
        return 0
    for nome, testo in file.items():
        destinazione = a.radice / nome
        destinazione.parent.mkdir(parents=True, exist_ok=True)
        destinazione.write_text(testo, encoding="utf-8")
    print(f"Scritti {len(file)} file: " + ", ".join(sorted(file)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
