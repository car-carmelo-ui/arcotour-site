"""Costruisce le pagine del sito ArcoTour. SOLO libreria standard (nessuna dipendenza da installare).

Entrata: content/site.json (indirizzo del sito, dati di chi pubblica, pass), content/percorsi.json, content/foto.json,
content/informativa_app.json (importati dall'app: tools/importa_da_app.py) e i testi in tools/contenuti_it.py / contenuti_en.py.
Uscita: le pagine HTML (italiano alla radice, inglese in en/), 404.html, sitemap.xml, robots.txt.

Principi:
  - TUTTI i collegamenti interni sono RELATIVI (dal file in cui stanno): il sito funziona sotto /arcotour-site/ e anche
    se un giorno avrà un dominio suo.
  - Nessuna risorsa esterna (né caratteri, né script, né immagini di altri) e nessun cookie.
  - Nessun dato inventato: nome, indirizzo ed email di chi pubblica stanno in content/site.json; finché sono segnaposto
    «DA_COMPLETARE…» le pagine legali sono marcate «in revisione» e non indicizzabili.
"""
import html
import json
import posixpath
import re
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent
sys.path.insert(0, str(QUI))

import contenuti_en  # noqa: E402
import contenuti_it  # noqa: E402

LINGUE = ("it", "en")
PAGINE = ("index.html", "support.html", "privacy.html", "terms.html")
PAGINE_LEGALI = ("support.html", "privacy.html", "terms.html")  # quelle con i dati di chi pubblica
TESTI = {"it": contenuti_it.T, "en": contenuti_en.T}
NOMI_LICENZA = {"it": {"Public domain": "pubblico dominio"}, "en": {"Public domain": "public domain"}}


# ----------------------------------------------------------------------------------------------------- dati
def carica_dati(radice: Path = RADICE) -> dict:
    def j(nome):
        return json.loads((radice / "content" / nome).read_text(encoding="utf-8"))
    return {"sito": j("site.json"), "percorsi": j("percorsi.json"), "foto": j("foto.json"), "informativa": j("informativa_app.json")}


def e_segnaposto(valore) -> bool:
    v = (valore or "").strip()
    return not v or v.startswith("DA_COMPLETARE")


PUNTO_APERTO = re.compile(r"\{[!?][^{}]+\}")  # {!testo} = scritto ma da confermare · {?etichetta} = un dato che manca nel testo


def punti_aperti(informativa: dict) -> bool:
    """True se il testo dell'informativa ha ancora un punto «da confermare» {!…} o un dato che manca {?…}."""
    return bool(PUNTO_APERTO.search(json.dumps(informativa["sezioni"], ensure_ascii=False)))


def bozza_legale(sito: dict, informativa: dict = None) -> bool:
    """Le pagine legali sono «in revisione» finché mancano i dati di chi pubblica, la revisione legale non è approvata o il testo dell'informativa ha
    ancora punti da confermare {!…} o dati che mancano {?…} (13/10/2026: così una pagina con un punto aperto non può passare per definitiva)."""
    v = sito["venditore"]
    return (sito.get("revisione_legale") != "approvata" or any(e_segnaposto(v[k]) for k in ("nome", "indirizzo", "email"))
            or (informativa is not None and punti_aperti(informativa)))


# ------------------------------------------------------------------------------------------------ contesto
class Ctx:
    """Tutto quel che serve per scrivere UNA pagina: lingua, nome del file, testi, dati."""

    def __init__(self, dati: dict, lingua: str, pagina: str):
        self.dati, self.sito, self.lingua, self.pagina = dati, dati["sito"], lingua, pagina
        self.T = TESTI[lingua]

    @property
    def file(self) -> str:
        """Percorso del file di questa pagina, dalla radice del sito."""
        return self.pagina if self.lingua == "it" else "en/" + self.pagina

    def file_di(self, pagina: str, lingua: str = None) -> str:
        lingua = lingua or self.lingua
        return pagina if lingua == "it" else "en/" + pagina

    def rel(self, destinazione: str) -> str:
        """Percorso RELATIVO da questa pagina a un file del sito (dato dalla radice)."""
        cartella = posixpath.dirname(self.file) or "."
        return posixpath.relpath(destinazione, cartella)

    def url(self, destinazione: str) -> str:
        """Indirizzo completo (per canonical, sitemap, anteprime social)."""
        base = self.sito["base_url"]
        if destinazione == "index.html":
            return base
        if destinazione == "en/index.html":
            return base + "en/"
        return base + destinazione

    @property
    def bozza(self) -> bool:
        return bozza_legale(self.sito, self.dati["informativa"])


# ------------------------------------------------------------------------------------------- piccolo linguaggio
def esc(s) -> str:
    return html.escape(str(s), quote=True)


def tipografia(s: str) -> str:
    """Apostrofo tipografico (’) dopo una lettera: l'app -> l’app, de' Fiori -> de’ Fiori. Solo sul testo, mai negli indirizzi."""
    return re.sub(r"(?<=\w)'", "’", s)


