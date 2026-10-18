# arcotour-site

Official website of ArcoTour, a cultural tourism app featuring self-guided itineraries, interactive maps and audio guides in Italian and English.

Il sito pubblico di **ArcoTour**, l'audioguida a piedi per il centro storico di Roma (prima destinazione), pubblicato con
GitHub Pages: <https://car-carmelo-ui.github.io/arcotour-site/>

| Pagina | Italiano | English |
| --- | --- | --- |
| Pagina iniziale | `/` | `/en/` |
| Assistenza (domande frequenti, pass Premium, ripristino acquisti, contatto) | `/support.html` | `/en/support.html` |
| Informativa sulla privacy | `/privacy.html` | `/en/privacy.html` |
| Condizioni d'uso | `/terms.html` | `/en/terms.html` |

I tre indirizzi per App Store Connect (URL di assistenza, URL di marketing, informativa sulla privacy) sono in fondo a questo file.

## Come è fatto

È un sito **statico**: solo HTML, CSS e un po' di JavaScript. Non ha cookie, non ha strumenti di analisi, non usa account, non
carica caratteri, immagini o script da altri siti (le prove lo controllano). Funziona sotto `/arcotour-site/` perché ogni
collegamento è **relativo**.

**Le pagine HTML sono generate: non si modificano a mano.** Si cambiano i testi o i dati e si rigenera:

| Che cosa | Dove |
| --- | --- |
| Testi in italiano / in inglese | `tools/contenuti_it.py`, `tools/contenuti_en.py` |
| Dati di chi pubblica, stato dell'app, prezzi dei pass | `content/site.json` |
| Percorsi, foto e informativa dell'app | `content/percorsi.json`, `content/foto.json`, `content/informativa_app.json` (importati dall'app) |
| Aspetto | `assets/css/site.css` |
| Il costruttore | `tools/sitegen.py` (si lancia con `tools/build_site.py`) |

## Comandi (solo Python 3, nessuna libreria da installare)

```
python3 tools/build_site.py            # rigenera le pagine
python3 tools/build_site.py --verifica # dice se le pagine sono aggiornate
python3 tools/check_site.py            # controlla tutto: collegamenti, SEO, accessibilità, contrasti, privacy, IT/EN uguali
python3 tools/check_site.py --rilascio # in più, il «cancello» della pubblicazione definitiva (vedi sotto)
python3 tools/check_site.py --esterni  # elenca gli indirizzi esterni usati (da riprovare in rete ogni tanto)
python3 tools/test_site.py             # prove: gli inseriscono di proposito errori e verificano che il controllo li veda
python3 -m http.server 8000            # anteprima su http://localhost:8000/
```

Dopo ogni modifica: `build_site.py`, poi `check_site.py` e `test_site.py` devono essere verdi.

## Prima della pubblicazione definitiva

Finché mancano i dati di chi pubblica, il sito dice **«Versione in revisione»**, i punti mancanti sono evidenziati
(«[da completare: …]»), le pagine di assistenza, privacy e condizioni sono **non indicizzabili** (`noindex`) e non stanno nella
`sitemap.xml`. Questo è voluto: nessun dato viene inventato.

