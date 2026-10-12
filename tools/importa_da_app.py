#!/usr/bin/env python3
"""Importa dal progetto dell'app ArcoTour (SOLA LETTURA) i dati veri che servono al sito.

Il sito non inventa niente: percorsi, foto con i loro crediti, icona e informativa sulla privacy vengono dal progetto
dell'app. Questo strumento li copia qui, in `content/` e `assets/`, e scrive da dove vengono (`content/origine.json`).

Uso:
    python3 tools/importa_da_app.py /percorso/del/progetto/ArcoTour

Non scrive MAI nulla nel progetto dell'app: lo legge soltanto (e il commit lo chiede a git, in sola lettura).
Serve solo per aggiornare il sito quando cambiano l'app o l'informativa; per costruire le pagine basta
`python3 tools/build_site.py` (solo libreria standard). Dipendenze di QUESTO strumento: PyYAML e Pillow.

Cosa importa:
  - percorsi di Roma           app/assets/data/roma.json          -> content/percorsi.json
  - foto scelte + crediti      content/roma/pois/*.yaml + images  -> content/foto.json, assets/img/foto/
  - informativa dell'app       content/legale/privacy.yaml        -> content/informativa_app.json
  - icona ufficiale            tools/genera_icona.py (disegno)    -> assets/img/ (icone, favicon, immagini di anteprima)
"""
import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

QUI = Path(__file__).resolve().parents[1]

# Le foto del sito: SOLO esterni di luoghi e monumenti all'aperto, tra quelle già nell'app. Restano fuori le quattro con
# annotazioni di licenza ancora da verificare (Palazzo Venezia, Santa Maria Maggiore, Terme di Diocleziano, Piazza Navona),
# gli interni e le foto con persone riconoscibili in primo piano. «percorso» dice a quale percorso dell'app appartiene la tappa.
FOTO_DEL_SITO = [
    # id scheda,          id percorso,           testo alternativo (it, en)
    ("colosseo", None, ("Il Colosseo visto dall'esterno.", "The Colosseum seen from outside.")),
    ("arco_costantino", "roma_antica", ("L'Arco di Costantino.", "The Arch of Constantine.")),
    ("campidoglio", "traiano_campidoglio", ("Piazza del Campidoglio, con la pavimentazione a stella e i palazzi che la circondano.",
                                            "Piazza del Campidoglio, with its star-patterned paving and the palaces around it.")),
    ("fontana_di_trevi", "campo_marzio", ("La Fontana di Trevi.", "The Trevi Fountain.")),
    ("piazza_spagna", "tridente", ("La Barcaccia in Piazza di Spagna, con la scalinata di Trinità dei Monti sullo sfondo.",
                                   "The Barcaccia fountain in Piazza di Spagna, with the Trinità dei Monti steps behind it.")),
    ("castel_sant_angelo", "gianicolo_vaticano", ("Castel Sant'Angelo.", "Castel Sant'Angelo.")),
    ("piazza_trilussa", "trastevere", ("Piazza Trilussa a Trastevere, con la fontana e la scalinata.",
                                       "Piazza Trilussa in Trastevere, with its fountain and steps.")),
]

LICENZE = {  # licenza -> pagina ufficiale (None: nessuna pagina propria, si rimanda alla pagina del file su Commons)
    "CC BY 2.0": "https://creativecommons.org/licenses/by/2.0/",
    "CC BY 2.5": "https://creativecommons.org/licenses/by/2.5/",
    "CC BY 3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC BY-SA 2.0": "https://creativecommons.org/licenses/by-sa/2.0/",
    "CC BY-SA 3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
    "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "CC0 1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "Public domain": None,
}

TERRACOTTA = (178, 74, 37)
TRAVERTINO = (245, 240, 230)
INCHIOSTRO = (43, 38, 34)
SECONDARIO = (90, 80, 72)


