#!/usr/bin/env python3
"""Controlla il sito già costruito. Solo libreria standard.

    python3 tools/check_site.py              # tutti i controlli (esce con 1 se c'è un errore)
    python3 tools/check_site.py --rilascio   # in più il «cancello» della pubblicazione definitiva (vedi sotto)
    python3 tools/check_site.py --esterni    # elenca gli indirizzi esterni usati (da controllare in rete)
    python3 tools/check_site.py --radice DIR # controlla un'altra cartella (lo usano le prove)

Che cosa controlla (ogni punto ha una prova in tools/test_site.py, che gli inserisce di proposito l'errore):
  - struttura: file necessari, .nojekyll, 404, sitemap, robots;
  - collegamenti: ogni href/src/srcset/url() esiste, è RELATIVO (niente «/» iniziale: sotto /arcotour-site/ si romperebbe),
    le ancore #... esistono nella pagina di arrivo, gli indirizzi esterni sono https;
  - SEO: lingua, titolo e descrizione unici, canonical, hreflang reciproci, Open Graph, robots/noindex, JSON-LD, sitemap;
  - accessibilità: un solo h1 e titoli in ordine, riferimenti aria che esistono, alt, nomi dei collegamenti e dei pulsanti,
    collegamento «Vai al contenuto», tabelle con th scope, focus visibile, movimento ridotto, contrasti dei colori (WCAG);
  - privacy: nessuna risorsa esterna, nessuno script che salva dati, nessun modulo, nessun cookie, nessuna email tranne quella
    di assistenza scelta in content/site.json;
  - contenuti: prezzi e durate dei pass uguali a quelli decisi, mai «permanente/illimitato/abbonamento» in positivo,
    crediti delle foto completi e con licenza che permette l'uso commerciale, IT e EN con gli stessi contenuti.
Cancello `--rilascio`: nessun segnaposto «da completare», revisione legale approvata, pagine legali indicizzabili e nella sitemap.
"""
import argparse
import json
import math
import posixpath
import re
import struct
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent

PAGINE = ("index.html", "support.html", "privacy.html", "terms.html")
PAGINE_LEGALI = ("support.html", "privacy.html", "terms.html")
LINGUE = ("it", "en")
FILE_NECESSARI = (
    ".nojekyll", "index.html", "support.html", "privacy.html", "terms.html", "404.html",
    "en/index.html", "en/support.html", "en/privacy.html", "en/terms.html",
    "sitemap.xml", "robots.txt", "favicon.ico",
    "assets/css/site.css", "assets/js/site.js",
    "assets/img/icona-96.png", "assets/img/icona-192.png", "assets/img/icona-512.png", "assets/img/favicon-32.png",
    "assets/img/apple-touch-icon.png", "assets/img/anteprima-it.png", "assets/img/anteprima-en.png",
    "assets/fonts/PlayfairDisplay-Bold.ttf", "assets/fonts/inter-regular.woff2", "assets/fonts/inter-semibold.woff2",
    "assets/fonts/OFL-Inter.txt", "assets/fonts/OFL-PlayfairDisplay.txt",
    "content/site.json", "content/foto.json",
)
ESTENSIONI_TESTO = {".html", ".json", ".xml", ".txt", ".css", ".js", ".md", ".py", ".yml", ".yaml"}
CLASSI_DI_STATO = {"js", "aperto"}  # le aggiunge il JavaScript: non stanno nell'HTML scritto
LICENZE_AMMESSE = ("CC BY 2.0", "CC BY 3.0", "CC BY 4.0", "CC BY-SA 2.0", "CC BY-SA 2.5", "CC BY-SA 3.0", "CC BY-SA 4.0", "CC0", "Public domain")
DIMENSIONE_MASSIMA_HTML = 150_000
DIMENSIONE_MASSIMA_IMMAGINE = 700_000
NEGAZIONI = re.compile(r"\b(non|né|nè|nessun|nessuna|senza|mai|not|no|never|neither|nor|without|isn[’']t|aren[’']t|doesn[’']t|don[’']t)\b", re.I)
# parole che, scritte in positivo, direbbero una cosa falsa dei pass (sono a tempo, a pagamento unico, senza rinnovo)
PAROLE_VIETATE = {
    "it": ("permanent", "illimitat", "a vita", "per sempre", "senza scadenza", "abbonament", "rinnovo", "si rinnova", "rinnovabil"),
    "en": ("permanent", "unlimited", "lifetime", "forever", "never expire", "no expiry", "subscription", "auto-renew", "renewal", "renews"),
}
# strumenti che raccolgono dati o carichino cose da fuori: il sito non ne ha e non ne deve avere
API_VIETATE_NEL_JS = ("document.cookie", "localStorage", "sessionStorage", "indexedDB", "fetch(", "XMLHttpRequest", "sendBeacon",
                      "WebSocket", "navigator.geolocation", "eval(", "new Function", "document.write", "importScripts")
NOMI_TRACCIAMENTO = ("google-analytics", "googletagmanager", "gtag(", "fbq(", "facebook.net", "hotjar", "matomo", "plausible", "mixpanel", "segment.com", "doubleclick")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")


class Esito:
    def __init__(self):
        self.errori, self.avvisi = [], []

    def err(self, file, msg):
        self.errori.append((file, msg))

    def avv(self, file, msg):
        self.avvisi.append((file, msg))


# ------------------------------------------------------------------------------------------------ colori e contrasto
def _canale(c: float) -> float:
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminanza(esadecimale: str) -> float:
    h = esadecimale.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _canale(r) + 0.7152 * _canale(g) + 0.0722 * _canale(b)


def contrasto(a: str, b: str) -> float:
    la, lb = luminanza(a), luminanza(b)
    chiaro, scuro = max(la, lb), min(la, lb)
    return (chiaro + 0.05) / (scuro + 0.05)


# --------------------------------------------------------------------------------------------------- lettura dell'HTML
VUOTI = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
TITOLI = {"h1", "h2", "h3", "h4", "h5", "h6"}
CATTURA = {"title", "a", "button", "summary", "label", "th", "script", "style"} | TITOLI


def _norma(testo: str) -> str:
    return re.sub(r"\s+", " ", testo).strip()