1. In `content/site.json`, sotto `venditore`, scrivere **nome o ragione sociale**, **indirizzo/sede** ed **email di assistenza**
   (un indirizzo dedicato ad ArcoTour, non una casella personale: finisce in pagine pubbliche). Dal 14/10/2026 nome
   (Carmelo Albanese), indirizzo («Terranova Sappo Minulio (RC), Italia», ridotto con il commit del 14/10/2026 «Riduci esposizione dell'indirizzo privato…») ed
   email ci sono. **Quale indirizzo sia pubblico resta una decisione di Carmelo** (il 18/10/2026 ha scritto che l'indirizzo fisico
   verrà inserito in seguito): nessun indirizzo si inventa.
2. Far leggere a un legale le **condizioni d'uso** e la parte «Questo sito web» dell'informativa (recesso, responsabilità, legge
   applicabile, hosting su GitHub negli Stati Uniti, gestione delle email).
3. Solo dopo l'approvazione: in `content/site.json` mettere `"revisione_legale": "approvata"`, rigenerare con `build_site.py`
   e lanciare `python3 tools/check_site.py --rilascio`: deve dire «pronto per la pubblicazione definitiva».
4. Quando l'app sarà su App Store: `"app": {"stato": "disponibile", "app_store_url": "https://apps.apple.com/…"}` e rigenerare.
   Fino ad allora la pagina iniziale dice «Prossimamente» e non contiene nessun collegamento all'App Store.

**Punti da confermare nell'informativa (13/10/2026).** Un testo già scritto che aspetta la conferma di un legale si racchiude fra `{!` e `}`
(in `content/legale/privacy.yaml` dell'app, da cui si importa; o in `tools/contenuti_*.py`): sulla pagina è **evidenziato**, la legenda nel
riquadro «Versione in revisione» lo spiega, e **finché ce n'è anche uno le pagine legali restano in revisione** (`noindex`, fuori dalla
`sitemap.xml`) e il cancello `--rilascio` resta chiuso. Si conferma togliendo SOLO le graffe e il punto esclamativo. Un dato che
**manca** (non scritto) si segna `{?etichetta}`: sulla pagina compare «[da completare: etichetta]». Dal 18/10/2026 i punti da
confermare sono 6 per lingua, tutti nella sezione «Chi siamo e perché trattiamo i dati»: basi giuridiche, trasferimenti fuori dall'UE e
minori (nessuna età scritta: il 4+ dell'App Store non è l'età minima della privacy); la revisione legale finale resta da fare.

**Frase sulla posizione (18/10/2026, voluta da Carmelo).** Nessuna pagina dice in modo generico che «la posizione resta sul telefono»:
le coordinate GPS restano sul dispositivo, ma per mostrare le mappe OpenStreetMap riceve l'area di mappa richiesta, che può indicare
approssimativamente dove si trova l'utente. `tools/check_site.py` rifiuta la formula generica, pretende la frase parola per parola
nell'informativa (IT e EN) e la precisazione nella pagina iniziale. La frase è la stessa di `FRASE_POSIZIONE` nel progetto dell'app.

I **prezzi dei pass** (24 ore €2,99, 72 ore €4,99, Roma Completa 10 giorni = 240 ore €7,99; pagamento unico, senza rinnovo
automatico) sono scritti in `content/site.json`. Il prezzo che vale è sempre quello mostrato dall'App Store: se cambia su App
Store Connect, cambiarlo anche qui. Il pass «Roma Completa» non è permanente né illimitato: dura 10 giorni dall'acquisto (le prove
lo controllano in tutte le pagine, in italiano e in inglese).

## Da dove vengono le cose

- **Foto**: solo da Wikimedia Commons, solo scorci esterni, ridimensionate. Autore, licenza e collegamento al file sono in
  `content/foto.json`, sono mostrati sotto ogni foto e nella tabella «Crediti» della pagina iniziale. Sono ammesse solo licenze che
  permettono l'uso commerciale (CC BY, CC BY-SA, CC0, pubblico dominio).
- **Icona**: l'icona ufficiale di ArcoTour (la stessa dell'app). **Caratteri**: Playfair Display e Inter, incorporati nel sito con le loro
  licenze (`assets/fonts/OFL-*.txt`).
- **Informativa sulla privacy**: la parte sull'app è copiata dall'informativa dell'app (unica fonte nel progetto dell'app), con in più
  la parte «Questo sito web». Se l'informativa dell'app cambia, si rilancia `python3 tools/importa_da_app.py <cartella-dell'app>`
  (serve il progetto dell'app, il Pillow e il PyYAML; copia solo materiale pubblico) e poi `build_site.py`.
  **Dal 18/10/2026** l'informativa importata (solo quella, non percorsi né foto) viene dal ramo `claude/zealous-lamport-nnnozj` del progetto
  dell'app, commit 546a5f4, **non ancora in `main`** (vedi `content/origine.json`): quando l'app sarà in `main`, rilanciare l'importatore.
- Questo sito **non è un parere legale**: testi legali e licenze vanno fatti controllare prima di usarli.

## Indirizzi per App Store Connect

Da inserire quando il sito sarà pubblicato e raggiungibile (si controllano con un browser):

| Campo di App Store Connect | Indirizzo |
| --- | --- |
| URL di marketing | <https://car-carmelo-ui.github.io/arcotour-site/> |
| URL di assistenza | <https://car-carmelo-ui.github.io/arcotour-site/support.html> |
| URL dell'informativa sulla privacy | <https://car-carmelo-ui.github.io/arcotour-site/privacy.html> |

Versioni inglesi: `/en/`, `/en/support.html`, `/en/privacy.html`. Condizioni d'uso: `/terms.html` (non è richiesto un campo apposito: si
può collegare nel campo «Contratto di licenza» o nella descrizione).

Apple controlla che la pagina di assistenza contenga **un modo per contattare** chi pubblica l'app: quindi l'email di assistenza
(punto 1) va inserita **prima** di inviare l'app alla revisione.