def valore_venditore(ctx: Ctx, chiave: str) -> str:
    """HTML del dato di chi pubblica: il dato vero, oppure un segnaposto ben visibile."""
    v = ctx.sito["venditore"][chiave]
    if e_segnaposto(v):
        nome_segnaposto = {"nome": "titolare"}.get(chiave, chiave)  # nel file dei dati si chiama «nome», nei testi «titolare»
        return f'<span class="segnaposto">{esc(ctx.T["ui"]["segnaposto"][nome_segnaposto])}</span>'
    if chiave == "email":
        return f'<a href="mailto:{esc(v)}">{esc(v)}</a>'
    return esc(tipografia(v))


def segnaposti(ctx: Ctx, testo_escaped: str, extra: dict = None) -> str:
    """Sostituisce {email}, {titolare}, {indirizzo}, {data}, {aggiornata}, {p24}, {p72}, {p10}, {durata}, {n} (testo già con l'escape fatto)
    e i due segni dell'informativa: {?etichetta} = un dato che MANCA, {!testo} = un testo scritto che aspetta una CONFERMA."""
    lingua, sito = ctx.lingua, ctx.sito
    pass_ = {p["id"]: p for p in sito["pass"]}
    valori = {
        "email": valore_venditore(ctx, "email"),
        "titolare": valore_venditore(ctx, "nome"),
        "indirizzo": valore_venditore(ctx, "indirizzo"),
        "data": esc(ctx.T["ui"]["data_aggiornamento"]),
        "aggiornata": esc(ctx.dati["informativa"]["aggiornata"][lingua]),
        "p24": esc(pass_["pass24h"]["prezzo"][lingua]),
        "p72": esc(pass_["pass72h"]["prezzo"][lingua]),
        "p10": esc(pass_["pass10d"]["prezzo"][lingua]),
    }
    for k, v in (extra or {}).items():
        valori[k] = esc(v)
    # {?etichetta}: come per l'indirizzo, finché il dato non c'è si vede «[da completare: etichetta]» (classe `segnaposto`).
    # {!testo}: un testo già scritto che aspetta una conferma (un legale, il titolare): evidenziato (<mark class="da-confermare">) e la pagina resta
    # «in revisione» (bozza_legale). check_site.py non lascia pubblicare come definitiva una pagina che ne ha ancora uno. Dentro non ci sono
    # collegamenti [testo](indirizzo): un punto da confermare è testo semplice.
    prefisso = esc(ctx.T["ui"]["da_completare"])
    testo_escaped = re.sub(r"\{\?([^{}]+)\}", lambda m: f'<span class="segnaposto">[{prefisso}: {m.group(1)}]</span>', testo_escaped)
    testo_escaped = re.sub(r"\{!([^{}]+)\}", lambda m: f'<mark class="da-confermare">{m.group(1)}</mark>', testo_escaped)
    return re.sub(r"\{(\w+)\}", lambda m: valori.get(m.group(1), m.group(0)), testo_escaped)


def risolvi(ctx: Ctx, href: str) -> str:
    """@pagina.html#ancora = pagina del sito nella stessa lingua; @@percorso = file del sito; il resto è un indirizzo esterno."""
    if href.startswith("@@"):
        return ctx.rel(href[2:])
    if href.startswith("@"):
        nome, _, ancora = href[1:].partition("#")
        r = ctx.rel(ctx.file_di(nome))
        return r + ("#" + ancora if ancora else "")
    return href


# indirizzi che l'informativa dell'app scrive come semplice testo: sul sito diventano collegamenti (solo questi, scelti a mano:
# tile.openstreetmap.org, per esempio, è un server di mappe e non una pagina da aprire)
INDIRIZZI_COLLEGABILI = {
    "osmfoundation.org/wiki/Privacy_Policy": "https://osmfoundation.org/wiki/Privacy_Policy",
    "apple.com/legal/privacy": "https://www.apple.com/legal/privacy/",
    "garanteprivacy.it": "https://www.garanteprivacy.it/",
}