class Analizzatore(HTMLParser):
    """Legge una pagina e ne tiene l'essenziale per i controlli (non è un browser: basta per HTML scritto da un generatore)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pila = []
        self.doctype = None
        self.html = {}
        self.meta, self.link = [], []
        self.ids, self.classi = [], set()
        self.titolo = ""
        self.titoli, self.a, self.img, self.script, self.bottoni = [], [], [], [], []
        self.rif = []
        self.stile_inline = 0
        self.eventi = []
        self.tag = Counter()
        self.testo = []
        self.mal_formato = []
        self.base = None
        self.nav_senza_etichetta = 0
        self.th_senza_scope = 0
        self.foto_senza_credito = []
        self.testo_con_lang = []

    # -- apertura
    def handle_decl(self, decl):
        self.doctype = decl.strip().lower()

    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        self.tag[tag] += 1
        if "id" in a:
            self.ids.append(a["id"])
        if "class" in a:
            self.classi.update(a["class"].split())
        if "style" in a:
            self.stile_inline += 1
        for k in a:
            if k.startswith("on"):
                self.eventi.append((tag, k))
        for k in ("aria-controls", "aria-labelledby", "aria-describedby"):
            if k in a:
                self.rif.extend((k, i) for i in a[k].split())
        if tag == "label" and "for" in a:
            self.rif.append(("for", a["for"]))
        if tag == "html":
            self.html = a
        elif tag == "meta":
            self.meta.append(a)
        elif tag == "link":
            self.link.append(a)
        elif tag == "base":
            self.base = a.get("href")
        elif tag == "nav" and not (a.get("aria-label", "").strip() or a.get("aria-labelledby", "").strip()):
            self.nav_senza_etichetta += 1
        elif tag == "th" and "scope" not in a:
            self.th_senza_scope += 1
        elif tag == "img":
            self.img.append(a)
            for el in self.pila:  # il testo alternativo di un'immagine dentro un collegamento è il nome del collegamento
                if el["tag"] == "a":
                    el["alt"].append(a.get("alt", ""))
            if "/foto/" in a.get("src", ""):
                for el in reversed(self.pila):
                    if el["tag"] in ("figure", "article"):
                        el["foto"] = True
                        break
        if "credito" in a.get("class", "").split():
            for el in reversed(self.pila):
                if el["tag"] in ("figure", "article"):
                    el["credito"] = True
                    break
        if tag in VUOTI:
            return
        self.pila.append({"tag": tag, "attrs": a, "buf": [] if tag in CATTURA else None, "alt": []})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VUOTI:
            self.handle_endtag(tag)

    # -- chiusura
    def handle_endtag(self, tag):
        if tag in VUOTI:
            return
        for i in range(len(self.pila) - 1, -1, -1):
            if self.pila[i]["tag"] == tag:
                break
        else:
            self.mal_formato.append(f"</{tag}> senza apertura")
            return
        if i != len(self.pila) - 1:
            self.mal_formato.append("<" + ">, <".join(e["tag"] for e in self.pila[i + 1:]) + f"> non chiuso prima di </{tag}>")
        while len(self.pila) > i:
            self._chiudi(self.pila.pop())

    def _chiudi(self, el):
        tag, a = el["tag"], el["attrs"]
        grezzo = "".join(el["buf"]) if el["buf"] is not None else ""
        testo = _norma(grezzo)
        if tag == "title":
            self.titolo = testo
        elif tag in TITOLI:
            self.titoli.append((int(tag[1]), testo, a.get("id")))
        elif tag == "a":
            self.a.append({"href": a.get("href"), "testo": testo, "attrs": a, "alt": _norma(" ".join(el["alt"]))})
        elif tag == "button":
            self.bottoni.append({"testo": testo, "attrs": a})
        elif tag in ("script", "style"):
            self.script.append((tag, a, grezzo))
        elif tag in ("figure", "article") and el.get("foto") and not el.get("credito"):
            self.foto_senza_credito.append(tag)

    def handle_data(self, data):
        dentro_codice = False
        for el in self.pila:
            if el["buf"] is not None:
                el["buf"].append(data)
            if el["tag"] in ("script", "style", "title"):
                dentro_codice = True
        if not dentro_codice:
            self.testo.append(data)

    # -- comodi
    def meta_contenuto(self, chiave):
        for m in self.meta:
            if m.get("name") == chiave or m.get("property") == chiave:
                return m.get("content", "")
        return None

    def link_rel(self, rel):
        return [l for l in self.link if rel in l.get("rel", "").split()]

    @property
    def testo_visibile(self):
        return _norma(" ".join(self.testo))

    def json_ld(self):
        return [grezzo for tag, a, grezzo in self.script if tag == "script" and a.get("type") == "application/ld+json"]


def leggi(testo: str) -> Analizzatore:
    p = Analizzatore()
    p.feed(testo)
    p.close()
    return p


# ------------------------------------------------------------------------------------------------------ il sito
class Sito:
    def __init__(self, radice: Path):
        self.radice = radice
        self.dati = json.loads((radice / "content" / "site.json").read_text(encoding="utf-8"))
        self.base_url = self.dati["base_url"]
        if not self.base_url.startswith("https://") or not self.base_url.endswith("/"):
            raise SystemExit("content/site.json: base_url deve cominciare con https:// e finire con /")
        self.percorso_base = "/" + self.base_url.split("://", 1)[1].split("/", 1)[1]
        self.testi, self.pagine, self._ids = {}, {}, {}
        for f in self.file_html():
            self.testi[f] = (radice / f).read_text(encoding="utf-8")
            self.pagine[f] = leggi(self.testi[f])

    def file_html(self):
        ammessi = list(PAGINE) + ["404.html"] + ["en/" + p for p in PAGINE]
        return [f for f in ammessi if (self.radice / f).is_file()]

    @property
    def bozza(self) -> bool:
        """Stessa regola del generatore, riscritta qui apposta: le pagine legali sono «in revisione» finché mancano i dati di chi pubblica o la revisione legale."""
        v = self.dati["venditore"]
        manca = any(not (v.get(k) or "").strip() or v[k].strip().startswith("DA_COMPLETARE") for k in ("nome", "indirizzo", "email"))
        return self.dati.get("revisione_legale") != "approvata" or manca

    def url_atteso(self, file: str) -> str:
        if file == "index.html":
            return self.base_url
        if file == "en/index.html":
            return self.base_url + "en/"
        return self.base_url + file

    def file_da_url(self, url: str):
        if url == self.base_url:
            return "index.html"
        if url == self.base_url + "en/":
            return "en/index.html"
        if url.startswith(self.base_url):
            return url[len(self.base_url):]
        return None

    def ids_di(self, file: str):
        if file not in self._ids:
            if file in self.pagine:
                p = self.pagine[file]
                nomi = {l["attrs"].get("name") for l in p.a if l["attrs"].get("name")}
                self._ids[file] = set(p.ids) | nomi
            else:
                self._ids[file] = set()
        return self._ids[file]


# ------------------------------------------------------------------------------------------ risoluzione dei collegamenti
def risolvi(sito: Sito, file_pagina: str, valore: str, con_base: bool = False):
    """Che cosa indica un collegamento? -> (tipo, file, frammento, errore)
    tipo: ancora | file | esterno | mailto | errore.  file = percorso dalla radice del sito."""
    v = (valore or "").strip()
    if not v:
        return "errore", None, None, "collegamento vuoto"
    if v.startswith("#"):
        return "ancora", file_pagina, unquote(v[1:]), None
    if v.startswith("//"):
        return "errore", None, None, "indirizzo senza protocollo («//…»): usa https:// o un percorso relativo"
    if v.startswith("/"):
        return "errore", None, None, "percorso che parte da «/»: sotto /arcotour-site/ non troverebbe il file (usa un percorso relativo)"
    m = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*):", v)
    if m:
        schema = m.group(1).lower()
        if schema == "https":
            return "esterno", v, None, None
        if schema == "http":
            return "errore", v, None, "indirizzo http:// non protetto (usa https://)"
        if schema == "mailto":
            return "mailto", v, None, None
        return "errore", v, None, f"indirizzo «{schema}:» non ammesso"
    parti = urlsplit(v)
    percorso, frammento = unquote(parti.path), unquote(parti.fragment)
    cartella = "" if con_base else posixpath.dirname(file_pagina)
    dest = posixpath.normpath(posixpath.join(cartella, percorso)) if percorso else file_pagina
    if dest.startswith(".."):
        return "errore", None, None, "il percorso esce dalla cartella del sito"
    if dest == ".":
        dest = ""
    if percorso.endswith("/") or dest == "" or (sito.radice / dest).is_dir():
        dest = posixpath.join(dest, "index.html")
    return "file", dest, frammento, None


def controlla_riferimento(sito: Sito, e: Esito, file_pagina: str, valore: str, cosa: str, con_base: bool, esterni: Counter, solo_file: bool = False):
    tipo, dest, frammento, errore = risolvi(sito, file_pagina, valore, con_base)
    if errore:
        e.err(file_pagina, f"{cosa} «{valore}»: {errore}")
        return
    if tipo == "esterno":
        if solo_file:
            e.err(file_pagina, f"{cosa} «{valore}»: il sito non carica nulla da altri siti")
        else:
            esterni[valore] += 1
        return
    if tipo == "mailto":
        if solo_file:
            e.err(file_pagina, f"{cosa} «{valore}»: non è un file")
        return
    if tipo == "ancora" or tipo == "file":
        if not (sito.radice / dest).is_file():
            e.err(file_pagina, f"{cosa} «{valore}»: il file {dest} non esiste")
            return
        if frammento and frammento != "top":
            if dest.endswith(".html"):
                if frammento not in sito.ids_di(dest):
                    e.err(file_pagina, f"{cosa} «{valore}»: nella pagina {dest} non c'è l'ancora #{frammento}")
            else:
                e.err(file_pagina, f"{cosa} «{valore}»: l'ancora #{frammento} non ha senso su un file che non è una pagina")


# ------------------------------------------------------------------------------------------------ controlli per pagina
def lingua_di(file: str) -> str:
    return "en" if file.startswith("en/") else "it"


def controlla_pagina(sito: Sito, e: Esito, file: str, p: Analizzatore, esterni: Counter):
    lingua = lingua_di(file)
    e_404 = file == "404.html"
    testo = sito.testi[file]
    if len(testo.encode("utf-8")) > DIMENSIONE_MASSIMA_HTML:
        e.err(file, f"pagina troppo pesante ({len(testo.encode('utf-8')) // 1000} KB)")
    if (p.doctype or "") != "doctype html":
        e.err(file, "manca <!doctype html> (senza, il browser lavora in «quirks mode»)")
    for m in p.mal_formato:
        e.err(file, f"HTML non ben formato: {m}")
    if p.html.get("lang") != lingua:
        e.err(file, f"<html lang> è «{p.html.get('lang')}», doveva essere «{lingua}»")
    if not any(m.get("charset", "").lower() == "utf-8" for m in p.meta):
        e.err(file, "manca <meta charset=\"utf-8\">")
    vp = p.meta_contenuto("viewport")
    if not vp or "width=device-width" not in vp:
        e.err(file, "manca il viewport per i telefoni (width=device-width)")
    elif re.search(r"maximum-scale|user-scalable\s*=\s*(no|0)", vp):
        e.err(file, "il viewport blocca l'ingrandimento: chi ha bisogno di ingrandire non può")
    if not p.titolo:
        e.err(file, "manca il <title>")
    elif len(p.titolo) > 70:
        e.avv(file, f"titolo lungo ({len(p.titolo)} caratteri): i motori di ricerca lo tagliano")
    desc = p.meta_contenuto("description")
    if not desc:
        e.err(file, "manca la meta description")
    elif not 60 <= len(desc) <= 190 and file != "404.html":
        e.avv(file, f"meta description di {len(desc)} caratteri (meglio tra 60 e 190)")

    # robots / noindex
    robots = (p.meta_contenuto("robots") or "").lower()
    voluto_noindex = e_404 or (sito.bozza and file.split("/")[-1] in PAGINE_LEGALI)
    if voluto_noindex and "noindex" not in robots:
        e.err(file, "questa pagina deve avere <meta name=\"robots\" content=\"noindex…\"> (è la 404 o una pagina legale ancora «in revisione»)")
    if not voluto_noindex and "noindex" in robots:
        e.err(file, "la pagina ha noindex ma dovrebbe comparire nei motori di ricerca")

    # canonical, lingue alternative, social
    if not e_404:
        canon = p.link_rel("canonical")
        if len(canon) != 1:
            e.err(file, f"serve esattamente un <link rel=canonical> (ce ne sono {len(canon)})")
        elif canon[0].get("href") != sito.url_atteso(file):
            e.err(file, f"canonical «{canon[0].get('href')}» invece di «{sito.url_atteso(file)}»")
        alt = {l.get("hreflang"): l.get("href") for l in p.link_rel("alternate") if l.get("hreflang")}
        nome = file.split("/")[-1]
        attese = {"it": sito.url_atteso(nome), "en": sito.url_atteso("en/" + nome), "x-default": sito.url_atteso(nome)}
        if alt != attese:
            e.err(file, f"lingue alternative (hreflang) sbagliate: {alt} invece di {attese}")
        for chiave in ("og:title", "og:description", "og:type", "og:url", "og:image", "og:locale", "og:site_name", "twitter:card"):
            if not p.meta_contenuto(chiave):
                e.err(file, f"manca {chiave} (anteprima quando il collegamento viene condiviso)")
        if p.meta_contenuto("og:url") and p.meta_contenuto("og:url") != sito.url_atteso(file):
            e.err(file, "og:url diverso dal canonical")
        if p.meta_contenuto("og:locale") and p.meta_contenuto("og:locale")[:2] != lingua:
            e.err(file, "og:locale non corrisponde alla lingua della pagina")
        immagine = p.meta_contenuto("og:image") or ""
        f_img = sito.file_da_url(immagine)
        if not f_img or not (sito.radice / f_img).is_file():
            e.err(file, f"og:image «{immagine}» non porta a un file del sito")
        elif f_img.endswith(".png"):
            dim = dimensioni_png(sito.radice / f_img)
            if dim != (1200, 630):
                e.err(file, f"l'anteprima social {f_img} misura {dim}, doveva essere 1200×630")
    else:
        base = p.base
        if base != sito.percorso_base:
            e.err(file, f"la 404 deve avere <base href=\"{sito.percorso_base}\"> (è «{base}»): senza, i suoi collegamenti si rompono da pagine in cartelle diverse")

    # struttura e titoli
    if p.tag["header"] != 1 or p.tag["main"] != 1 or p.tag["footer"] != 1:
        e.err(file, f"servono un solo <header>, un solo <main> e un solo <footer> (ci sono {p.tag['header']}, {p.tag['main']}, {p.tag['footer']})")
    if p.nav_senza_etichetta:
        e.err(file, "ogni <nav> deve avere un aria-label (ce ne sono più d'una)")
    h1 = [t for t in p.titoli if t[0] == 1]
    if len(h1) != 1:
        e.err(file, f"serve un solo <h1> (ce ne sono {len(h1)})")
    if p.titoli and p.titoli[0][0] != 1:
        e.err(file, "il primo titolo della pagina non è un <h1>")
    for prima, dopo in zip(p.titoli, p.titoli[1:]):
        if dopo[0] > prima[0] + 1:
            e.err(file, f"salto di livello nei titoli: «{prima[1]}» (h{prima[0]}) seguito da «{dopo[1]}» (h{dopo[0]})")
    for liv, t, _ in p.titoli:
        if not t:
            e.err(file, f"titolo h{liv} vuoto")
    ripetuti = [i for i, n in Counter(p.ids).items() if n > 1]
    if ripetuti:
        e.err(file, f"id ripetuti nella stessa pagina: {', '.join(sorted(ripetuti))}")
    for attr, i in p.rif:
        if i not in p.ids:
            e.err(file, f"{attr}=\"{i}\" punta a un id che non c'è")
    main_id = None
    # collegamento «Vai al contenuto»: il primo della pagina, verso il <main>
    if p.a:
        primo = p.a[0]["attrs"].get("href", "")
        if not primo.startswith("#") or primo[1:] not in p.ids:
            e.err(file, "il primo collegamento della pagina dev'essere «Vai al contenuto» verso un id esistente")
    else:
        e.err(file, "nessun collegamento nella pagina")
    if p.tag["details"] != p.tag["summary"]:
        e.err(file, "ogni <details> deve avere il suo <summary>")
    if p.th_senza_scope:
        e.err(file, f"{p.th_senza_scope} celle <th> senza scope (le tabelle devono dire se l'intestazione è di colonna o di riga)")
    for b in p.bottoni:
        if not (b["testo"] or b["attrs"].get("aria-label")):
            e.err(file, "pulsante senza nome (testo o aria-label)")
        if b["attrs"].get("aria-controls") and "aria-expanded" not in b["attrs"]:
            e.err(file, "pulsante che apre/chiude qualcosa senza aria-expanded")
        if b["attrs"].get("type") is None:
            e.err(file, "pulsante senza type (dentro un modulo invierebbe dati)")
    for tag in ("form", "input", "textarea", "select", "iframe", "embed", "object", "video", "audio", "canvas"):
        if p.tag[tag]:
            e.err(file, f"<{tag}> non ammesso: il sito non raccoglie dati e non incorpora contenuti di altri")
    if p.stile_inline:
        e.err(file, f"{p.stile_inline} stili scritti dentro l'HTML (style=\"…\"): vanno nel foglio di stile")
    for tag, evento in p.eventi:
        e.err(file, f"gestore di evento scritto dentro l'HTML (<{tag} {evento}=…>)")
    if p.foto_senza_credito:
        e.err(file, "una foto senza il suo credito (autore, licenza, Wikimedia Commons) nella stessa scheda")

    # immagini
    for im in p.img:
        src = im.get("src", "")
        if "alt" not in im:
            e.err(file, f"immagine senza attributo alt: {src}")
        if not im.get("width") or not im.get("height"):
            e.err(file, f"immagine senza width/height (la pagina «salta» mentre carica): {src}")
        if im.get("alt", "x") == "" and "/foto/" in src:
            e.err(file, f"foto senza testo alternativo: {src}")
        controlla_riferimento(sito, e, file, src, "immagine", e_404, esterni, solo_file=True)
        for cand in (c.strip() for c in im.get("srcset", "").split(",") if c.strip()):
            controlla_riferimento(sito, e, file, cand.split()[0], "immagine (srcset)", e_404, esterni, solo_file=True)
    # collegamenti
    for l in p.a:
        href, a = l["href"], l["attrs"]
        if href is None:
            if not a.get("name"):
                e.err(file, f"collegamento senza href: «{l['testo']}»")
            continue
        if not (l["testo"] or l["alt"] or a.get("aria-label")):
            e.err(file, f"collegamento senza nome per chi usa lo screen reader: {href}")
        if a.get("target") == "_blank" and "noopener" not in a.get("rel", ""):
            e.err(file, f"collegamento con target=_blank senza rel=noopener: {href}")
        controlla_riferimento(sito, e, file, href, "collegamento", e_404, esterni)
        if href.startswith("mailto:") and not EMAIL.fullmatch(href[7:].split("?")[0]):
            e.err(file, f"indirizzo email non valido in {href}")
    # link, script e stili caricati
    for l in p.link:
        rel = l.get("rel", "").split()
        href = l.get("href")
        if href is None:
            continue
        if any(r in rel for r in ("canonical", "alternate")):
            continue
        controlla_riferimento(sito, e, file, href, f"<link rel={' '.join(rel)}>", e_404, esterni, solo_file=True)
    for tag, a, grezzo in p.script:
        if tag != "script":
            continue
        if a.get("src"):
            controlla_riferimento(sito, e, file, a["src"], "script", e_404, esterni, solo_file=True)
            if "defer" not in a and "async" not in a:
                e.avv(file, f"script {a['src']} senza defer: rallenta la comparsa della pagina")
        elif a.get("type") == "application/ld+json":
            try:
                json.loads(grezzo)
            except ValueError as ex:
                e.err(file, f"dati strutturati JSON-LD non validi: {ex}")
            for url in re.findall(r"https?://[^\"\s]+", grezzo):
                if not url.startswith(sito.base_url) and "schema.org" not in url:
                    e.err(file, f"nei dati strutturati c'è un indirizzo che non è del sito: {url}")
        elif grezzo.strip() != "document.documentElement.className='js'":
            e.err(file, "script scritto dentro la pagina diverso da quello ammesso (document.documentElement.className='js')")
    for nome in NOMI_TRACCIAMENTO:
        if nome in testo.lower():
            e.err(file, f"traccia di uno strumento di analisi/tracciamento: «{nome}»")
    # la 404 deve poter essere aperta da qualsiasi cartella: ogni suo collegamento ai file dipende da <base>
    if e_404 and "noindex" not in robots:
        e.err(file, "la 404 deve essere noindex")


def dimensioni_png(percorso: Path):
    dati = percorso.read_bytes()[:24]
    if dati[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", dati[16:24])


# ------------------------------------------------------------------------------------------------ testi e promesse
def frasi(testo: str):
    return [f.strip() for f in re.split(r"(?<=[.!?;:])\s+", testo) if f.strip()]


def controlla_testo(sito: Sito, e: Esito):
    pass_ = sito.dati["pass"]
    for file, p in sito.pagine.items():
        lingua = lingua_di(file)
        testo = p.testo_visibile
        if re.search(r"DA_COMPLETARE|lorem ipsum|\bTODO\b|\bXXX\b", testo, re.I):
            e.err(file, "nel testo visibile resta un segnaposto grezzo (DA_COMPLETARE, TODO…)")
        # parole che non devono comparire in positivo
        for fr in frasi(testo):
            if fr.endswith("?"):
                continue  # una domanda («È un abbonamento?») non afferma niente: conta la risposta
            for parola in PAROLE_VIETATE[lingua]:
                if parola in fr.lower() and not NEGAZIONI.search(fr):
                    e.err(file, f"frase che promette il contrario del vero sui pass («{parola}» senza negazione): «{fr[:140]}»")
        # prezzi e durate
        prezzi_ammessi = {pp["prezzo"][lingua] for pp in pass_}
        for m in re.finditer(r"€\s?\d+(?:[.,]\d{2})?", testo):
            prezzo = m.group(0).replace(" ", "")
            if prezzo not in prezzi_ammessi:
                e.err(file, f"prezzo «{prezzo}» non previsto (ammessi: {', '.join(sorted(prezzi_ammessi))})")
        ore_ammesse = {str(pp["ore"]) for pp in pass_}
        for fr in frasi(testo):
            if re.search(r"\b(esempio|example)\b", fr, re.I):
                continue  # in un esempio («24 ore comprate a mezzogiorno e altre 24 ore comprate 12 ore dopo…») i numeri sono di chi spiega
            for m in re.finditer(r"(\d+)\s*(ore|hours)\b", fr):
                if m.group(1) not in ore_ammesse:
                    e.err(file, f"durata «{m.group(0)}» non prevista (ammesse: {', '.join(sorted(ore_ammesse))} ore)")
            for m in re.finditer(r"(\d+)\s*(giorni|days)\b", fr):
                if m.group(1) != "10":
                    e.err(file, f"durata «{m.group(0)}» non prevista (il pass lungo dura 10 giorni)")
        completo = next(pp for pp in pass_ if pp["id"] == "pass10d")
        if completo["nome"][lingua] in testo and "240" not in testo:
            e.err(file, f"cita «{completo['nome'][lingua]}» ma non dice che dura 10 giorni (240 ore)")
    # la pagina iniziale deve mostrare i tre pass con il loro prezzo
    for file in ("index.html", "en/index.html"):
        if file not in sito.pagine:
            continue
        lingua, testo = lingua_di(file), sito.pagine[file].testo_visibile
        for pp in pass_:
            nome, prezzo, durata = pp["nome"][lingua], pp["prezzo"][lingua], pp["durata"][lingua]
            i = testo.find(nome)
            if i < 0 or prezzo not in testo[i:i + 220] or durata not in testo[i:i + 220]:
                e.err(file, f"il pass «{nome}» non compare con la sua durata «{durata}» e il suo prezzo «{prezzo}»")
    # stato dell'app e collegamento all'App Store
    stato, url_app = sito.dati["app"]["stato"], sito.dati["app"].get("app_store_url", "")
    for file, p in sito.pagine.items():
        store = [l["href"] for l in p.a if l["href"] and re.match(r"https://(apps|itunes)\.apple\.com/", l["href"])]
        if stato == "prossimamente":
            if store:
                e.err(file, "c'è un collegamento all'App Store ma l'app risulta ancora «prossimamente» in content/site.json")
            if file in ("index.html", "en/index.html") and not re.search(r"Prossimamente|Coming soon", p.testo_visibile):
                e.err(file, "l'app non è ancora pubblicata: la pagina iniziale deve dire «Prossimamente»")
        elif stato == "disponibile":
            if not url_app.startswith("https://apps.apple.com/"):
                e.err(file, "stato «disponibile» ma app_store_url non è un indirizzo https://apps.apple.com/…")
            if file in ("index.html", "en/index.html") and url_app not in store:
                e.err(file, "app disponibile: la pagina iniziale deve collegarsi all'App Store")
            if re.search(r"Prossimamente|Coming soon", p.testo_visibile):
                e.err(file, "app disponibile ma la pagina dice ancora «prossimamente»")
        else:
            e.err("content/site.json", f"app.stato «{stato}» non riconosciuto (prossimamente | disponibile)")


def controlla_foto(sito: Sito, e: Esito):
    """Ogni foto del sito: solo Wikimedia Commons, autore e licenza che permettono l'uso commerciale, con il suo credito."""
    foto = json.loads((sito.radice / "content" / "foto.json").read_text(encoding="utf-8"))
    per_id = {f["id"]: f for f in foto}
    for f in foto:
        host = urlsplit(f["fonte_url"]).netloc
        if host != "commons.wikimedia.org":
            e.err("content/foto.json", f"{f['id']}: la fonte non è Wikimedia Commons ({host})")
        atteso = "File:" + f["file_commons"].replace(" ", "_")
        if unquote(urlsplit(f["fonte_url"]).path).rsplit("/wiki/", 1)[-1] != atteso:
            e.err("content/foto.json", f"{f['id']}: l'indirizzo non corrisponde al nome del file «{f['file_commons']}»")
        if f["licenza"] not in LICENZE_AMMESSE:
            e.err("content/foto.json", f"{f['id']}: licenza «{f['licenza']}» non ammessa (serve una che permetta l'uso commerciale)")
        if f["licenza"] != "Public domain" and not (f.get("licenza_url") or "").startswith("https://creativecommons.org/"):
            e.err("content/foto.json", f"{f['id']}: manca il collegamento alla licenza")
        if not f.get("autore"):
            e.err("content/foto.json", f"{f['id']}: manca l'autore")
        for lato in (640, 1280):
            if not (sito.radice / f"assets/img/foto/{f['id']}-{lato}.jpg").is_file():
                e.err("content/foto.json", f"{f['id']}: manca il file assets/img/foto/{f['id']}-{lato}.jpg")
    usate = set()
    for file, p in sito.pagine.items():
        for im in p.img:
            m = re.search(r"/foto/(.+)-(?:640|1280)\.jpg$", im.get("src", ""))
            if m:
                usate.add(m.group(1))
                if m.group(1) not in per_id:
                    e.err(file, f"foto {m.group(1)} usata ma non descritta in content/foto.json")
    for f in Path(sito.radice / "assets/img/foto").glob("*.jpg"):
        nome = re.sub(r"-(640|1280)$", "", f.stem)
        if nome not in per_id:
            e.err(f"assets/img/foto/{f.name}", "foto senza scheda in content/foto.json (autore, licenza, fonte)")
        if f.stat().st_size > DIMENSIONE_MASSIMA_IMMAGINE:
            e.err(f"assets/img/foto/{f.name}", f"foto troppo pesante ({f.stat().st_size // 1000} KB)")
    for file in ("index.html", "en/index.html"):
        if file not in sito.pagine:
            continue
        p = sito.pagine[file]
        testo = p.testo_visibile
        urls = {l["href"] for l in p.a if l["href"]}
        for pid in usate:
            f = per_id.get(pid)
            if not f:
                continue
            if f["autore"] not in testo:
                e.err(file, f"nei crediti manca l'autore «{f['autore']}» della foto {pid}")
            if f["fonte_url"] not in urls:
                e.err(file, f"nei crediti manca il collegamento alla pagina Commons della foto {pid}")
            if f["licenza"] != "Public domain" and f["licenza_url"] not in urls:
                e.err(file, f"nei crediti manca il collegamento alla licenza della foto {pid}")
        if usate and "Wikimedia Commons" not in testo:
            e.err(file, "le foto vengono da Wikimedia Commons ma la pagina non lo dice")


