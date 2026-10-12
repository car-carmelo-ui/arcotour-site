#!/usr/bin/env python3
"""Prepara i caratteri del sito: Inter in versione leggera (solo lettere latine, formato WOFF2).

Perché: i file di Inter dell'app pesano 325 KB l'uno (tutte le lingue del mondo). Al sito bastano italiano e inglese:
tagliati a lettere latine, punteggiatura, simboli di uso comune e frecce, in WOFF2 pesano pochi KB e il sito si apre
più in fretta sul telefono.

Licenza: Inter è sotto SIL Open Font License 1.1 e NON ha un «nome riservato», quindi alleggerirlo è consentito; la
licenza e il copyright restano accanto ai file (assets/fonts/OFL-Inter.txt). Il Playfair Display, che invece ha un nome
riservato, NON si tocca: il sito serve il file identico a quello dell'app.

Uso (solo per rifarli; serve fontTools + brotli):
    python3 tools/prepara_caratteri.py /percorso/del/progetto/ArcoTour
"""
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

QUI = Path(__file__).resolve().parents[1]

# Intervalli Unicode: latino di base e supplemento, latino esteso A, punteggiatura generale, euro, frecce, segni usati dal sito.
INTERVALLI = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,"
              "U+2190-2193,U+2212,U+2215,U+FEFF,U+FFFD")


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    app = Path(sys.argv[1])
    for nome, uscita in (("Inter-Regular.ttf", "inter-regular.woff2"), ("Inter-SemiBold.ttf", "inter-semibold.woff2")):
        opzioni = subset.Options()
        opzioni.flavor = "woff2"
        opzioni.layout_features = ["*"]
        opzioni.name_IDs = ["*"]  # il copyright e la licenza dentro il file restano
        opzioni.notdef_outline = True
        font = TTFont(app / "app/assets/google_fonts" / nome)
        s = subset.Subsetter(opzioni)
        s.populate(unicodes=subset.parse_unicodes(INTERVALLI))
        s.subset(font)
        destinazione = QUI / "assets/fonts" / uscita
        destinazione.parent.mkdir(parents=True, exist_ok=True)
        font.flavor = "woff2"
        font.save(destinazione)
        print(f"{uscita}: {destinazione.stat().st_size // 1024} KB (originale {(app / 'app/assets/google_fonts' / nome).stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