def scrivi_json(percorso: Path, dati) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(json.dumps(dati, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def testo(x, lingua):
    return x.get(lingua) if isinstance(x, dict) else x


# --- percorsi ------------------------------------------------------------------------------------------------------
def importa_percorsi(app: Path) -> list:
    d = json.loads((app / "app/assets/data/roma.json").read_text(encoding="utf-8"))
    out = []
    for t in d["tours"]:
        tappe = []
        for s in t["stops"]:
            n = s.get("name") or s.get("id")
            tappe.append({"it": testo(n, "it") or s["id"], "en": testo(n, "en") or testo(n, "it") or s["id"]})
        out.append({"id": t["id"], "tipo": t["type"], "titolo": {"it": t["title"]["it"], "en": t["title"]["en"]}, "tappe": tappe})
    scrivi_json(QUI / "content/percorsi.json", out)
    return out


# --- foto ------------------------------------------------------------------------------------------------------------
def ridimensiona(origine: Path, destinazione: Path, larghezza: int) -> tuple:
    im = Image.open(origine).convert("RGB")
    w, h = im.size
    if w > larghezza:
        im = im.resize((larghezza, round(h * larghezza / w)), Image.LANCZOS)
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    im.save(destinazione, "JPEG", quality=82, optimize=True, progressive=True)
    return im.size


def importa_foto(app: Path) -> list:
    out = []
    for pid, percorso, (alt_it, alt_en) in FOTO_DEL_SITO:
        scheda = yaml.safe_load((app / f"content/roma/pois/{pid}.yaml").read_text(encoding="utf-8"))
        img = scheda["image"]
        licenza = img["license"]
        if licenza not in LICENZE:
            sys.exit(f"Licenza non prevista per {pid}: {licenza}")
        # la scheda di qualche foto non scrive il campo «large»: il file c'è lo stesso, col nome di sempre
        grande = app / img.get("large", f"content/roma/images/{pid}_1280.jpg")
        if not grande.exists():
            sys.exit(f"Manca il file della foto di {pid}: {grande}")
        w, h = ridimensiona(grande, QUI / f"assets/img/foto/{pid}-1280.jpg", 1280)
        ridimensiona(grande, QUI / f"assets/img/foto/{pid}-640.jpg", 640)
        out.append({
            "id": pid, "percorso": percorso, "larghezza": w, "altezza": h,
            "alt": {"it": alt_it, "en": alt_en},
            "file_commons": img["file"], "autore": img["author"], "licenza": licenza,
            "licenza_url": LICENZE[licenza], "fonte_url": img["source_url"], "credito_app": img["attribution"],
        })  # chi ha verificato la foto resta nel progetto dell'app: sul sito pubblico non serve
    scrivi_json(QUI / "content/foto.json", out)
    return out


# --- informativa -----------------------------------------------------------------------------------------------------
def importa_informativa(app: Path) -> dict:
    d = yaml.safe_load((app / "content/legale/privacy.yaml").read_text(encoding="utf-8"))
    out = {
        "versione": str(d["versione"]), "aggiornata": d["aggiornata"], "titolo": d["titolo"], "sottotitolo": d["sottotitolo"],
        "sezioni": [{"id": s["id"], "titolo": s["titolo"], "testo": {k: v.strip() for k, v in s["testo"].items()}} for s in d["sezioni"]],
    }
    scrivi_json(QUI / "content/informativa_app.json", out)
    return out


# --- icona -----------------------------------------------------------------------------------------------------------
def carica_disegno_icona(app: Path):
    spec = importlib.util.spec_from_file_location("genera_icona_app", app / "tools/genera_icona.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)  # solo definisce funzioni: non scrive nulla finché non si chiama main()
    return modulo


def angoli_arrotondati(im: Image.Image, raggio_relativo: float = 0.2237) -> Image.Image:
    """Stessa forma «a quadrato morbido» che iOS dà all'icona: serve alle icone del sito che non passano da iOS."""
    lato = im.size[0]
    s = 4
    maschera = Image.new("L", (lato * s, lato * s), 0)
    ImageDraw.Draw(maschera).rounded_rectangle([0, 0, lato * s - 1, lato * s - 1], radius=lato * s * raggio_relativo, fill=255)
    maschera = maschera.resize((lato, lato), Image.LANCZOS)
    rgba = im.convert("RGBA")
    rgba.putalpha(maschera)
    return rgba


def font(percorso: Path, dimensione: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(percorso), dimensione)


def immagine_anteprima(icona: Image.Image, titolo_font: Path, testo_font: Path, frase: str, destinazione: Path) -> None:
    """Immagine 1200x630 per le anteprime sui social: fondo travertino, icona, nome e frase. Solo risorse vere (icona e caratteri)."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), TRAVERTINO)
    d = ImageDraw.Draw(im)
    d.rectangle([0, H - 14, W, H], fill=TERRACOTTA)
    ic = angoli_arrotondati(icona.resize((220, 220), Image.LANCZOS))
    im.paste(ic, (90, 205), ic)
    f_nome = font(titolo_font, 118)
    d.text((350, 200), "ArcoTour", font=f_nome, fill=INCHIOSTRO)
    f_frase = font(testo_font, 40)
    riga, righe = "", []
    for parola in frase.split():
        prova = (riga + " " + parola).strip()
        if d.textlength(prova, font=f_frase) > W - 350 - 70:
            righe.append(riga); riga = parola
        else:
            riga = prova
    righe.append(riga)
    for i, r in enumerate(righe):
        d.text((354, 350 + i * 56), r, font=f_frase, fill=SECONDARIO)
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    im.save(destinazione, "PNG", optimize=True)


def importa_icona(app: Path) -> None:
    disegno = carica_disegno_icona(app)
    grande = disegno.disegna(1024)  # RGB, a tutto quadrato, come l'icona dell'app
    img = QUI / "assets/img"
    img.mkdir(parents=True, exist_ok=True)
    # icone «morbide» per l'intestazione e per le schede del browser
    for lato in (96, 192, 512):
        angoli_arrotondati(grande.resize((lato, lato), Image.LANCZOS)).save(img / f"icona-{lato}.png", optimize=True)
    angoli_arrotondati(grande.resize((32, 32), Image.LANCZOS)).save(img / "favicon-32.png", optimize=True)
    # iOS applica da solo la sua forma all'icona da schermata Home: a tutto quadrato, senza trasparenza
    grande.resize((180, 180), Image.LANCZOS).convert("RGB").save(img / "apple-touch-icon.png", optimize=True)
    # favicon.ico con più misure
    ico = [angoli_arrotondati(grande.resize((n, n), Image.LANCZOS)) for n in (16, 32, 48)]
    ico[2].save(QUI / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:2])
    # anteprime social (italiano e inglese): i caratteri si leggono dal progetto dell'app, senza copiarli
    titolo_font = app / "app/assets/google_fonts/PlayfairDisplay-Bold.ttf"
    testo_font = app / "app/assets/google_fonts/Inter-Regular.ttf"
    immagine_anteprima(grande, titolo_font, testo_font, "Audioguida a piedi per Roma", img / "anteprima-it.png")
    immagine_anteprima(grande, titolo_font, testo_font, "Walking audio tours of Rome", img / "anteprima-en.png")


def copia_caratteri(app: Path) -> None:
    """Copia il Playfair Display dell'app (file IDENTICO, byte per byte) e le licenze dei due caratteri.
    Inter si alleggerisce a parte (tools/prepara_caratteri.py): qui non serve."""
    d = QUI / "assets/fonts"
    d.mkdir(parents=True, exist_ok=True)
    for nome in ("PlayfairDisplay-Bold.ttf", "OFL-Inter.txt", "OFL-PlayfairDisplay.txt"):
        (d / nome).write_bytes((app / "app/assets/google_fonts" / nome).read_bytes())


def git_head(app: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(app), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "sconosciuto"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("app", type=Path, help="cartella del progetto dell'app ArcoTour (letta soltanto)")
    a = p.parse_args(argv)
    app = a.app.resolve()
    if not (app / "app/assets/data/roma.json").exists():
        sys.exit(f"{app} non sembra il progetto di ArcoTour (manca app/assets/data/roma.json)")
    percorsi = importa_percorsi(app)
    foto = importa_foto(app)
    importa_informativa(app)
    copia_caratteri(app)
    importa_icona(app)
    scrivi_json(QUI / "content/origine.json", {
        "importato_il": date.today().isoformat(), "progetto_app": "ArcoTour (privato)", "commit_app": git_head(app),
        "file_letti": ["app/assets/data/roma.json", "content/legale/privacy.yaml", "content/roma/pois/<scheda>.yaml (7 foto)",
                       "content/roma/images/<scheda>_1280.jpg", "tools/genera_icona.py (disegno dell'icona)", "app/assets/google_fonts/*"],
    })
    print(f"Importati: {len(percorsi)} percorsi, {len(foto)} foto, informativa, icona e caratteri.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