# --------------------------------------------------------------------------------------------- IT e EN uguali
def chiave_collegamento(sito: Sito, file: str, l: dict):
    href = l["href"]
    if not href:
        return None
    tipo, dest, frammento, errore = risolvi(sito, file, href, file == "404.html")
    if errore:
        return None
    if tipo == "esterno":
        return ("esterno", urlsplit(dest).netloc)
    if tipo in ("file", "ancora"):
        d = dest[3:] if dest.startswith("en/") else dest
        return ("interno", d, frammento or "")
    return (tipo,)


def controlla_coerenza_lingue(sito: Sito, e: Esito):
    for pagina in PAGINE:
        it, en = sito.pagine.get(pagina), sito.pagine.get("en/" + pagina)
        if not it or not en:
            e.err("en/" + pagina, "manca una delle due lingue")
            continue
        for livello in (2, 3):
            n_it, n_en = sum(1 for t in it.titoli if t[0] == livello), sum(1 for t in en.titoli if t[0] == livello)
            if n_it != n_en:
                e.err("en/" + pagina, f"titoli h{livello}: {n_it} in italiano, {n_en} in inglese")
        if set(it.ids) != set(en.ids):
            diff = sorted(set(it.ids) ^ set(en.ids))
            e.err("en/" + pagina, f"id diversi tra italiano e inglese (le ancore non funzionerebbero in tutte e due): {', '.join(diff)}")
        k_it = Counter(k for k in (chiave_collegamento(sito, pagina, l) for l in it.a) if k and k[0] == "interno")
        k_en = Counter(k for k in (chiave_collegamento(sito, "en/" + pagina, l) for l in en.a) if k and k[0] == "interno")
        if k_it != k_en:
            diff = sorted(str(k) for k in set(k_it.items()) ^ set(k_en.items()))
            e.err("en/" + pagina, f"i collegamenti interni non sono gli stessi nelle due lingue: {', '.join(diff[:6])}")
        if len(it.img) != len(en.img):
            e.err("en/" + pagina, f"{len(it.img)} immagini in italiano, {len(en.img)} in inglese")
        if it.tag["details"] != en.tag["details"]:
            e.err("en/" + pagina, "numero diverso di domande frequenti")
        # selettore della lingua: ciascuna pagina rimanda all'altra e viceversa
        for file, altra_lingua, altro in ((pagina, "en", "en/" + pagina), ("en/" + pagina, "it", pagina)):
            p = sito.pagine[file]
            vers = [l for l in p.a if l["attrs"].get("hreflang") == altra_lingua]
            if len(vers) != 1:
                e.err(file, f"serve un solo collegamento alla versione «{altra_lingua}» (ce ne sono {len(vers)})")
            else:
                tipo, dest, _, errore = risolvi(sito, file, vers[0]["href"])
                if errore or dest != altro:
                    e.err(file, f"il selettore della lingua porta a «{vers[0]['href']}» invece di {altro}")
        if it.titolo == en.titolo:
            e.avv("en/" + pagina, "titolo uguale nelle due lingue")
    # titoli e descrizioni unici
    for chiave, valori in (("title", {f: p.titolo for f, p in sito.pagine.items()}),
                           ("description", {f: p.meta_contenuto("description") for f, p in sito.pagine.items() if p.meta_contenuto("description")})):
        visti = {}
        for f, v in valori.items():
            if v in visti:
                e.err(f, f"{chiave} identico a quello di {visti[v]}: ogni pagina ha il suo")
            visti[v] = f


