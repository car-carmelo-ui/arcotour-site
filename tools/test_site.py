#!/usr/bin/env python3
"""Prove del sito: python3 tools/test_site.py   (solo libreria standard; non tocca mai i file veri del sito).

Tre famiglie di prove, tutte su COPIE in cartelle temporanee:
  1. il generatore: collegamenti relativi, stato «in revisione», stato «app disponibile», nessun dato inventato;
  2. il controllo (tools/check_site.py): gli si inserisce di proposito ogni errore e si verifica che lo veda
     (un controllo che non sa trovare gli errori è peggio di nessun controllo);
  3. il sito servito sotto /arcotour-site/ come fa GitHub Pages: ogni pagina, immagine, carattere e ancora si raggiunge davvero.
"""
import http.server
import json
import re
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent
sys.path.insert(0, str(QUI))

import check_site  # noqa: E402
import sitegen  # noqa: E402

COPIA = ("content", "assets", "index.html", "support.html", "privacy.html", "terms.html", "404.html", "en",
         "sitemap.xml", "robots.txt", "favicon.ico", ".nojekyll")


def copia_del_sito(destinazione: Path) -> Path:
    destinazione.mkdir(parents=True, exist_ok=True)
    for nome in COPIA:
        origine = RADICE / nome
        if origine.is_dir():
            shutil.copytree(origine, destinazione / nome, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(origine, destinazione / nome)
    return destinazione


def leggi(radice: Path, rel: str) -> str:
    return (radice / rel).read_text(encoding="utf-8")


def scrivi(radice: Path, rel: str, testo: str):
    (radice / rel).write_text(testo, encoding="utf-8")


def sostituisci(radice: Path, rel: str, vecchio: str, nuovo: str, volte: int = 1):
    s = leggi(radice, rel)
    assert s.count(vecchio) >= 1, f"{rel}: non trovo «{vecchio[:70]}»"
    scrivi(radice, rel, s.replace(vecchio, nuovo, volte) if volte else s.replace(vecchio, nuovo))


def modifica_dati(radice: Path, funzione):
    d = json.loads(leggi(radice, "content/site.json"))
    funzione(d)
    scrivi(radice, "content/site.json", json.dumps(d, ensure_ascii=False, indent=2))


def ricostruisci(radice: Path):
    dati = sitegen.carica_dati(radice)
    for nome, testo in sitegen.costruisci(dati).items():
        (radice / nome).parent.mkdir(parents=True, exist_ok=True)
        (radice / nome).write_text(testo, encoding="utf-8")


def dati_veri(radice: Path):
    """Dati completi e approvati (per provare lo stato «pronto»): sono INVENTATI e vivono solo in una cartella temporanea."""
    def f(d):
        d["venditore"] = {"nome": "Ditta di Prova", "indirizzo": "Via di Prova 1, 00100 Roma, Italia", "email": "assistenza@esempio.test", "partita_iva": ""}
        d["revisione_legale"] = "approvata"
    modifica_dati(radice, f)
    ricostruisci(radice)


class ConCopia(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.r = copia_del_sito(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def esiti(self, rilascio=False):
        e, esterni = check_site.controlla(self.r, rilascio)
        return e, esterni

    def assertTrova(self, frammento, rilascio=False, in_file=None):
        e, _ = self.esiti(rilascio)
        trovati = [(f, m) for f, m in e.errori if frammento.lower() in f"{f}: {m}".lower() and (in_file is None or f == in_file)]
        self.assertTrue(trovati, f"il controllo NON ha visto l'errore «{frammento}». Errori trovati: {e.errori[:6]}")

    def assertPulito(self, rilascio=False):
        e, _ = self.esiti(rilascio)
        self.assertEqual(e.errori, [], f"errori inattesi: {e.errori[:8]}")


# ============================================================================================ 1. il sito vero
class SitoVero(unittest.TestCase):
    def test_il_sito_nel_repository_e_in_regola(self):
        e, _ = check_site.controlla(RADICE)
        self.assertEqual(e.errori, [], e.errori[:10])

    def test_il_sito_e_aggiornato_rispetto_al_generatore(self):
        dati = sitegen.carica_dati(RADICE)
        for nome, testo in sitegen.costruisci(dati).items():
            self.assertEqual((RADICE / nome).read_text(encoding="utf-8"), testo, f"{nome} non è aggiornato: python3 tools/build_site.py")

    def test_la_costruzione_e_sempre_uguale(self):
        dati = sitegen.carica_dati(RADICE)
        self.assertEqual(sitegen.costruisci(dati), sitegen.costruisci(dati))

    def test_oggi_il_cancello_di_pubblicazione_e_chiuso(self):
        """Finché mancano i dati di chi pubblica NON si può dire «pronto»: è voluto."""
        e, _ = check_site.controlla(RADICE, rilascio=True)
        messaggi = " ".join(m for _, m in e.errori)
        self.assertIn("manca nome o ragione sociale", messaggi)
        self.assertIn("manca indirizzo o sede", messaggi)
        self.assertIn("manca email di assistenza", messaggi)
        self.assertIn("revisione_legale", messaggi)

    def test_nessun_dato_personale_inventato_o_vero(self):
        for f in RADICE.rglob("*"):
            rel = f.relative_to(RADICE).as_posix()
            if not f.is_file() or rel.startswith(".git/") or "__pycache__" in rel or f.suffix not in check_site.ESTENSIONI_TESTO or rel == "tools/test_site.py":
                continue
            testo = f.read_text(encoding="utf-8")
            for m in check_site.EMAIL.finditer(testo):
                if m.group(0).split("@")[0].lower() != "noreply":
                    self.fail(f"{rel}: indirizzo email «{m.group(0)}» in un file pubblico")

    def test_i_segnaposto_non_compaiono_mai_scritti_grezzi_nelle_pagine(self):
        for f in check_site.Sito(RADICE).pagine:
            self.assertNotIn("DA_COMPLETARE", leggi(RADICE, f), f)

    def test_prezzi_e_durate_dei_pass(self):
        it = check_site.leggi(leggi(RADICE, "index.html")).testo_visibile
        en = check_site.leggi(leggi(RADICE, "en/index.html")).testo_visibile
        for t in ("Roma 24 ore", "€2,99", "Roma 72 ore", "€4,99", "Roma Completa", "€7,99", "10 giorni (240 ore)"):
            self.assertIn(t, it)
        for t in ("Rome 24 hours", "€2.99", "Rome 72 hours", "€4.99", "Rome Complete", "€7.99", "10 days (240 hours)"):
            self.assertIn(t, en)

    def test_le_pagine_legali_oggi_sono_in_revisione_e_non_indicizzabili(self):
        sito = check_site.Sito(RADICE)
        self.assertTrue(sito.bozza)
        for pagina in check_site.PAGINE_LEGALI:
            for f in (pagina, "en/" + pagina):
                p = sito.pagine[f]
                self.assertIn("noindex", p.meta_contenuto("robots"), f)
                self.assertIn("bozza", p.classi, f)
        sitemap = leggi(RADICE, "sitemap.xml")
        for pagina in check_site.PAGINE_LEGALI:
            self.assertNotIn(pagina, sitemap)


# ============================================================================================ 2. il generatore
class Generatore(ConCopia):
    def test_percorsi_relativi_in_ogni_cartella(self):
        c = sitegen.Ctx(sitegen.carica_dati(self.r), "it", "support.html")
        self.assertEqual(c.rel("assets/css/site.css"), "assets/css/site.css")
        self.assertEqual(c.file_di("privacy.html"), "privacy.html")
        c_en = sitegen.Ctx(sitegen.carica_dati(self.r), "en", "support.html")
        self.assertEqual(c_en.rel("assets/css/site.css"), "../assets/css/site.css")
        self.assertEqual(c_en.rel("index.html"), "../index.html")
        self.assertEqual(c_en.rel("en/privacy.html"), "privacy.html")
        self.assertEqual(sitegen.risolvi(c_en, "@privacy.html#sito-web"), "privacy.html#sito-web")
        self.assertEqual(sitegen.risolvi(c, "@privacy.html#sito-web"), "privacy.html#sito-web")
        self.assertEqual(sitegen.risolvi(c_en, "@@assets/img/x.png"), "../assets/img/x.png")

    def test_indirizzi_completi_solo_dove_servono(self):
        c = sitegen.Ctx(sitegen.carica_dati(self.r), "en", "index.html")
        self.assertEqual(c.url("en/index.html"), "https://car-carmelo-ui.github.io/arcotour-site/en/")
        self.assertEqual(c.url("index.html"), "https://car-carmelo-ui.github.io/arcotour-site/")
        self.assertEqual(c.url("support.html"), "https://car-carmelo-ui.github.io/arcotour-site/support.html")

    def test_apostrofo_tipografico_solo_nel_testo(self):
        self.assertEqual(sitegen.tipografia("l'app e de' Fiori"), "l’app e de’ Fiori")
        self.assertEqual(sitegen.tipografia("«Inizia il tour»"), "«Inizia il tour»")

    def test_html_degli_input_viene_neutralizzato(self):
        def f(d):
            d["venditore"]["nome"] = "<script>alert(1)</script> & Figli"
        modifica_dati(self.r, f)
        ricostruisci(self.r)
        for pagina in ("privacy.html", "terms.html"):
            testo = leggi(self.r, pagina)
            self.assertNotIn("<script>alert", testo)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt; &amp; Figli", testo)

    def test_dati_completi_e_approvati_tolgono_avvisi_e_noindex_e_riempiono_la_sitemap(self):
        dati_veri(self.r)
        self.assertPulito(rilascio=True)
        for pagina in check_site.PAGINE_LEGALI:
            testo = leggi(self.r, pagina)
            self.assertNotIn("noindex", testo)
            self.assertNotIn('class="bozza"', testo)
            self.assertNotIn('class="segnaposto"', testo)  # (la parola compare anche nel testo: i «segnaposto» della mappa)
            self.assertIn("mailto:assistenza@esempio.test", testo)
            self.assertIn(pagina, leggi(self.r, "sitemap.xml"))
        self.assertIn("en/terms.html", leggi(self.r, "sitemap.xml"))
        for pagina in ("privacy.html", "terms.html", "en/privacy.html", "en/terms.html"):
            self.assertIn("Ditta di Prova", leggi(self.r, pagina), pagina)
            self.assertIn("Via di Prova 1, 00100 Roma, Italia", leggi(self.r, pagina), pagina)

    def test_revisione_legale_da_fare_tiene_il_sito_in_revisione_anche_con_i_dati(self):
        dati_veri(self.r)
        modifica_dati(self.r, lambda d: d.update(revisione_legale="da_fare"))
        ricostruisci(self.r)
        self.assertIn("noindex", leggi(self.r, "terms.html"))
        self.assertTrova("revisione_legale", rilascio=True)

    def test_app_disponibile_ha_un_collegamento_all_app_store(self):
        def f(d):
            d["app"] = {"stato": "disponibile", "app_store_url": "https://apps.apple.com/it/app/arcotour/id1234567890"}
        modifica_dati(self.r, f)
        ricostruisci(self.r)
        self.assertIn('href="https://apps.apple.com/it/app/arcotour/id1234567890"', leggi(self.r, "index.html"))
        self.assertNotIn("Prossimamente", leggi(self.r, "index.html"))
        self.assertPulito()

    def test_app_disponibile_senza_indirizzo_non_si_costruisce(self):
        modifica_dati(self.r, lambda d: d.update(app={"stato": "disponibile", "app_store_url": ""}))
        with self.assertRaises(SystemExit):
            ricostruisci(self.r)

    def test_la_404_funziona_da_qualsiasi_cartella(self):
        testo = leggi(self.r, "404.html")
        self.assertIn('<base href="/arcotour-site/">', testo)
        self.assertIn("noindex", testo)


# ============================================================================================ 3. il controllo trova gli errori
class ControlloTrovaGliErrori(ConCopia):
    def test_base_pulita(self):
        self.assertPulito()

    # --- collegamenti e percorsi
    def test_collegamento_a_pagina_inesistente(self):
        sostituisci(self.r, "index.html", 'href="support.html"', 'href="assistenza.html"')
        self.assertTrova("assistenza.html")

    def test_ancora_inesistente(self):
        sostituisci(self.r, "index.html", 'href="support.html"', 'href="support.html#non-esiste"')
        self.assertTrova("non c'è l'ancora #non-esiste")

    def test_ancora_nella_stessa_pagina_inesistente(self):
        sostituisci(self.r, "index.html", 'href="#roma"', 'href="#nessun-posto"')
        self.assertTrova("#nessun-posto")

    def test_percorso_che_parte_da_slash(self):
        sostituisci(self.r, "index.html", 'href="assets/css/site.css"', 'href="/assets/css/site.css"')
        self.assertTrova("parte da «/»")

    def test_percorso_sbagliato_nella_pagina_inglese(self):
        sostituisci(self.r, "en/index.html", 'href="../assets/css/site.css"', 'href="assets/css/site.css"')
        self.assertTrova("non esiste", in_file="en/index.html")

    def test_immagine_mancante(self):
        (self.r / "assets/img/icona-96.png").unlink()
        self.assertTrova("icona-96.png")

    def test_srcset_con_file_mancante(self):
        sostituisci(self.r, "index.html", "colosseo-640.jpg 640w", "colosseo-640x.jpg 640w")
        self.assertTrova("colosseo-640x.jpg")

    def test_collegamento_http_non_protetto(self):
        sostituisci(self.r, "privacy.html", 'href="https://docs.github.com/en/site-policy', 'href="http://docs.github.com/en/site-policy')
        self.assertTrova("http://")

    def test_collegamento_senza_protocollo(self):
        sostituisci(self.r, "privacy.html", 'href="https://docs.github.com/en/site-policy', 'href="//docs.github.com/en/site-policy')
        self.assertTrova("senza protocollo")

    def test_target_blank_senza_noopener(self):
        sostituisci(self.r, "index.html", '<a class="salta" href="#contenuto">', '<a class="salta" target="_blank" href="#contenuto">')
        self.assertTrova("noopener")

    def test_collegamento_vuoto_o_senza_nome(self):
        sostituisci(self.r, "index.html", '<footer class="piede">', '<footer class="piede"><a href="privacy.html"></a>')
        self.assertTrova("senza nome")

    def test_404_senza_base(self):
        sostituisci(self.r, "404.html", '<base href="/arcotour-site/">', "")
        self.assertTrova("<base")

    # --- risorse esterne e privacy
    def test_script_esterno(self):
        sostituisci(self.r, "index.html", '<script src="assets/js/site.js" defer></script>', '<script src="https://cdn.esempio.test/x.js" defer></script>')
        self.assertTrova("non carica nulla da altri siti")

    def test_carattere_da_google(self):
        sostituisci(self.r, "index.html", '<link rel="stylesheet" href="assets/css/site.css">',
                    '<link rel="stylesheet" href="assets/css/site.css"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">')
        self.assertTrova("non carica nulla da altri siti")

    def test_css_che_carica_da_fuori(self):
        sostituisci(self.r, "assets/css/site.css", "/* ----", '@import url("https://esempio.test/a.css");\n/* ----')
        self.assertTrova("@import")

    def test_css_url_inesistente(self):
        sostituisci(self.r, "assets/css/site.css", "../fonts/inter-regular.woff2", "../fonts/inter-regolare.woff2")
        self.assertTrova("inter-regolare.woff2")

    def test_analytics(self):
        sostituisci(self.r, "index.html", "</head>", '<script async src="assets/js/site.js"></script><!-- googletagmanager --></head>')
        self.assertTrova("tracciamento")

    def test_js_che_salva_dati(self):
        (self.r / "assets/js/site.js").write_text("document.cookie='a=1';", encoding="utf-8")
        self.assertTrova("document.cookie")

    def test_js_che_fa_richieste(self):
        (self.r / "assets/js/site.js").write_text("fetch('x');", encoding="utf-8")
        self.assertTrova("fetch(")

    def test_modulo_nella_pagina(self):
        sostituisci(self.r, "support.html", '<footer class="piede">', '<form><input name="m"></form><footer class="piede">')
        self.assertTrova("<form> non ammesso")

    def test_iframe(self):
        sostituisci(self.r, "index.html", '<footer class="piede">', '<iframe src="privacy.html"></iframe><footer class="piede">')
        self.assertTrova("<iframe> non ammesso")

    def test_email_personale_in_un_file(self):
        (self.r / "content" / "note.json").write_text('{"x": "scrivi a mario.rossi@posta.test"}', encoding="utf-8")
        self.assertTrova("indirizzo email")

    def test_email_personale_in_una_pagina(self):
        sostituisci(self.r, "privacy.html", "<footer", '<p>mario.rossi@posta.test</p><footer')
        self.assertTrova("mario.rossi@posta.test")

    def test_stile_scritto_dentro_la_pagina(self):
        sostituisci(self.r, "index.html", '<footer class="piede">', '<footer class="piede" style="color:red">')
        self.assertTrova("style=")

    def test_script_in_pagina_diverso_da_quello_ammesso(self):
        sostituisci(self.r, "index.html", "</body>", "<script>alert(1)</script></body>")
        self.assertTrova("script scritto dentro la pagina")

    def test_evento_scritto_dentro_la_pagina(self):
        sostituisci(self.r, "index.html", '<footer class="piede">', '<footer class="piede" onclick="x()">')
        self.assertTrova("gestore di evento")

    # --- SEO
    def test_manca_il_titolo(self):
        sostituisci(self.r, "privacy.html", "<title>", "<titolo>")
        sostituisci(self.r, "privacy.html", "</title>", "</titolo>")
        self.assertTrova("manca il <title>")

    def test_titolo_ripetuto(self):
        t = check_site.leggi(leggi(self.r, "index.html")).titolo
        sostituisci(self.r, "support.html", f"<title>{check_site.leggi(leggi(self.r, 'support.html')).titolo}</title>", f"<title>{t}</title>")
        self.assertTrova("identico a quello di")

    def test_manca_la_descrizione(self):
        sostituisci(self.r, "terms.html", '<meta name="description"', '<meta name="descrizione"')
        self.assertTrova("meta description")

    def test_canonical_sbagliato(self):
        sostituisci(self.r, "index.html", '<link rel="canonical" href="https://car-carmelo-ui.github.io/arcotour-site/">',
                    '<link rel="canonical" href="https://car-carmelo-ui.github.io/altro-sito/">')
        self.assertTrova("canonical")

    def test_hreflang_mancante(self):
        sostituisci(self.r, "en/index.html", '<link rel="alternate" hreflang="it" href="https://car-carmelo-ui.github.io/arcotour-site/">', "")
        self.assertTrova("hreflang")

    def test_lingua_della_pagina_sbagliata(self):
        sostituisci(self.r, "en/support.html", '<html lang="en">', '<html lang="it">')
        self.assertTrova("<html lang>")

    def test_manca_open_graph(self):
        sostituisci(self.r, "index.html", '<meta property="og:image" content="https://car-carmelo-ui.github.io/arcotour-site/assets/img/anteprima-it.png">', "")
        self.assertTrova("og:image")

    def test_anteprima_social_di_misura_sbagliata(self):
        shutil.copy(self.r / "assets/img/icona-512.png", self.r / "assets/img/anteprima-it.png")
        self.assertTrova("1200×630")

    def test_pagina_legale_in_revisione_senza_noindex(self):
        sostituisci(self.r, "terms.html", '<meta name="robots" content="noindex, follow">', "")
        self.assertTrova("noindex")

    def test_pagina_legale_pubblicabile_con_noindex(self):
        dati_veri(self.r)
        sostituisci(self.r, "terms.html", "<head>", '<head><meta name="robots" content="noindex">')
        self.assertTrova("noindex")

    def test_sitemap_con_pagina_inesistente(self):
        sostituisci(self.r, "sitemap.xml", "</urlset>",
                    "<url><loc>https://car-carmelo-ui.github.io/arcotour-site/fantasma.html</loc><lastmod>2026-10-12</lastmod></url></urlset>")
        self.assertTrova("fantasma.html")

    def test_sitemap_con_pagina_in_revisione(self):
        sostituisci(self.r, "sitemap.xml", "</urlset>",
                    "<url><loc>https://car-carmelo-ui.github.io/arcotour-site/terms.html</loc><lastmod>2026-10-12</lastmod></url></urlset>")
        self.assertTrova("non deve esserci")

    def test_sitemap_rotta(self):
        scrivi(self.r, "sitemap.xml", "<urlset>")
        self.assertTrova("XML")

    def test_robots_senza_sitemap(self):
        scrivi(self.r, "robots.txt", "User-agent: *\nAllow: /\n")
        self.assertTrova("Sitemap")

    def test_robots_che_chiude_tutto(self):
        scrivi(self.r, "robots.txt", f"User-agent: *\nDisallow: /\n\nSitemap: {check_site.Sito(self.r).base_url}sitemap.xml\n")
        self.assertTrova("Disallow: /")

    def test_manca_nojekyll(self):
        (self.r / ".nojekyll").unlink()
        self.assertTrova(".nojekyll")

    def test_manca_la_404(self):
        (self.r / "404.html").unlink()
        self.assertTrova("404.html")

    # --- accessibilità e struttura
    def test_due_h1(self):
        s2 = re.sub(r'<div class="contatto"><h2>(.*?)</h2>', r'<div class="contatto"><h1>\1</h1>', leggi(self.r, "support.html"))
        scrivi(self.r, "support.html", s2)
        self.assertTrova("un solo <h1>")

    def test_salto_di_livello_nei_titoli(self):
        sostituisci(self.r, "index.html", '<h3 class="sottotitolo-sezione">', '<h5 class="sottotitolo-sezione">')
        sostituisci(self.r, "index.html", "</h3>\n<ol class=\"elenco-percorsi\">", "</h5>\n<ol class=\"elenco-percorsi\">")
        self.assertTrova("salto di livello")

    def test_immagine_senza_alt(self):
        sostituisci(self.r, "index.html", 'width="40" height="40" alt=""', 'width="40" height="40"', 1)
        self.assertTrova("senza attributo alt")

    def test_foto_senza_testo_alternativo(self):
        sostituisci(self.r, "index.html", 'alt="Il Colosseo visto dall’esterno."', 'alt=""')
        self.assertTrova("foto senza testo alternativo")

    def test_immagine_senza_dimensioni(self):
        sostituisci(self.r, "index.html", 'width="1280" height="897" alt="Il Colosseo', 'alt="Il Colosseo')
        self.assertTrova("senza width/height")

    def test_foto_senza_credito(self):
        s = leggi(self.r, "index.html")
        i = s.index('<figcaption class="credito">')
        j = s.index("</figcaption>", i) + len("</figcaption>")
        scrivi(self.r, "index.html", s[:i] + s[j:])
        self.assertTrova("senza il suo credito")

    def test_id_ripetuti(self):
        sostituisci(self.r, "index.html", 'id="titolo-roma"', 'id="titolo-come"')
        self.assertTrova("id ripetuti")

    def test_riferimento_aria_a_id_inesistente(self):
        sostituisci(self.r, "index.html", 'aria-controls="menu-principale"', 'aria-controls="menu-fantasma"')
        self.assertTrova("menu-fantasma")

    def test_pulsante_senza_nome(self):
        sostituisci(self.r, "index.html", '>Menu</button>', "></button>")
        self.assertTrova("pulsante senza nome")

    def test_pulsante_senza_aria_expanded(self):
        sostituisci(self.r, "index.html", ' aria-expanded="false"', "")
        self.assertTrova("aria-expanded")

    def test_nav_senza_nome(self):
        sostituisci(self.r, "index.html", '<nav aria-label="Il sito">', "<nav>")
        self.assertTrova("aria-label")

    def test_manca_il_collegamento_vai_al_contenuto(self):
        sostituisci(self.r, "index.html", '<a class="salta" href="#contenuto">Vai al contenuto</a>', "")
        self.assertTrova("Vai al contenuto")

    def test_tabella_senza_scope(self):
        sostituisci(self.r, "index.html", '<th scope="col">Foto</th>', "<th>Foto</th>")
        self.assertTrova("senza scope")

    def test_html_non_chiuso(self):
        sostituisci(self.r, "privacy.html", '<main id="contenuto">', '<main id="contenuto"><div>')
        self.assertTrova("non ben formato")

    def test_senza_doctype(self):
        sostituisci(self.r, "index.html", "<!doctype html>", "")
        self.assertTrova("doctype")

    def test_viewport_che_blocca_lo_zoom(self):
        sostituisci(self.r, "index.html", "initial-scale=1", "initial-scale=1, maximum-scale=1")
        self.assertTrova("ingrandimento")

    def test_css_senza_focus(self):
        s = leggi(self.r, "assets/css/site.css").replace(":focus-visible", ":hover-visible")
        scrivi(self.r, "assets/css/site.css", s)
        self.assertTrova("focus")

    def test_css_senza_movimento_ridotto(self):
        s = leggi(self.r, "assets/css/site.css").replace("prefers-reduced-motion", "prefers-qualcosa")
        scrivi(self.r, "assets/css/site.css", s)
        self.assertTrova("reduced-motion")

    def test_css_che_toglie_il_focus(self):
        sostituisci(self.r, "assets/css/site.css", "a { color: var(--terracotta-scura);", "a:hover { outline: none; }\na { color: var(--terracotta-scura);")
        self.assertTrova("outline")

    def test_contrasto_troppo_basso(self):
        sostituisci(self.r, "assets/css/site.css", "--secondario: #5A5048;", "--secondario: #A09A92;")
        self.assertTrova("contrasto")

    def test_classe_con_errore_di_battitura(self):
        sostituisci(self.r, "index.html", 'class="pulsanti"', 'class="pulsante-inesistente"')
        self.assertTrova("assenti dal foglio di stile")

    def test_font_face_senza_font_display(self):
        s = leggi(self.r, "assets/css/site.css").replace(" font-display: swap;", "", 1)
        scrivi(self.r, "assets/css/site.css", s)
        self.assertTrova("font-display")

    def test_manca_un_file_necessario(self):
        (self.r / "assets/fonts/OFL-Inter.txt").unlink()
        self.assertTrova("OFL-Inter.txt")

    # --- promesse sui pass
    def test_pass_descritto_come_permanente(self):
        sostituisci(self.r, "index.html", "<footer", "<p>Roma Completa è un pass permanente.</p><footer")
        self.assertTrova("permanente")

    def test_pass_descritto_come_illimitato_in_inglese(self):
        sostituisci(self.r, "en/index.html", "<footer", "<p>Rome Complete gives unlimited access.</p><footer")
        self.assertTrova("unlimited")

    def test_pass_descritto_come_abbonamento(self):
        sostituisci(self.r, "support.html", "<footer", "<p>Il pass è un abbonamento.</p><footer")
        self.assertTrova("abbonament")

    def test_rinnovo_automatico_promesso(self):
        sostituisci(self.r, "terms.html", "<footer", "<p>Il pass si rinnova ogni mese.</p><footer")
        self.assertTrova("rinnov")

    def test_la_negazione_e_ammessa(self):
        sostituisci(self.r, "terms.html", "<footer", "<p>Il pass non è un abbonamento e non si rinnova.</p><footer")
        self.assertPulito()

    def test_prezzo_diverso(self):
        sostituisci(self.r, "index.html", "€4,99", "€5,99", 0)
        self.assertTrova("prezzo «€5,99»")

    def test_durata_diversa(self):
        sostituisci(self.r, "index.html", "<footer", "<p>Il pass dura 48 ore.</p><footer")
        self.assertTrova("48 ore")

    def test_pass_completo_senza_durata(self):
        s = leggi(self.r, "support.html")
        scrivi(self.r, "support.html", s.replace("10 giorni (240 ore)", "alcuni giorni").replace("240", "x"))
        self.assertTrova("240")

    def test_manca_un_pass_nella_home(self):
        sostituisci(self.r, "index.html", "Roma 72 ore", "Roma tre giorni", 0)
        self.assertTrova("Roma 72 ore")

    def test_collegamento_a_app_store_con_app_non_pubblicata(self):
        sostituisci(self.r, "index.html", "<footer", '<a href="https://apps.apple.com/it/app/arcotour/id1">App</a><footer')
        self.assertTrova("prossimamente")

    def test_segnaposto_grezzo_visibile(self):
        sostituisci(self.r, "index.html", "<footer", "<p>DA_COMPLETARE:cosa</p><footer")
        self.assertTrova("segnaposto grezzo")

    # --- foto e crediti
    def test_foto_di_altro_sito_che_non_e_commons(self):
        d = json.loads(leggi(self.r, "content/foto.json"))
        d[0]["fonte_url"] = "https://unsplash.com/photos/abc"
        scrivi(self.r, "content/foto.json", json.dumps(d, ensure_ascii=False))
        self.assertTrova("Wikimedia Commons")

    def test_foto_con_licenza_non_commerciale(self):
        d = json.loads(leggi(self.r, "content/foto.json"))
        d[0]["licenza"] = "CC BY-NC 4.0"
        scrivi(self.r, "content/foto.json", json.dumps(d, ensure_ascii=False))
        self.assertTrova("non ammessa")

    def test_foto_senza_autore(self):
        d = json.loads(leggi(self.r, "content/foto.json"))
        d[1]["autore"] = ""
        scrivi(self.r, "content/foto.json", json.dumps(d, ensure_ascii=False))
        self.assertTrova("manca l'autore")

    def test_foto_senza_scheda(self):
        shutil.copy(self.r / "assets/img/foto/colosseo-640.jpg", self.r / "assets/img/foto/sconosciuta-640.jpg")
        self.assertTrova("senza scheda")

    def test_indirizzo_commons_non_corrisponde_al_file(self):
        d = json.loads(leggi(self.r, "content/foto.json"))
        d[0]["fonte_url"] = "https://commons.wikimedia.org/wiki/File:Altro.jpg"
        scrivi(self.r, "content/foto.json", json.dumps(d, ensure_ascii=False))
        self.assertTrova("non corrisponde")

    def test_credito_senza_collegamento_alla_licenza(self):
        s = leggi(self.r, "index.html")
        scrivi(self.r, "index.html", s.replace('<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>', "CC BY-SA 4.0"))
        self.assertTrova("collegamento alla licenza")

    # --- italiano e inglese
    def test_inglese_con_una_sezione_in_meno(self):
        sostituisci(self.r, "en/support.html", '<details id="lingua">', '<details id="language">')
        self.assertTrova("id diversi")

    def test_collegamento_interno_diverso_nelle_due_lingue(self):
        sostituisci(self.r, "en/index.html", 'href="support.html"', 'href="terms.html"')
        self.assertTrova("collegamenti interni non sono gli stessi")

    def test_selettore_della_lingua_che_porta_alla_pagina_sbagliata(self):
        sostituisci(self.r, "index.html", 'hreflang="en" aria-label="English" href="en/index.html"', 'hreflang="en" aria-label="English" href="en/support.html"')
        self.assertTrova("selettore della lingua")

    def test_manca_una_lingua(self):
        shutil.rmtree(self.r / "en")
        self.assertTrova("manca")

    # --- cancello della pubblicazione
    def test_il_cancello_si_apre_solo_con_tutto(self):
        dati_veri(self.r)
        self.assertPulito(rilascio=True)

    def test_il_cancello_vede_il_segnaposto_dell_email(self):
        dati_veri(self.r)
        modifica_dati(self.r, lambda d: d["venditore"].update(email="DA_COMPLETARE:email"))
        ricostruisci(self.r)
        self.assertTrova("manca email di assistenza", rilascio=True)

    def test_il_cancello_vede_l_email_non_valida(self):
        dati_veri(self.r)
        modifica_dati(self.r, lambda d: d["venditore"].update(email="non-una-email"))
        ricostruisci(self.r)
        self.assertTrova("non è un indirizzo email", rilascio=True)

    def test_il_cancello_vede_pagine_ancora_in_revisione(self):
        self.assertTrova("segnaposto", rilascio=True)
        self.assertTrova("revisione", rilascio=True)

    def test_dati_completi_ma_pagina_vecchia(self):
        dati_veri(self.r)
        sostituisci(self.r, "terms.html", '<main id="contenuto">', '<main id="contenuto"><p class="bozza">Versione in revisione.</p>')
        self.assertTrova("avvisi o segnaposto")


# ============================================================================================ 4. servito come GitHub Pages
class Servito(unittest.TestCase):
    """Il sito servito sotto /arcotour-site/ (come https://car-carmelo-ui.github.io/arcotour-site/): ogni risorsa si raggiunge."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls._tmp.name)
        copia_del_sito(cls.base / "arcotour-site")
        radice = str(cls.base)

        class Gestore(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **k):
                super().__init__(*a, directory=radice, **k)

            def log_message(self, *a):
                pass

            def send_error(self, code, message=None, explain=None):
                if code == 404:  # come Pages: la 404 personalizzata del sito, con il suo codice 404
                    f = Path(radice) / "arcotour-site" / "404.html"
                    corpo = f.read_bytes()
                    self.send_response(404)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(corpo)))
                    self.end_headers()
                    self.wfile.write(corpo)
                else:
                    super().send_error(code, message, explain)

        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Gestore)
        cls.porta = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.sito = check_site.Sito(RADICE)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls._tmp.cleanup()

    def prendi(self, percorso: str):
        url = f"http://127.0.0.1:{self.porta}{percorso}"
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                return r.status, r.headers.get("Content-Type", ""), r.read()
        except urllib.error.HTTPError as ex:
            return ex.code, ex.headers.get("Content-Type", ""), ex.read()

    def test_ogni_pagina_risponde(self):
        for f in self.sito.pagine:
            stato, tipo, corpo = self.prendi("/arcotour-site/" + f)
            self.assertEqual(stato, 200, f)
            self.assertIn("text/html", tipo, f)
        self.assertEqual(self.prendi("/arcotour-site/")[0], 200)
        self.assertEqual(self.prendi("/arcotour-site/en/")[0], 200)

    def test_ogni_risorsa_collegata_si_raggiunge_con_l_indirizzo_che_il_browser_costruirebbe(self):
        """Per ogni pagina: tutti gli src/href relativi, risolti come fa un browser a partire dall'indirizzo vero della pagina."""
        from urllib.parse import urljoin
        for f, p in self.sito.pagine.items():
            indirizzo_pagina = f"http://127.0.0.1:{self.porta}/arcotour-site/{f}"
            if f == "404.html":
                indirizzo_pagina = f"http://127.0.0.1:{self.porta}/arcotour-site/"  # con <base> è come stare nella radice
            riferimenti = [l["href"] for l in p.a if l["href"]] + [i.get("src") for i in p.img] + [l.get("href") for l in p.link if l.get("href")]
            riferimenti += [a.get("src") for _, a, _ in p.script if a.get("src")]
            for r in riferimenti:
                if r.startswith(("https://", "mailto:", "#")):
                    continue
                url = urljoin(indirizzo_pagina, r.split("#")[0])
                stato = self.prendi(url[len(f"http://127.0.0.1:{self.porta}"):])[0]
                self.assertEqual(stato, 200, f"{f}: «{r}» → {url}")

    def test_la_404_arriva_con_codice_404_e_trova_i_suoi_file_da_qualsiasi_profondita(self):
        for percorso in ("/arcotour-site/non-esiste.html", "/arcotour-site/en/non-esiste", "/arcotour-site/a/b/c/d"):
            stato, tipo, corpo = self.prendi(percorso)
            self.assertEqual(stato, 404, percorso)
            self.assertIn(b"Pagina non trovata", corpo)
            self.assertIn(b'<base href="/arcotour-site/">', corpo)

    def test_i_caratteri_hanno_il_tipo_giusto_e_si_trovano(self):
        for f in ("PlayfairDisplay-Bold.ttf", "inter-regular.woff2", "inter-semibold.woff2"):
            stato, tipo, corpo = self.prendi("/arcotour-site/assets/fonts/" + f)
            self.assertEqual(stato, 200, f)
            self.assertGreater(len(corpo), 5000, f)

    def test_le_ancore_delle_domande_esistono_nelle_due_lingue(self):
        for pagina in ("support.html", "en/support.html"):
            ids = self.sito.ids_di(pagina)
            for ancora in ("come-funzionano-i-pass", "ripristino-acquisti", "abbonamento", "rimborsi", "durata-scadenza"):
                self.assertIn(ancora, ids, pagina)


if __name__ == "__main__":
    unittest.main(verbosity=1)