def inline(ctx: Ctx, testo: str, extra: dict = None) -> str:
    """Un pezzo di testo: collegamenti [testo](indirizzo), **grassetto**, segnaposto. Restituisce HTML con l'escape fatto."""
    pezzi, ultimo = [], 0

    def semplice(t, collega=False):
        t = esc(tipografia(t))
        if collega:  # solo fuori da un collegamento già scritto: un <a> dentro un <a> non esiste
            for visibile, url in INDIRIZZI_COLLEGABILI.items():
                t = re.sub(re.escape(esc(visibile)) + r"(?![\w/-])", lambda m: f'<a href="{esc(url)}">{m.group(0)}</a>', t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        return segnaposti(ctx, t, extra)

    for m in re.finditer(r"\[([^\]]+)\]\(([^)\s]+)\)", testo):
        pezzi.append(semplice(testo[ultimo:m.start()], collega=True))
        pezzi.append(f'<a href="{esc(risolvi(ctx, m.group(2)))}">{semplice(m.group(1))}</a>')
        ultimo = m.end()
    pezzi.append(semplice(testo[ultimo:], collega=True))
    return "".join(pezzi)


def blocchi(ctx: Ctx, testo: str, extra: dict = None) -> str:
    """Paragrafi (separati da una riga vuota) ed elenchi (righe che iniziano con «- »)."""
    out, par, lista = [], [], []

    def chiudi_par():
        if par:
            out.append("<p>" + inline(ctx, " ".join(par), extra) + "</p>")
            par.clear()

    def chiudi_lista():
        if lista:
            out.append("<ul>" + "".join(f"<li>{inline(ctx, v, extra)}</li>" for v in lista) + "</ul>")
            lista.clear()

    for riga in testo.split("\n"):
        if riga.startswith("- "):
            chiudi_par()
            lista.append(riga[2:].strip())
        elif not riga.strip():
            chiudi_par()
            chiudi_lista()
        else:
            chiudi_lista()
            par.append(riga.strip())
    chiudi_par()
    chiudi_lista()
    return "\n".join(out)


def solo_testo(ctx: Ctx, testo: str) -> str:
    """Il testo senza segni (per titoli e descrizioni nei <meta>): niente HTML, niente segnaposto."""
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", testo)
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    return tipografia(t)


# ---------------------------------------------------------------------------------------------- foto e crediti
def foto_per_id(dati: dict, pid: str) -> dict:
    return next(f for f in dati["foto"] if f["id"] == pid)


def licenza_visibile(ctx: Ctx, f: dict) -> str:
    return NOMI_LICENZA[ctx.lingua].get(f["licenza"], f["licenza"])


def credito_html(ctx: Ctx, f: dict) -> str:
    """«Foto: autore, licenza, via Wikimedia Commons»: con il collegamento alla licenza e alla pagina del file."""
    lic = esc(licenza_visibile(ctx, f))
    if f["licenza_url"]:
        lic = f'<a href="{esc(f["licenza_url"])}">{lic}</a>'
    fonte = f'<a href="{esc(f["fonte_url"])}">Wikimedia Commons</a>'
    return f'{esc(ctx.T["ui"]["foto"])}: {esc(tipografia(f["autore"]))}, {lic}, via {fonte}'


def img_foto(ctx: Ctx, f: dict, *, sizes: str, lazy: bool = True, alta: bool = False) -> str:
    base = f'assets/img/foto/{f["id"]}'
    attr = "" if not lazy else ' loading="lazy" decoding="async"'
    if alta:
        attr = ' fetchpriority="high" decoding="async"'
    return (f'<img src="{esc(ctx.rel(base + "-1280.jpg"))}" srcset="{esc(ctx.rel(base + "-640.jpg"))} 640w, {esc(ctx.rel(base + "-1280.jpg"))} 1280w" '
            f'sizes="{esc(sizes)}" width="{f["larghezza"]}" height="{f["altezza"]}" alt="{esc(tipografia(f["alt"][ctx.lingua]))}"{attr}>')


def maiuscola(s: str) -> str:
    return s[:1].upper() + s[1:]


# -------------------------------------------------------------------------------------- struttura della pagina
def intestazione(ctx: Ctx) -> str:
    T = ctx.T
    voci = []
    for v in T["nav"]:
        corrente = ' aria-current="page"' if (v["id"] == "supporto" and ctx.pagina == "support.html") else ""
        voci.append(f'<li><a href="{esc(risolvi(ctx, v["href"]))}"{corrente}>{esc(v["etichetta"])}</a></li>')
    altra = "en" if ctx.lingua == "it" else "it"
    etichette = {"it": "IT", "en": "EN"}
    nomi = {"it": "Italiano", "en": "English"}

    def voce_lingua(l):
        if l == ctx.lingua:
            return f'<span lang="{l}" aria-label="{nomi[l]}" aria-current="true">{etichette[l]}</span>'
        # la 404 non ha una gemella nell'altra lingua: si va alla pagina iniziale
        destinazione = ctx.file_di("index.html", l) if ctx.pagina == "404.html" else ctx.file_di(ctx.pagina, l)
        return (f'<a lang="{l}" hreflang="{l}" aria-label="{nomi[l]}" href="{esc(ctx.rel(destinazione))}">{etichette[l]}</a>')

    ordine = ("it", "en")
    return (
        '<header class="intestazione">\n<div class="contenitore">\n'
        f'<a class="marchio" href="{esc(ctx.rel(ctx.file_di("index.html")))}" aria-label="{esc(T["ui"]["home_aria"])}">'
        f'<img src="{esc(ctx.rel("assets/img/icona-96.png"))}" width="40" height="40" alt=""><span>ArcoTour</span></a>\n'
        f'<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu-principale">{esc(T["ui"]["menu"])}</button>\n'
        f'<nav class="nav" id="menu-principale" aria-label="{esc(T["ui"]["menu_aria"])}"><ul>{"".join(voci)}</ul></nav>\n'
        f'<div class="lingua" role="group" aria-label="{esc(T["ui"]["lingua_aria"])}">{"".join(voce_lingua(l) for l in ordine)}</div>\n'
        '</div>\n</header>'
    )


def piede(ctx: Ctx) -> str:
    P = ctx.T["piede"]
    link = "".join(f'<li><a href="{esc(risolvi(ctx, v["href"]))}">{esc(v["etichetta"])}</a></li>' for v in P["link"])
    return (
        '<footer class="piede">\n<div class="contenitore">\n<div class="piede-griglia">\n<div>\n'
        f'<a class="marchio" href="{esc(ctx.rel(ctx.file_di("index.html")))}" aria-label="{esc(ctx.T["ui"]["home_aria"])}">'
        f'<img src="{esc(ctx.rel("assets/img/icona-96.png"))}" width="40" height="40" alt=""><span>ArcoTour</span></a>\n'
        f'<p class="frase">{esc(tipografia(P["frase"]))}</p>\n</div>\n'
        f'<nav aria-label="{esc(P["titolo_link"])}"><ul>{link}</ul></nav>\n</div>\n'
        f'<div class="note">\n<p>{esc(tipografia(P["marchi"]))}</p>\n<p>{esc(tipografia(P["foto_nota"]))}</p>\n<p>{esc(tipografia(P["copyright"]))}</p>\n</div>\n'
        '</div>\n</footer>'
    )


def documento(ctx: Ctx, *, titolo: str, descrizione: str, corpo: str, noindex: bool = False, json_ld: dict = None,
              canonical_file: str = None, base_href: str = None, alternate: bool = True) -> str:
    """La pagina intera: <head> con titolo, descrizione, canonical, lingue alternative, anteprime social; poi intestazione, corpo e piè."""
    T, lingua = ctx.T, ctx.lingua
    f = canonical_file or ctx.file
    canonical = ctx.url(f)
    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(solo_testo(ctx, titolo))}</title>",
        f'<meta name="description" content="{esc(solo_testo(ctx, descrizione))}">',
        '<meta name="theme-color" content="#F5F0E6">',
        '<meta name="color-scheme" content="light">',
    ]
    if base_href:
        head.insert(2, f'<base href="{esc(base_href)}">')
    if noindex:
        head.append('<meta name="robots" content="noindex, follow">')
    head.append(f'<link rel="canonical" href="{esc(canonical)}">')
    if alternate:
        for l in LINGUE:
            head.append(f'<link rel="alternate" hreflang="{l}" href="{esc(ctx.url(ctx.file_di(ctx.pagina, l)))}">')
        head.append(f'<link rel="alternate" hreflang="x-default" href="{esc(ctx.url(ctx.file_di(ctx.pagina, "it")))}">')
    anteprima = ctx.sito["base_url"] + f"assets/img/anteprima-{lingua}.png"
    altro_locale = TESTI["en" if lingua == "it" else "it"]["locale"]
    head += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="ArcoTour">',
        f'<meta property="og:title" content="{esc(solo_testo(ctx, titolo))}">',
        f'<meta property="og:description" content="{esc(solo_testo(ctx, descrizione))}">',
        f'<meta property="og:url" content="{esc(canonical)}">',
        f'<meta property="og:locale" content="{T["locale"]}">',
        f'<meta property="og:locale:alternate" content="{altro_locale}">',
        f'<meta property="og:image" content="{esc(anteprima)}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc("ArcoTour, " + T["home"]["occhiello"].split(" · ")[0].lower())}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<link rel="icon" href="{esc(ctx.rel("favicon.ico"))}" sizes="any">',
        f'<link rel="icon" type="image/png" sizes="32x32" href="{esc(ctx.rel("assets/img/favicon-32.png"))}">',
        f'<link rel="apple-touch-icon" href="{esc(ctx.rel("assets/img/apple-touch-icon.png"))}">',
        f'<link rel="preload" href="{esc(ctx.rel("assets/fonts/PlayfairDisplay-Bold.ttf"))}" as="font" type="font/ttf" crossorigin>',
        f'<link rel="preload" href="{esc(ctx.rel("assets/fonts/inter-regular.woff2"))}" as="font" type="font/woff2" crossorigin>',
        f'<link rel="stylesheet" href="{esc(ctx.rel("assets/css/site.css"))}">',
        "<script>document.documentElement.className='js'</script>",
        f'<script src="{esc(ctx.rel("assets/js/site.js"))}" defer></script>',
    ]
    if json_ld:
        head.append('<script type="application/ld+json">' + json.dumps(json_ld, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")
    return (
        f'<!doctype html>\n<html lang="{lingua}">\n<head>\n' + "\n".join(head) + "\n</head>\n<body>\n"
        f'<a class="salta" href="#contenuto">{esc(T["ui"]["salta"])}</a>\n'
        + intestazione(ctx) + '\n<main id="contenuto">\n' + corpo + "\n</main>\n" + piede(ctx) + "\n</body>\n</html>\n"
    )


def occhiello(testo: str) -> str:
    return f'<p class="occhiello">{esc(tipografia(testo))}</p>'


# --------------------------------------------------------------------------------------------- pagina iniziale
def percorso_della_foto(dati: dict) -> list:
    """I percorsi che hanno una foto sul sito, nell'ordine dell'app, con la foto."""
    per_id = {f["percorso"]: f for f in dati["foto"] if f["percorso"]}
    return [(p, per_id[p["id"]]) for p in dati["percorsi"] if p["id"] in per_id]


def scheda_percorso(ctx: Ctx, p: dict, f: dict) -> str:
    L, T = ctx.lingua, ctx.T
    tipo = T["ui"]["in_metro"] if p["tipo"] == "metro" else T["ui"]["a_piedi"]
    n = len(p["tappe"])
    nomi = [maiuscola(t[L]) for t in p["tappe"]]
    mostrate = nomi if n <= 5 else nomi[:4]  # con 5 tappe si vedono tutte: «e altre 1 tappe» non esiste
    elenco = " · ".join(mostrate) + (" · " + T["ui"]["e_altre"].format(n=n - 4) if n > 5 else "")
    etichetta_tappe = T["ui"]["tappa"] if n == 1 else T["ui"]["tappe"]
    return (
        '<article class="scheda">\n'
        + img_foto(ctx, f, sizes="(min-width: 60rem) 22rem, (min-width: 40rem) 45vw, 92vw") + "\n"
        '<div class="scheda-corpo">\n'
        f'<ul class="meta"><li>{esc(tipo)}</li><li>{n} {esc(etichetta_tappe)}</li></ul>\n'
        f'<h3>{esc(tipografia(p["titolo"][L]))}</h3>\n'
        f'<p class="tappe-elenco">{esc(tipografia(elenco))}</p>\n'
        f'<p class="credito">{credito_html(ctx, f)}</p>\n'
        "</div>\n</article>"
    )


def sezione_eroe(ctx: Ctx) -> str:
    H = ctx.T["home"]
    f = foto_per_id(ctx.dati, "colosseo")
    stato = ctx.sito["app"]["stato"]
    disp = H["disponibilita"]["disponibile" if stato == "disponibile" else "prossimamente"]
    disp_html = esc(tipografia(disp))
    if stato == "disponibile":
        url_app = ctx.sito["app"].get("app_store_url", "")
        if not url_app.startswith("https://apps.apple.com/"):
            raise SystemExit("content/site.json: con stato «disponibile» serve app_store_url (https://apps.apple.com/…)")
        disp_html = f'<a href="{esc(url_app)}">{disp_html}</a>'
    return (
        '<section class="eroe" aria-labelledby="titolo-eroe">\n<div class="contenitore">\n<div>\n'
        + occhiello(H["occhiello"]) + "\n"
        f'<h1 id="titolo-eroe">{esc(tipografia(H["h1"]))}</h1>\n'
        f'<p class="lead">{esc(tipografia(H["lead"]))}</p>\n'
        '<div class="pulsanti">'
        f'<a class="pulsante pulsante-primario" href="#roma">{esc(H["cta_principale"])}</a>'
        f'<a class="pulsante pulsante-secondario" href="#come-funziona">{esc(H["cta_secondaria"])}</a></div>\n'
        f'<p class="disponibilita">{disp_html}</p>\n</div>\n'
        '<figure class="arco">\n<div class="arco-cornice">\n'
        + img_foto(ctx, f, sizes="(min-width: 60rem) 26rem, 86vw", lazy=False, alta=True) + "\n</div>\n"
        f'<figcaption class="credito">{credito_html(ctx, f)}</figcaption>\n</figure>\n</div>\n</section>'
    )


def sezione_fatti(ctx: Ctx) -> str:
    voci = "".join(f'<li><span class="valore">{esc(v["valore"])}</span><span class="etichetta">{esc(tipografia(v["etichetta"]))}</span></li>'
                   for v in ctx.T["home"]["fatti"])
    return f'<section class="fatti sezione-avorio" aria-label="ArcoTour"><div class="contenitore"><ul>{voci}</ul></div></section>'


def sezione_come(ctx: Ctx) -> str:
    C = ctx.T["home"]["come"]
    passi = "".join(f'<li class="passo"><h3>{esc(tipografia(p["titolo"]))}</h3><p>{esc(tipografia(p["testo"]))}</p></li>' for p in C["passi"])
    return ('<section id="come-funziona" aria-labelledby="titolo-come">\n<div class="contenitore">\n<div class="testata">\n'
            + occhiello(C["occhiello"]) + f'\n<h2 id="titolo-come">{esc(tipografia(C["h2"]))}</h2>\n</div>\n<ol class="passi">{passi}</ol>\n</div>\n</section>')


def sezione_roma(ctx: Ctx) -> str:
    R, L = ctx.T["home"]["roma"], ctx.lingua
    schede = "\n".join(scheda_percorso(ctx, p, f) for p, f in percorso_della_foto(ctx.dati))
    elenco = []
    for p in ctx.dati["percorsi"]:
        n = len(p["tappe"])
        tipo = ctx.T["ui"]["in_metro"] if p["tipo"] == "metro" else ctx.T["ui"]["a_piedi"]
        et = ctx.T["ui"]["tappa"] if n == 1 else ctx.T["ui"]["tappe"]
        elenco.append(f'<li><span><span class="nome">{esc(tipografia(p["titolo"][L]))}</span><span class="dettaglio">{esc(tipo)} · {n} {esc(et)}</span></span></li>')
    return (
        '<section id="roma" class="sezione-avorio" aria-labelledby="titolo-roma">\n<div class="contenitore">\n<div class="testata">\n'
        + occhiello(R["occhiello"]) + f'\n<h2 id="titolo-roma">{esc(tipografia(R["h2"]))}</h2>\n<p class="lead">{esc(tipografia(R["lead"]))}</p>\n</div>\n'
        f'<div class="griglia griglia-percorsi">\n{schede}\n</div>\n'
        f'<h3 class="sottotitolo-sezione">{esc(R["tutti"])}</h3>\n<ol class="elenco-percorsi">{"".join(elenco)}</ol>\n'
        f'<p class="nota nota-sotto">{esc(tipografia(R["nota"]))}</p>\n</div>\n</section>'
    )


def sezione_audioguide(ctx: Ctx) -> str:
    A = ctx.T["home"]["audioguide"]
    punti = "".join(f"<li>{esc(tipografia(p))}</li>" for p in A["punti"])
    return (
        '<section id="audioguide" aria-labelledby="titolo-audio">\n<div class="contenitore due-colonne">\n<div>\n'
        + occhiello(A["occhiello"]) + f'\n<h2 id="titolo-audio">{esc(tipografia(A["h2"]))}</h2>\n' + blocchi(ctx, A["testo"])
        + f'\n<ul class="punti">{punti}</ul>\n</div>\n'
        f'<div class="citazione"><p>{esc(tipografia(A["citazione"]))}</p><p>{esc(tipografia(A["citazione_nota"]))}</p></div>\n</div>\n</section>'
    )


def sezione_mappe(ctx: Ctx) -> str:
    M = ctx.T["home"]["mappe"]
    schede = "".join(f'<article class="scheda"><div class="scheda-corpo"><h3>{esc(tipografia(s["titolo"]))}</h3><p>{esc(tipografia(s["testo"]))}</p></div></article>' for s in M["schede"])
    return (
        '<section id="mappe" class="sezione-sabbia" aria-labelledby="titolo-mappe">\n<div class="contenitore">\n<div class="testata">\n'
        + occhiello(M["occhiello"]) + f'\n<h2 id="titolo-mappe">{esc(tipografia(M["h2"]))}</h2>\n<p class="lead">{esc(tipografia(M["lead"]))}</p>\n</div>\n'
        f'<div class="griglia griglia-3">{schede}</div>\n<p class="nota nota-sotto">{esc(tipografia(M["nota"]))}</p>\n</div>\n</section>'
    )


def sezione_pass(ctx: Ctx) -> str:
    P, L = ctx.T["home"]["pass"], ctx.lingua
    carte = []
    for p in ctx.sito["pass"]:
        bollini = "".join(f"<li>{esc(b)}</li>" for b in P["bollini"])
        carte.append(
            '<article class="pass">\n'
            f'<h3>{esc(tipografia(p["nome"][L]))}</h3>\n<p class="durata">{esc(P["dall_acquisto"].format(durata=p["durata"][L]))}</p>\n'
            f'<p class="prezzo">{esc(p["prezzo"][L])}</p>\n<p class="contenuto">{esc(P["per_ogni"])}</p>\n'
            f'<ul class="bollini">{bollini}</ul>\n</article>')
    punti = "".join(f"<li>{esc(tipografia(x))}</li>" for x in P["punti"])
    return (
        '<section id="pass" aria-labelledby="titolo-pass">\n<div class="contenitore">\n<div class="testata">\n'
        + occhiello(P["occhiello"]) + f'\n<h2 id="titolo-pass">{esc(tipografia(P["h2"]))}</h2>\n<p class="lead">{esc(tipografia(P["lead"]))}</p>\n</div>\n'
        f'<div class="griglia-pass">\n{chr(10).join(carte)}\n</div>\n<ul class="punti pass-punti">{punti}</ul>\n'
        f'<p class="nota nota-sotto">{esc(tipografia(P["nota"]))} '
        f'<a href="{esc(ctx.rel(ctx.file_di("support.html")))}#come-funzionano-i-pass">{esc(P["link"])}</a>.</p>\n</div>\n</section>'
    )


def sezione_privacy(ctx: Ctx) -> str:
    P = ctx.T["home"]["privacy"]
    return (
        '<section id="privacy" class="senza-sopra" aria-labelledby="titolo-privacy">\n<div class="contenitore">\n<div class="fascia-privacy">\n<div>\n'
        + occhiello(P["occhiello"]) + f'\n<h2 id="titolo-privacy">{esc(tipografia(P["h2"]))}</h2>\n</div>\n<div>\n' + blocchi(ctx, P["testo"])
        + f'\n<p><a class="pulsante pulsante-secondario" href="{esc(ctx.rel(ctx.file_di("privacy.html")))}">{esc(P["link"])}</a></p>\n</div>\n</div>\n</div>\n</section>'
    )


def sezione_crediti(ctx: Ctx) -> str:
    C, L = ctx.T["home"]["crediti"], ctx.lingua
    righe = []
    for f in ctx.dati["foto"]:
        lic = esc(licenza_visibile(ctx, f))
        if f["licenza_url"]:
            lic = f'<a href="{esc(f["licenza_url"])}">{lic}</a>'
        righe.append(f'<tr><td>{esc(tipografia(f["file_commons"]))}</td><td>{esc(tipografia(f["autore"]))}</td><td>{lic}</td>'
                     f'<td><a href="{esc(f["fonte_url"])}">{esc(C["fonte_link"])}</a></td></tr>')
    col = C["colonne"]
    return (
        '<section id="crediti" class="crediti" aria-labelledby="titolo-crediti">\n<div class="contenitore">\n'
        f'<h2 id="titolo-crediti">{esc(C["h2"])}</h2>\n<p>{esc(tipografia(C["foto"]))}</p>\n'
        f'<div class="scorri"><table class="tabella-crediti"><thead><tr><th scope="col">{esc(col["foto"])}</th><th scope="col">{esc(col["autore"])}</th>'
        f'<th scope="col">{esc(col["licenza"])}</th><th scope="col">{esc(col["fonte"])}</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>\n'
        f'<p>{inline(ctx, C["mappe"])}</p>\n<p>{inline(ctx, C["caratteri"])}</p>\n</div>\n</section>'
    )


def json_ld_home(ctx: Ctx) -> dict:
    H = ctx.T["home"]
    base = ctx.sito["base_url"]
    return {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": base + "#sito", "url": ctx.url(ctx.file_di("index.html")), "name": "ArcoTour", "inLanguage": ctx.lingua},
            {"@type": "MobileApplication", "name": "ArcoTour", "operatingSystem": "iOS 15 or later", "applicationCategory": "TravelApplication",
             "description": H["json_ld_descrizione"], "inLanguage": ["it", "en"], "url": ctx.url(ctx.file_di("index.html"))},
        ],
    }


def pagina_home(ctx: Ctx) -> str:
    H = ctx.T["home"]
    corpo = "\n".join([sezione_eroe(ctx), sezione_fatti(ctx), sezione_come(ctx), sezione_roma(ctx), sezione_audioguide(ctx),
                       sezione_mappe(ctx), sezione_pass(ctx), sezione_privacy(ctx), sezione_crediti(ctx)])
    return documento(ctx, titolo=H["titolo"], descrizione=H["descrizione"], corpo=corpo, json_ld=json_ld_home(ctx))


# ------------------------------------------------------------------------------------------------ assistenza
def banner_bozza(ctx: Ctx) -> str:
    if not ctx.bozza:
        return ""
    u = ctx.T["ui"]
    # nella pagina dell'informativa, se ci sono punti evidenziati, la legenda dice che cosa sono
    legenda = ""
    if ctx.pagina == "privacy.html" and "{!" in json.dumps(ctx.dati["informativa"]["sezioni"], ensure_ascii=False):
        legenda = " " + esc(u["legenda_da_confermare"])
    return f'<p class="bozza" role="note"><strong>{esc(u["bozza_titolo"])}</strong> {esc(tipografia(u["bozza_testo"]))}{legenda}</p>'


def pagina_supporto(ctx: Ctx) -> str:
    S = ctx.T["supporto"]
    indice = "".join(f'<li><a href="#{esc(g["id"])}">{esc(tipografia(g["titolo"]))}</a></li>' for g in S["gruppi"])
    gruppi = []
    for g in S["gruppi"]:
        domande = "".join(
            f'<details id="{esc(q["id"])}"><summary>{esc(tipografia(q["q"]))}</summary><div class="risposta">{blocchi(ctx, q["a"])}</div></details>'
            for q in g["domande"])
        gruppi.append(f'<div class="gruppo-faq" id="{esc(g["id"])}"><h2>{esc(tipografia(g["titolo"]))}</h2><div class="faq">{domande}</div></div>')
    corpo = (
        '<div class="contenitore pagina-testata">\n' + occhiello(S["occhiello"]) + f'\n<h1>{esc(tipografia(S["h1"]))}</h1>\n<p class="lead">{esc(tipografia(S["lead"]))}</p>\n</div>\n'
        '<div class="contenitore pagina-corpo">\n' + banner_bozza(ctx) + "\n"
        f'<div class="contatto"><h2>{esc(S["contatto"]["titolo"])}</h2>{blocchi(ctx, S["contatto"]["testo"])}</div>\n'
        f'<nav aria-label="{esc(S["indice"])}"><ul class="indice">{indice}</ul></nav>\n' + "\n".join(gruppi) + "\n</div>"
    )
    return documento(ctx, titolo=S["titolo"], descrizione=S["descrizione"], corpo=corpo, noindex=ctx.bozza)


# ------------------------------------------------------------------------------------------- privacy e condizioni
def sommario(ctx: Ctx, titolo: str, voci: list) -> str:
    li = "".join(f'<li><a href="#{esc(i)}">{esc(tipografia(t))}</a></li>' for i, t in voci)
    return f'<nav class="sommario" aria-labelledby="titolo-sommario"><h2 id="titolo-sommario">{esc(titolo)}</h2><ol>{li}</ol></nav>'


def pagina_privacy(ctx: Ctx) -> str:
    P, L = ctx.T["privacy"], ctx.lingua
    info = ctx.dati["informativa"]
    sez_app = [(s["id"], s["titolo"][L], s["testo"][L]) for s in info["sezioni"]]
    sito = P["sito"]
    tutte = sez_app + [(sito["id"], sito["titolo"], sito["testo"])]
    corpo_sez = []
    corpo_sez.append(f'<h2 class="parte-titolo">{esc(P["parte_app"])}</h2>')
    for i, t, x in sez_app:
        corpo_sez.append(f'<section class="prosa-sez" id="{esc(i)}"><h3>{esc(tipografia(t))}</h3>{blocchi(ctx, x)}</section>')
    corpo_sez.append(f'<h2 class="parte-titolo">{esc(P["parte_sito"])}</h2>')
    corpo_sez.append(f'<section class="prosa-sez" id="{esc(sito["id"])}"><h3>{esc(tipografia(sito["titolo"]))}</h3>{blocchi(ctx, sito["testo"])}</section>')
    corpo = (
        '<div class="contenitore pagina-testata">\n' + occhiello(P["occhiello"]) + f'\n<h1>{esc(tipografia(P["h1"]))}</h1>\n'
        f'<p class="lead">{esc(tipografia(P["sottotitolo"]))}. {esc(P["aggiornata_etichetta"])}{esc(info["aggiornata"][L])}.</p>\n</div>\n'
        '<div class="contenitore pagina-corpo">\n' + banner_bozza(ctx) + "\n"
        + sommario(ctx, P["indice"], [(i, t) for i, t, _ in tutte]) + '\n<div class="prosa">\n' + "\n".join(corpo_sez) + "\n</div>\n</div>"
    )
    return documento(ctx, titolo=P["titolo"], descrizione=P["descrizione"], corpo=corpo, noindex=ctx.bozza)


def pagina_condizioni(ctx: Ctx) -> str:
    C = ctx.T["condizioni"]
    sez = "".join(f'<section id="{esc(s["id"])}"><h2>{esc(tipografia(s["titolo"]))}</h2>{blocchi(ctx, s["testo"])}</section>' for s in C["sezioni"])
    corpo = (
        '<div class="contenitore pagina-testata">\n' + occhiello(C["occhiello"]) + f'\n<h1>{esc(tipografia(C["h1"]))}</h1>\n'
        f'<p class="lead">{esc(tipografia(C["sottotitolo"]))}. {inline(ctx, C["aggiornate"])}</p>\n</div>\n'
        '<div class="contenitore pagina-corpo">\n' + banner_bozza(ctx) + "\n"
        + sommario(ctx, ctx.T["privacy"]["indice"], [(s["id"], s["titolo"]) for s in C["sezioni"]]) + f'\n<div class="prosa">{sez}</div>\n</div>'
    )
    return documento(ctx, titolo=C["titolo"], descrizione=C["descrizione"], corpo=corpo, noindex=ctx.bozza)


# --------------------------------------------------------------------------------------------------- 404
def pagina_404(dati: dict) -> str:
    """La 404 sta nella radice e può essere aperta da qualsiasi percorso sotto il sito: usa <base> con il percorso vero del sito."""
    base_url = dati["sito"]["base_url"]
    percorso_base = "/" + base_url.split("://", 1)[1].split("/", 1)[1]  # es. /arcotour-site/
    ctx = Ctx(dati, "it", "404.html")
    it, en = TESTI["it"]["pagina404"], TESTI["en"]["pagina404"]
    corpo = (
        '<section class="vuota"><div class="contenitore">\n'
        f'<h1>{esc(it["h1"])}</h1>\n<p class="lead">{esc(it["testo"])}</p>\n<p><a class="pulsante pulsante-primario" href="index.html">{esc(it["link"])}</a></p>\n'
        f'<p class="lead lead-en" lang="en">{esc(en["testo"])}</p>\n<p lang="en"><a class="pulsante pulsante-secondario" href="en/index.html">{esc(en["link"])}</a></p>\n'
        '</div></section>')
    return documento(ctx, titolo=it["titolo"], descrizione=it["testo"], corpo=corpo, noindex=True, base_href=percorso_base, alternate=False)


# ------------------------------------------------------------------------------------- sitemap e robots
def sitemap(dati: dict) -> str:
    sito = dati["sito"]
    righe = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    bozza = bozza_legale(sito, dati["informativa"])
    for pagina in PAGINE:
        if bozza and pagina in PAGINE_LEGALI:
            continue  # le pagine «in revisione» non vanno nella mappa del sito
        for l in LINGUE:
            ctx = Ctx(dati, l, pagina)
            righe.append("<url>")
            righe.append(f"<loc>{esc(ctx.url(ctx.file))}</loc>")
            righe.append(f"<lastmod>{esc(sito['aggiornato'])}</lastmod>")
            for l2 in LINGUE:
                righe.append(f'<xhtml:link rel="alternate" hreflang="{l2}" href="{esc(ctx.url(ctx.file_di(pagina, l2)))}"/>')
            righe.append(f'<xhtml:link rel="alternate" hreflang="x-default" href="{esc(ctx.url(ctx.file_di(pagina, "it")))}"/>')
            righe.append("</url>")
    righe.append("</urlset>")
    return "\n".join(righe) + "\n"


def robots(dati: dict) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {dati['sito']['base_url']}sitemap.xml\n"


# -------------------------------------------------------------------------------------------- tutto insieme
COSTRUTTORI = {"index.html": pagina_home, "support.html": pagina_supporto, "privacy.html": pagina_privacy, "terms.html": pagina_condizioni}


def costruisci(dati: dict) -> dict:
    """Restituisce {percorso dalla radice: contenuto} di tutti i file generati."""
    out = {}
    for lingua in LINGUE:
        for pagina in PAGINE:
            ctx = Ctx(dati, lingua, pagina)
            out[ctx.file] = COSTRUTTORI[pagina](ctx)
    out["404.html"] = pagina_404(dati)
    out["sitemap.xml"] = sitemap(dati)
    out["robots.txt"] = robots(dati)
    return out