# ---------------------------------------------------------------------------------------------- file del sito
def testo_css(radice: Path) -> str:
    return (radice / "assets/css/site.css").read_text(encoding="utf-8")


def senza_commenti(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def controlla_css(sito: Sito, e: Esito, esterni: Counter):
    f = "assets/css/site.css"
    css = senza_commenti(testo_css(sito.radice))
    if css.count("{") != css.count("}"):
        e.err(f, f"graffe non bilanciate ({css.count('{')} aperte, {css.count('}')} chiuse)")
    if "@import" in css:
        e.err(f, "@import: il sito non carica fogli di stile da fuori")
    for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", css):
        u = m.group(1)
        if re.match(r"^(https?:)?//", u) or u.startswith("data:"):
            e.err(f, f"url({u}): il foglio di stile non carica nulla da fuori")
            continue
        if not (sito.radice / "assets/css" / u).resolve().is_file():
            e.err(f, f"url({u}): il file non esiste (il percorso è relativo al foglio di stile)")
    for blocco in re.findall(r"@font-face\s*\{[^}]*\}", css):
        if "font-display" not in blocco:
            e.err(f, "un @font-face senza font-display (il testo resterebbe invisibile finché il carattere non arriva)")
    if not re.search(r":focus-visible", css):
        e.err(f, "manca lo stile del focus (chi usa la tastiera non vedrebbe dove si trova)")
    if not re.search(r"prefers-reduced-motion", css):
        e.err(f, "manca @media (prefers-reduced-motion): le animazioni vanno spente per chi lo chiede")
    if re.search(r"outline\s*:\s*(none|0)\b", css):
        e.err(f, "«outline: none» toglie l'indicatore del focus")
    for m in re.finditer(r"font-size\s*:\s*([\d.]+)rem", css):
        if float(m.group(1)) < 0.75:
            e.avv(f, f"carattere molto piccolo ({m.group(0)})")
    # ogni classe usata nell'HTML esiste nel foglio di stile (si trovano gli errori di battitura)
    pulito = re.sub(r"url\([^)]*\)|\"[^\"]*\"|'[^']*'", "", css)
    definite = set(re.findall(r"\.(-?[A-Za-z_][\w-]*)", pulito))
    for file, p in sito.pagine.items():
        mancanti = sorted(c for c in p.classi if c not in definite and c not in CLASSI_DI_STATO)
        if mancanti:
            e.err(file, f"classi usate nell'HTML ma assenti dal foglio di stile: {', '.join(mancanti)}")
    # larghezza dei telefoni
    if not re.search(r"@media[^{]*max-width", css) and not re.search(r"@media[^{]*min-width", css):
        e.err(f, "nessuna regola per schermi di larghezze diverse (@media)")


COPPIE_DI_COLORE = [  # (testo, sfondo, minimo, a cosa serve)
    ("inchiostro", "travertino", 7.0, "testo normale"), ("inchiostro", "avorio", 7.0, "testo sulle fasce chiare"),
    ("inchiostro", "bianco", 7.0, "testo nelle schede"), ("inchiostro", "sabbia", 7.0, "testo sul piè di pagina"),
    ("inchiostro", "ocra-chiara", 7.0, "avviso «in revisione»"),
    ("secondario", "travertino", 4.5, "testo secondario"), ("secondario", "avorio", 4.5, "testo secondario"),
    ("secondario", "bianco", 4.5, "testo secondario"), ("secondario", "sabbia", 4.5, "note del piè di pagina"),
    ("terracotta-scura", "travertino", 4.5, "collegamenti"), ("terracotta-scura", "avorio", 4.5, "collegamenti"),
    ("terracotta-scura", "bianco", 4.5, "collegamenti"), ("terracotta-scura", "sabbia", 4.5, "collegamenti nel piè di pagina"),
    ("terracotta-scura", "ocra-chiara", 4.5, "collegamenti nell'avviso"),
    ("bianco", "terracotta", 4.5, "pulsanti pieni"), ("bianco", "inchiostro", 7.0, "«Vai al contenuto»"),
    ("terracotta", "travertino", 3.0, "indicatore del focus"), ("terracotta", "bianco", 3.0, "elementi grafici"),
    ("verde", "bianco", 3.0, "segni di spunta"),
]


def controlla_contrasti(sito: Sito, e: Esito):
    f = "assets/css/site.css"
    css = senza_commenti(testo_css(sito.radice))
    colori = {m.group(1): m.group(2) for m in re.finditer(r"--([\w-]+)\s*:\s*(#[0-9A-Fa-f]{3,6})\s*;", css)}
    for testo, sfondo, minimo, a_cosa in COPPIE_DI_COLORE:
        if testo not in colori or sfondo not in colori:
            e.err(f, f"colore --{testo} o --{sfondo} non definito")
            continue
        c = contrasto(colori[testo], colori[sfondo])
        if c < minimo:
            e.err(f, f"contrasto {c:.2f}:1 tra {testo} e {sfondo} ({a_cosa}): serve almeno {minimo}:1")
    # in più: ogni regola del foglio di stile che dà colore e sfondo insieme
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, corpo = " ".join(m.group(1).split()), m.group(2)
        if sel.startswith("@"):
            continue
        c1 = re.search(r"(?<![-\w])color\s*:\s*(?:var\(--([\w-]+)\)|(#[0-9A-Fa-f]{3,6}))", corpo)
        c2 = re.search(r"background(?:-color)?\s*:\s*(?:var\(--([\w-]+)\)|(#[0-9A-Fa-f]{3,6}))\s*[;]?\s*$|background(?:-color)?\s*:\s*(?:var\(--([\w-]+)\)|(#[0-9A-Fa-f]{3,6}))\s*;", corpo)
        if not (c1 and c2):
            continue
        testo = colori.get(c1.group(1)) if c1.group(1) else c1.group(2)
        nome_sfondo = c2.group(1) or c2.group(3)
        sfondo = colori.get(nome_sfondo) if nome_sfondo else (c2.group(2) or c2.group(4))
        if not testo or not sfondo:
            continue
        c = contrasto(testo, sfondo)
        if c < 3.0:
            e.err(f, f"{sel}: contrasto {c:.2f}:1 tra testo e sfondo (sotto il minimo di 3:1)")
        elif c < 4.5:
            e.avv(f, f"{sel}: contrasto {c:.2f}:1 (va bene solo per testo grande)")


def controlla_js(sito: Sito, e: Esito):
    cartella = sito.radice / "assets/js"
    for js in sorted(cartella.glob("*.js")):
        codice = js.read_text(encoding="utf-8")
        for api in API_VIETATE_NEL_JS:
            if api in codice:
                e.err(f"assets/js/{js.name}", f"usa «{api}»: il sito non salva dati, non fa richieste e non esegue codice scritto altrove")
        if re.search(r"https?://", codice):
            e.err(f"assets/js/{js.name}", "contiene un indirizzo di rete")
        for nome in NOMI_TRACCIAMENTO:
            if nome in codice.lower():
                e.err(f"assets/js/{js.name}", f"traccia di uno strumento di analisi: «{nome}»")


def controlla_file_e_dati(sito: Sito, e: Esito):
    for f in FILE_NECESSARI:
        if not (sito.radice / f).is_file():
            e.err(f, "file necessario mancante")
    for f in ("assets/img/apple-touch-icon.png",):
        if (sito.radice / f).is_file() and dimensioni_png(sito.radice / f) != (180, 180):
            e.err(f, f"deve misurare 180×180 (misura {dimensioni_png(sito.radice / f)})")
    # nessun file che Pages tratterebbe in modo diverso da come si pensa
    if (sito.radice / "_config.yml").exists() and not (sito.radice / ".nojekyll").exists():
        e.err("_config.yml", "c'è una configurazione Jekyll ma manca .nojekyll")
    for strano in sito.radice.rglob("*"):
        rel = strano.relative_to(sito.radice).as_posix()
        if rel.startswith(".git/") or "__pycache__" in rel or not strano.is_file():
            continue
        if re.search(r"[A-Z]", strano.name) and strano.suffix in (".html", ".css", ".js") and not strano.name.startswith(("OFL", "README")):
            e.avv(rel, "nome di file con maiuscole (GitHub Pages distingue maiuscole e minuscole)")
        if " " in strano.name:
            e.err(rel, "spazio nel nome del file")
    # sitemap e robots
    try:
        albero = ET.parse(sito.radice / "sitemap.xml").getroot()
    except (ET.ParseError, OSError) as ex:
        e.err("sitemap.xml", f"non è un XML valido: {ex}")
        albero = None
    if albero is not None:
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}
        locs = [u.findtext("s:loc", namespaces=ns) for u in albero.findall("s:url", ns)]
        for loc in locs:
            f = sito.file_da_url(loc or "")
            if not f or not (sito.radice / f).is_file():
                e.err("sitemap.xml", f"indirizzo {loc} che non porta a una pagina del sito")
            elif "noindex" in (sito.pagine[f].meta_contenuto("robots") or "").lower():
                e.err("sitemap.xml", f"{loc} è nella sitemap ma la pagina è noindex")
        if len(set(locs)) != len(locs):
            e.err("sitemap.xml", "indirizzi ripetuti")
        for pagina in PAGINE:
            for l in LINGUE:
                f = pagina if l == "it" else "en/" + pagina
                voluto = not (sito.bozza and pagina in PAGINE_LEGALI)
                presente = sito.url_atteso(f) in locs
                if voluto and not presente:
                    e.err("sitemap.xml", f"manca {sito.url_atteso(f)}")
                if not voluto and presente:
                    e.err("sitemap.xml", f"{sito.url_atteso(f)} non deve esserci finché la pagina è «in revisione»")
        for u in albero.findall("s:url", ns):
            for l in u.findall("x:link", ns):
                f = sito.file_da_url(l.get("href", ""))
                if not f or not (sito.radice / f).is_file():
                    e.err("sitemap.xml", f"alternativa di lingua {l.get('href')} che non esiste")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", u.findtext("s:lastmod", namespaces=ns) or ""):
                e.err("sitemap.xml", "lastmod mancante o non nel formato AAAA-MM-GG")
    robots = (sito.radice / "robots.txt").read_text(encoding="utf-8") if (sito.radice / "robots.txt").is_file() else ""
    if f"Sitemap: {sito.base_url}sitemap.xml" not in robots:
        e.err("robots.txt", f"manca la riga «Sitemap: {sito.base_url}sitemap.xml»")
    if re.search(r"^\s*Disallow:\s*/\s*$", robots, re.M):
        e.err("robots.txt", "«Disallow: /» chiude tutto il sito ai motori di ricerca")
    # caratteri: licenza accanto ai file
    for f in (sito.radice / "assets/fonts").glob("*"):
        if f.suffix in (".ttf", ".woff2") and f.stat().st_size > 500_000:
            e.avv(f"assets/fonts/{f.name}", f"carattere pesante ({f.stat().st_size // 1000} KB)")


def controlla_privacy(sito: Sito, e: Esito):
    """Nessuna email nei file pubblici tranne quella di assistenza scelta in content/site.json (mai quella personale di qualcuno)."""
    v = sito.dati["venditore"]["email"]
    ammessa = None if (not v.strip() or v.strip().startswith("DA_COMPLETARE")) else v.strip().lower()
    for f in sorted(sito.radice.rglob("*")):
        rel = f.relative_to(sito.radice).as_posix()
        if not f.is_file() or rel.startswith(".git/") or "__pycache__" in rel or f.suffix not in ESTENSIONI_TESTO:
            continue
        try:
            testo = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for m in EMAIL.finditer(testo):
            indirizzo = m.group(0).lower()
            if indirizzo == ammessa or indirizzo.split("@")[0] == "noreply" or indirizzo.endswith("@users.noreply.github.com"):
                continue  # gli indirizzi «noreply» non sono di nessuna persona
            if rel.startswith("tools/test_site.py"):
                continue
            e.err(rel, f"indirizzo email «{m.group(0)}» in un file pubblico: l'unico ammesso è quello di assistenza in content/site.json")


def controlla_rilascio(sito: Sito, e: Esito):
    """Il «cancello»: tutto quel che deve essere vero prima di dire a Apple «questo è il sito»."""
    f = "content/site.json"
    v = sito.dati["venditore"]
    for chiave, nome in (("nome", "nome o ragione sociale di chi pubblica"), ("indirizzo", "indirizzo o sede di chi pubblica"), ("email", "email di assistenza")):
        if not (v.get(chiave) or "").strip() or v[chiave].strip().startswith("DA_COMPLETARE"):
            e.err(f, f"manca {nome} (venditore.{chiave}): finché è un segnaposto il sito non è pubblicabile")
    if sito.dati.get("revisione_legale") != "approvata":
        e.err(f, "revisione_legale non è «approvata»: condizioni e informativa devono prima essere lette da un legale")
    for file, p in sito.pagine.items():
        if "segnaposto" in p.classi:
            e.err(file, "ci sono ancora segnaposto «da completare» nella pagina")
        if "bozza" in p.classi:
            e.err(file, "c'è ancora l'avviso «versione in revisione»")
        if "noindex" in (p.meta_contenuto("robots") or "") and file != "404.html":
            e.err(file, "la pagina è ancora noindex")
    for pagina in PAGINE_LEGALI:
        for l in LINGUE:
            f_ = pagina if l == "it" else "en/" + pagina
            sitemap = (sito.radice / "sitemap.xml").read_text(encoding="utf-8")
            if sito.url_atteso(f_) not in sitemap:
                e.err("sitemap.xml", f"{sito.url_atteso(f_)} non è nella sitemap")
    email = v.get("email", "").strip()
    if email and not email.startswith("DA_COMPLETARE") and not EMAIL.fullmatch(email):
        e.err(f, f"venditore.email «{email}» non è un indirizzo email")
    if sito.dati["app"]["stato"] == "prossimamente":
        e.avv(f, "l'app risulta «prossimamente»: dopo la pubblicazione su App Store cambia stato e app_store_url")


# ------------------------------------------------------------------------------------------------------- insieme
def controlla(radice: Path = RADICE, rilascio: bool = False):
    """Esegue tutti i controlli: restituisce (Esito, indirizzi esterni)."""
    e, esterni = Esito(), Counter()
    sito = Sito(radice)
    mancanti = [f for f in ["index.html", "support.html", "privacy.html", "terms.html", "404.html"] + ["en/" + p for p in PAGINE] if f not in sito.pagine]
    for f in mancanti:
        e.err(f, "pagina mancante")
    controlla_file_e_dati(sito, e)
    for file, p in sito.pagine.items():
        controlla_pagina(sito, e, file, p, esterni)
    controlla_testo(sito, e)
    controlla_foto(sito, e)
    controlla_coerenza_lingue(sito, e)
    if (sito.radice / "assets/css/site.css").is_file():
        controlla_css(sito, e, esterni)
        controlla_contrasti(sito, e)
    controlla_js(sito, e)
    controlla_privacy(sito, e)
    # pagine legali «in revisione»: devono dirlo (avviso) e viceversa
    for file, p in sito.pagine.items():
        if file.split("/")[-1] in PAGINE_LEGALI:
            if sito.bozza and "bozza" not in p.classi:
                e.err(file, "i dati di chi pubblica non sono completi ma la pagina non mostra l'avviso «in revisione»")
            if not sito.bozza and ("bozza" in p.classi or "segnaposto" in p.classi):
                e.err(file, "i dati sono completi e la revisione approvata ma la pagina mostra ancora avvisi o segnaposto: rigenera con tools/build_site.py")
    if rilascio:
        controlla_rilascio(sito, e)
    return e, esterni


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--radice", type=Path, default=RADICE)
    ap.add_argument("--rilascio", action="store_true", help="in più, il cancello della pubblicazione definitiva")
    ap.add_argument("--esterni", action="store_true", help="elenca gli indirizzi esterni (non fa altri controlli di rete)")
    a = ap.parse_args(argv)
    e, esterni = controlla(a.radice, a.rilascio)
    if a.esterni:
        for url, n in sorted(esterni.items()):
            print(f"{n:3d}  {url}")
        return 0
    for file, msg in e.errori:
        print(f"ERRORE  {file}: {msg}")
    for file, msg in e.avvisi:
        print(f"avviso  {file}: {msg}")
    print(f"\n{len(e.errori)} errori, {len(e.avvisi)} avvisi" + (" (con il cancello di pubblicazione)" if a.rilascio else ""))
    if not e.errori:
        print("Il sito è in regola." if not a.rilascio else "Il sito è pronto per la pubblicazione definitiva.")
    return 1 if e.errori else 0


if __name__ == "__main__":
    sys.exit(main())
