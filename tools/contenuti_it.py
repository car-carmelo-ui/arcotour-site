"""Testi del sito in ITALIANO.

Regole di scrittura (le stesse dell'app, docs/store-testi.md «Cosa NON dire»):
  - nessuna promessa che l'app non mantiene; i pass sono TEMPORANEI e senza rinnovo (mai «permanente» o «illimitato»);
  - la mappa ha bisogno di internet; racconti, testi e foto no;
  - niente orari o biglietti dei musei; solo iPhone; l'app non è ancora in vendita;
  - nessun dato personale, nessuna email, nessun dato legale inventato: i dati di chi pubblica arrivano da content/site.json.

Piccolo linguaggio dei testi (lo traduce tools/sitegen.py):
  [testo](https://...)   collegamento esterno         [testo](@support.html#pass)   pagina del sito nella stessa lingua
  **grassetto**          righe che iniziano con «- » = elenco puntato     riga vuota = nuovo paragrafo
  {email} {titolare} {indirizzo} {aggiornata}   dati di chi pubblica (se mancano, si vede un segnaposto evidente)
"""

T = {
    "lingua": "it",
    "locale": "it_IT",
    "nome_lingua": "Italiano",
    "ui": {
        "salta": "Vai al contenuto",
        "menu": "Menu",
        "menu_aria": "Menu principale",
        "lingua_aria": "Lingua del sito",
        "home_aria": "ArcoTour, pagina iniziale",
        "foto": "Foto",
        "tappe": "tappe",
        "tappa": "tappa",
        "a_piedi": "A piedi",
        "in_metro": "In metro",
        "e_altre": "e altre {n} tappe",
        "vai_a": "Vai a",
        "bozza_titolo": "Versione in revisione.",
        "bozza_testo": "Questa pagina sarà completata con i dati di chi pubblica l’app e, per le parti legali, controllata da un legale prima del lancio.",
        "segnaposto": {
            "titolare": "[da completare: nome o ragione sociale]",
            "indirizzo": "[da completare: indirizzo]",
            "email": "[da completare: email di assistenza]",
        },
        "data_aggiornamento": "12 ottobre 2026",
    },
    "nav": [
        {"id": "roma", "etichetta": "Percorsi", "href": "@index.html#roma"},
        {"id": "audioguide", "etichetta": "Audioguide", "href": "@index.html#audioguide"},
        {"id": "mappe", "etichetta": "Mappe e mezzi", "href": "@index.html#mappe"},
        {"id": "pass", "etichetta": "Pass", "href": "@index.html#pass"},
        {"id": "supporto", "etichetta": "Assistenza", "href": "@support.html"},
    ],
    "piede": {
        "frase": "Dall’arrivo in città alla fine del tour, mezzi compresi.",
        "titolo_link": "Il sito",
        "link": [
            {"etichetta": "Assistenza", "href": "@support.html"},
            {"etichetta": "Informativa sulla privacy", "href": "@privacy.html"},
            {"etichetta": "Condizioni d’uso", "href": "@terms.html"},
            {"etichetta": "Crediti", "href": "@index.html#crediti"},
        ],
        "marchi": "iPhone e App Store sono marchi di Apple Inc., registrati negli Stati Uniti e in altri Paesi.",
        "copyright": "© 2026 ArcoTour. Tutti i diritti riservati.",
        "foto_nota": "Le fotografie appartengono ai rispettivi autori: crediti e licenze in fondo alla pagina iniziale.",
    },
    # ------------------------------------------------------------------------------------------------ pagina iniziale
    "home": {
        "titolo": "ArcoTour · Audioguida a piedi per Roma",
        "descrizione": "ArcoTour è l’audioguida per scoprire Roma camminando: dieci percorsi a piedi e in metro, con racconti in italiano e inglese che partono da soli a ogni tappa.",
        "occhiello": "Audioguida a piedi · Roma",
        "h1": "Roma a piedi, con la voce giusta al posto giusto.",
        "lead": "ArcoTour è l’audioguida per scoprire il centro storico di Roma camminando. Scegli un percorso e cammina: quando arrivi a una tappa, il racconto parte da solo, anche con il telefono in tasca e lo schermo spento.",
        "cta_principale": "Scopri i percorsi",
        "cta_secondaria": "Come funziona",
        "disponibilita": {
            "prossimamente": "Prossimamente su App Store · solo iPhone",
            "disponibile": "Disponibile su App Store · solo iPhone",
        },
        "fatti": [
            {"valore": "10", "etichetta": "percorsi nel centro di Roma"},
            {"valore": "2", "etichetta": "lingue: italiano e inglese"},
            {"valore": "0", "etichetta": "account da creare"},
        ],
        "come": {
            "occhiello": "Come funziona",
            "h2": "Scegli, cammina, ascolta.",
            "passi": [
                {"titolo": "Scegli un percorso",
                 "testo": "Dieci percorsi nel centro di Roma, a piedi o in metro: dal Colosseo al Gianicolo, da Trastevere al Tridente."},
                {"titolo": "Premi «Inizia il tour» e cammina",
                 "testo": "Con il telefono in tasca. Per far partire i racconti da soli serve consentire la posizione, anche con l’app in secondo piano."},
                {"titolo": "Ascolta a ogni tappa",
                 "testo": "Quando arrivi, la voce parte da sola, in italiano o in inglese. Se il GPS non basta, tocchi il numero della tappa."},
            ],
        },
        "roma": {
            "occhiello": "Roma, la prima destinazione",
            "h2": "Dieci percorsi per scoprire il centro storico.",
            "lead": "Dall’antica Roma ai palazzi barocchi, da Trastevere al Gianicolo: percorsi a piedi e in metro, con un racconto per ogni tappa.",
            "tutti": "Tutti i percorsi",
            "nota": "Nell’app i percorsi si possono combinare con deviazioni facoltative e dettagli lungo il cammino.",
        },
        "audioguide": {
            "occhiello": "Audioguide",
            "h2": "Racconti che partono da soli.",
            "testo": ("A ogni tappa il racconto parte quando arrivi, anche con il telefono in tasca e lo schermo spento.\n\n"
                      "Le voci sono sintetiche, generate con l’intelligenza artificiale. I testi non nascono dal nulla: partono da fatti con una fonte indicata e vengono approvati prima di diventare audio."),
            "punti": [
                "In italiano e in inglese.",
                "Racconti, testi e foto sono dentro l’app: funzionano anche senza internet.",
                "Ascolta con attenzione a ciò che ti circonda e rispetta semafori e traffico.",
            ],
            "citazione": "Prima i fatti, poi il racconto.",
            "citazione_nota": "È la regola con cui nasce ogni testo di ArcoTour.",
        },
        "mappe": {
            "occhiello": "Mappe e mezzi pubblici",
            "h2": "Dall’arrivo in città alla fine del tour, mezzi compresi.",
            "lead": "ArcoTour ti accompagna anche negli spostamenti: sai dove sono le fermate vicine e come arrivarci a piedi.",
            "schede": [
                {"titolo": "Mezzi", "testo": "La scheda Mezzi mostra le fermate dei mezzi pubblici vicine e le linee, con il percorso di ogni linea."},
                {"titolo": "Accompagnami", "testo": "Ti guida a piedi fino alla fermata scelta."},
                {"titolo": "Il tuo tour", "testo": "Scegli sulla mappa i luoghi che ti interessano: l’app li mette nell’ordine che fa camminare di meno."},
            ],
            "nota": "Le mappe sono di OpenStreetMap e per mostrarle serve internet.",
        },
        "pass": {
            "occhiello": "Pass Roma",
            "h2": "L’app è gratuita. I racconti si sbloccano con un pass.",
            "lead": "Tre pass temporanei per Roma. Pagamento unico, nessun rinnovo automatico: il tempo conta dal momento dell’acquisto e, alla scadenza, l’accesso ai racconti finisce da solo.",
            "per_ogni": "Tutti i tour di Roma",
            "dall_acquisto": "Dall’acquisto, per {durata}",
            "bollini": ["Pagamento unico", "Senza rinnovo automatico"],
            "punti": [
                "I tre pass sbloccano gli stessi contenuti: cambia solo la durata.",
                "Le durate non si sommano: con più pass validi vale quello che scade più tardi.",
                "Restano sempre gratuiti la presentazione di Roma, le schede dei percorsi, la scheda Mezzi e «Accompagnami».",
                "Un pass di Roma non sblocca altre città.",
            ],
            "nota": "Prezzi indicativi per l’Italia: il prezzo definitivo è quello mostrato dall’App Store al momento dell’acquisto. Gli acquisti saranno disponibili con il lancio dell’app.",
            "link": "Domande sui pass e sul ripristino degli acquisti",
        },
        "privacy": {
            "occhiello": "Privacy",
            "h2": "La tua posizione resta sul tuo telefono.",
            "testo": ("ArcoTour non ha account, non ha pubblicità e non usa strumenti di analisi o di tracciamento.\n\n"
                      "Usa internet solo per due cose: scaricare le mappe da OpenStreetMap e, se compri un pass, parlare con l’App Store di Apple."),
            "link": "Leggi l’informativa sulla privacy",
        },
        "crediti": {
            "h2": "Crediti",
            "foto": ("Le fotografie vengono da Wikimedia Commons e appartengono ai rispettivi autori, che le hanno rilasciate con le licenze indicate "
                     "qui sotto. Sono ridimensionate per il web."),
            "colonne": {"foto": "Foto", "autore": "Autore", "licenza": "Licenza", "fonte": "Fonte"},
            "fonte_link": "Pagina del file",
            "mappe": "I dati delle mappe dell’app sono © [contributori di OpenStreetMap](https://www.openstreetmap.org/copyright), disponibili con licenza ODbL.",
            "caratteri": "Caratteri: Playfair Display e Inter, con licenza SIL Open Font License 1.1 ([Inter](@@assets/fonts/OFL-Inter.txt), [Playfair Display](@@assets/fonts/OFL-PlayfairDisplay.txt)).",
        },
        "json_ld_descrizione": "Audioguida a piedi per Roma: percorsi a piedi e in metro, racconti in italiano e inglese che partono da soli a ogni tappa.",
    },
    # ---------------------------------------------------------------------------------------------------- assistenza
    "supporto": {
        "titolo": "Assistenza · ArcoTour",
        "descrizione": "Assistenza per ArcoTour: domande frequenti su tour, posizione, mappe, pass Roma e ripristino degli acquisti, e come contattarci.",
        "occhiello": "Assistenza",
        "h1": "Come possiamo aiutarti?",
        "lead": "Qui trovi le risposte alle domande più frequenti su ArcoTour. Se non basta, scrivici.",
        "contatto": {
            "titolo": "Scrivici",
            "testo": ("Per assistenza, segnalazioni e suggerimenti scrivi a {email}.\n\n"
                      "Per aiutarci a capire, indica il modello di iPhone, la versione di iOS e la versione di ArcoTour (la trovi nel Profilo)."),
        },
        "indice": "Domande frequenti",
        "gruppi": [
            {"id": "iniziare", "titolo": "Per cominciare", "domande": [
                {"id": "come-iniziare", "q": "Come comincio un tour?",
                 "a": ("Apri l’app, scegli Roma e un percorso, poi premi «Inizia il tour» e cammina. Quando arrivi a una tappa il racconto parte da solo.\n\n"
                       "Se il GPS non basta (in galleria o in metro, per esempio), tocca il numero della tappa per far partire il racconto a mano.")},
                {"id": "dispositivi", "q": "Su quali dispositivi funziona?",
                 "a": "ArcoTour è pensata per iPhone, con iOS 15 o successivo. La versione 1.0 non ha una versione dedicata a iPad."},
                {"id": "lingua", "q": "Come cambio la lingua?",
                 "a": ("L’app parte in italiano se il telefono è in italiano, altrimenti in inglese. Per cambiare usa il selettore IT/EN in alto a destra: "
                       "vale per l’interfaccia, per i testi e per i racconti audio.")},
            ]},
            {"id": "posizione", "titolo": "Posizione e racconti", "domande": [
                {"id": "racconti-non-partono", "q": "I racconti non partono da soli quando arrivo a una tappa.",
                 "a": ("Controlla in Impostazioni di iOS → Privacy e sicurezza → Localizzazione → ArcoTour che l’accesso sia «Durante l’uso dell’app» o «Sempre» e che «Posizione precisa» sia attiva. "
                       "Poi apri il tour e premi «Inizia il tour»: l’app deve restare in funzione (può stare a schermo spento o in secondo piano).\n\n"
                       "Il GPS funziona male dentro le gallerie o in metro. Se non si riconosce l’arrivo, puoi sempre toccare il numero della tappa per far partire il racconto a mano.")},
                {"id": "schermo-spento", "q": "Funziona con lo schermo spento o con il telefono in tasca?",
                 "a": ("Sì. Durante un tour l’app usa la posizione e l’audio anche a schermo bloccato o in secondo piano, così il racconto parte anche con il telefono in tasca. "
                       "Quando la posizione è in uso, iOS mostra un indicatore.")},
                {"id": "posizione-privacy", "q": "Perché ArcoTour usa la mia posizione? Va a qualcuno?",
                 "a": ("La usa per far partire il racconto quando arrivi a una tappa, per mostrarti le fermate dei mezzi pubblici vicine e per guidarti a piedi fino a una fermata.\n\n"
                       "Resta sul tuo telefono: non viene salvata, non arriva a noi e non viene condivisa con nessuno. Puoi ritirare il permesso quando vuoi da Impostazioni di iOS. "
                       "Dettagli nell’[informativa sulla privacy](@privacy.html).")},
            ]},
            {"id": "mappe-mezzi", "titolo": "Mappe e mezzi pubblici", "domande": [
                {"id": "internet", "q": "Serve internet?",
                 "a": ("I racconti audio, i testi e le foto sono dentro l’app e funzionano senza rete. Le mappe si scaricano da OpenStreetMap: senza internet vedi quelle già viste, "
                       "e una zona nuova resta vuota (i segnaposto e i comandi funzionano lo stesso). L’acquisto di un pass richiede internet.")},
                {"id": "mappa-vuota", "q": "La mappa è vuota o a pezzi.",
                 "a": ("Con una connessione debole alcune parti della mappa possono mancare: l’app lo segnala e riprova da sola poche volte. "
                       "Controlla la connessione e riapri la schermata. I segnaposto e i comandi funzionano comunque.")},
                {"id": "mezzi", "q": "Che cosa fanno la scheda Mezzi e «Accompagnami»?",
                 "a": "La scheda Mezzi mostra le fermate dei mezzi pubblici vicine e le linee. «Accompagnami» ti guida a piedi fino alla fermata scelta."},
            ]},
            {"id": "pass", "titolo": "Pass Roma e acquisti", "domande": [
                {"id": "come-funzionano-i-pass", "q": "Come funzionano i pass Roma?",
                 "a": ("Sono tre pass temporanei: **Roma 24 ore** ({p24}), **Roma 72 ore** ({p72}) e **Roma Completa** (10 giorni, cioè 240 ore, {p10}). "
                       "Pagamento unico, nessun rinnovo automatico.\n\n"
                       "Il tempo conta dal momento dell’acquisto. Alla scadenza l’accesso ai racconti finisce e basta. I prezzi indicati valgono per l’Italia: il prezzo definitivo "
                       "è quello che mostra l’App Store, nella tua valuta.")},
                {"id": "cosa-sblocca", "q": "Che cosa sblocca un pass e che cosa resta gratuito?",
                 "a": ("Un pass sblocca i racconti dei tour («Inizia il tour»), «Il tuo tour» e i racconti di arrivo. I tre pass sbloccano gli stessi contenuti: cambia solo la durata. "
                       "Un pass di Roma non sblocca altre città.\n\n"
                       "Restano sempre gratuiti la presentazione di Roma, le schede dei percorsi (tappe, foto e descrizione), la scheda Mezzi e «Accompagnami».")},
                {"id": "durata-scadenza", "q": "Quanto dura un pass? Che cosa succede alla scadenza?",
                 "a": ("Dal momento dell’acquisto, per il numero di ore esatto: 24, 72 oppure 240 (10 giorni). Il pass Roma Completa dura 10 giorni dall’acquisto: non è permanente né illimitato.\n\n"
                       "Le durate non si sommano: con più pass validi vale quello che scade più tardi. Per esempio, 24 ore comprate a mezzogiorno e altre 24 ore comprate 12 ore dopo finiscono "
                       "36 ore dopo il primo acquisto, non 48. Dopo la scadenza puoi comprare un nuovo pass quando vuoi.")},
                {"id": "abbonamento", "q": "È un abbonamento? Devo annullare qualcosa?",
                 "a": "No. I pass non sono abbonamenti e non si rinnovano da soli: non c’è niente da annullare."},
                {"id": "ripristino-acquisti", "q": "Ho comprato un pass ma non lo vedo. Come ripristino gli acquisti?",
                 "a": ("Apri il Profilo e guarda la scheda del pass: dice «Pass attivo» e fino a quando vale. Se non compare, premi «Dettagli» e poi «Ripristina acquisti» "
                       "(serve internet e lo stesso account Apple con cui hai pagato).\n\n"
                       "Se non risolvi, scrivici a {email} indicando la data dell’acquisto.")},
                {"id": "rimborsi", "q": "Come chiedo un rimborso?",
                 "a": ("Per i rimborsi decide Apple: vai su [reportaproblem.apple.com](https://reportaproblem.apple.com). "
                       "Un acquisto rimborsato da Apple non dà più accesso ai contenuti a pagamento.")},
            ]},
            {"id": "privacy-dati", "titolo": "Privacy e dati", "domande": [
                {"id": "account", "q": "Devo creare un account?",
                 "a": "No. ArcoTour non ha account e non ha pubblicità."},
                {"id": "informativa", "q": "Dove trovo l’informativa sulla privacy?",
                 "a": "Dentro l’app, nel Profilo → «Informativa sulla privacy», e qui: [informativa sulla privacy](@privacy.html)."},
                {"id": "crediti-foto", "q": "Di chi sono le foto e le mappe?",
                 "a": ("Le foto vengono da Wikimedia Commons, con i crediti degli autori e le licenze; le mappe sono di OpenStreetMap. "
                       "I crediti sono nell’app (Profilo → «Licenze e crediti») e in fondo alla [pagina iniziale](@index.html#crediti) del sito.")},
            ]},
            {"id": "contenuti", "titolo": "Contenuti", "domande": [
                {"id": "errori", "q": "Ho trovato un errore in un racconto o in una foto.",
                 "a": ("Scrivici a {email} indicando il percorso, la tappa e che cosa non va. Le voci sono sintetiche, generate con l’intelligenza artificiale, "
                       "e i testi partono da fatti con una fonte indicata: ogni segnalazione ci aiuta a correggere.")},
                {"id": "orari-biglietti", "q": "L’app dà orari e biglietti dei musei?",
                 "a": "No: cambiano spesso. Controlla sempre i siti ufficiali dei luoghi che visiti."},
            ]},
        ],
    },
    # ------------------------------------------------------------------------------------------------------ privacy
    "privacy": {
        "titolo": "Informativa sulla privacy · ArcoTour",
        "descrizione": "Informativa sulla privacy di ArcoTour: la tua posizione resta sul telefono, nessun account, nessuna pubblicità, nessuno strumento di analisi.",
        "occhiello": "Privacy",
        "h1": "Informativa sulla privacy",
        "sottotitolo": "L’app ArcoTour (versione 1.0, Roma) e questo sito",
        "aggiornata_etichetta": "Informativa dell’app aggiornata all’",
        "indice": "In questa pagina",
        "parte_app": "L’app",
        "parte_sito": "Questo sito web",
        "sito": {
            "id": "sito-web",
            "titolo": "Cookie, dati di navigazione e email",
            "testo": ("Questo sito non usa cookie, non ha strumenti di analisi o di tracciamento e non carica caratteri, immagini o script da altri servizi: tutto quello che vedi è ospitato qui.\n\n"
                      "Il sito è ospitato da GitHub Pages (GitHub, Inc.). Come spiega GitHub, quando si visita un sito GitHub Pages l’indirizzo IP del visitatore viene registrato e conservato da GitHub "
                      "per motivi di sicurezza, anche se il visitatore non ha un account GitHub. Noi non usiamo questi dati. Come GitHub li tratta è spiegato nella sua "
                      "[informativa sulla privacy](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement) e nella pagina "
                      "[Che cos’è GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection).\n\n"
                      "Se ci scrivi un’email, usiamo il tuo indirizzo e il contenuto del messaggio solo per risponderti."),
        },
    },
    # --------------------------------------------------------------------------------------------------- condizioni
    "condizioni": {
        "titolo": "Condizioni d’uso · ArcoTour",
        "descrizione": "Condizioni d’uso di ArcoTour: come funziona l’app, i pass Roma (24 ore, 72 ore, 10 giorni, pagamento unico, senza rinnovo), ripristino e rimborsi.",
        "occhiello": "Condizioni",
        "h1": "Condizioni d’uso",
        "sottotitolo": "L’app ArcoTour (iPhone) e questo sito",
        "aggiornate": "Ultimo aggiornamento: {data}.",
        "sezioni": [
            {"id": "chi-siamo", "titolo": "Chi fornisce il servizio",
             "testo": ("ArcoTour è fornito da {titolare}, {indirizzo}. Per qualsiasi domanda scrivi a {email}.\n\n"
                       "Scaricando o usando l’app accetti queste condizioni. Si applicano insieme al "
                       "[contratto di licenza standard di Apple per le app](https://www.apple.com/legal/internet-services/itunes/dev/stdeula/), valido per tutte le app dell’App Store.")},
            {"id": "servizio", "titolo": "Che cos’è ArcoTour",
             "testo": ("ArcoTour è un’audioguida per iPhone che accompagna a piedi nei centri storici. La versione 1.0 riguarda Roma: percorsi a piedi e in metro, racconti audio in italiano e inglese, "
                       "mappe, fermate dei mezzi pubblici e la funzione «Il tuo tour». Serve iOS 15 o successivo; non c’è una versione dedicata a iPad.\n\n"
                       "L’app è gratuita da scaricare. I racconti dei tour si sbloccano con un pass a pagamento (vedi «I pass Roma»).")},
            {"id": "uso", "titolo": "Come usare ArcoTour in sicurezza",
             "testo": ("- Cammina in sicurezza: rispetta semafori e traffico e ascolta con attenzione a ciò che ti circonda.\n"
                       "- I percorsi e le indicazioni sono un aiuto, non sostituiscono la segnaletica, le regole del luogo e il buon senso.\n"
                       "- Orari di apertura, biglietti e accessi dei luoghi che visiti non sono nell’app e cambiano: controlla sempre i siti ufficiali.\n"
                       "- Per far partire i racconti da soli serve consentire la posizione, anche con l’app in secondo piano; puoi ritirare il permesso quando vuoi.")},
            {"id": "contenuti", "titolo": "I contenuti",
             "testo": ("I racconti sono letti da voci sintetiche, generate con l’intelligenza artificiale. I testi partono da fatti con una fonte indicata e vengono approvati prima di diventare audio, "
                       "ma possono contenere imprecisioni: se ne trovi, scrivici.\n\n"
                       "I contenuti hanno scopo informativo e culturale.")},
            {"id": "pass", "titolo": "I pass Roma",
             "testo": ("- **Che cosa sono.** Tre pass temporanei per Roma: **Roma 24 ore**, **Roma 72 ore** e **Roma Completa** (10 giorni, cioè 240 ore). Sbloccano gli stessi contenuti: cambia solo la durata. "
                       "Un pass di Roma non sblocca altre città.\n"
                       "- **Che cosa sbloccano.** I racconti dei tour («Inizia il tour»), «Il tuo tour» e i racconti di arrivo. Restano gratuiti la presentazione di Roma, le schede dei percorsi, la scheda Mezzi e «Accompagnami».\n"
                       "- **Prezzi.** {p24}, {p72} e {p10} in Italia. Il prezzo definitivo è quello mostrato dall’App Store al momento dell’acquisto.\n"
                       "- **Pagamento unico, nessun rinnovo automatico.** I pass non sono abbonamenti e non si rinnovano da soli. Il pass Roma Completa dura 10 giorni dall’acquisto: non è permanente né illimitato.\n"
                       "- **Durata.** Dal momento dell’acquisto verificato, per il numero di ore esatto. Alla scadenza l’accesso ai racconti finisce da solo. Le durate non si sommano: con più pass validi vale quello che scade più tardi.\n"
                       "- **Pagamento.** L’acquisto avviene con il tuo account Apple; il pagamento e la fatturazione li gestisce Apple.\n"
                       "- **Ripristino.** Dal Profilo → «Dettagli» → «Ripristina acquisti», con lo stesso account Apple (serve internet).\n"
                       "- **Rimborsi.** Li gestisce Apple ([reportaproblem.apple.com](https://reportaproblem.apple.com)). Un acquisto rimborsato non dà più accesso ai contenuti a pagamento.")},
            {"id": "recesso", "titolo": "Diritti dei consumatori",
             "testo": ("Se sei un consumatore, i diritti che la legge ti riconosce restano quelli previsti dalla normativa applicabile e dalle condizioni di Apple per gli acquisti sull’App Store, "
                       "compresi quelli sul recesso e sui contenuti digitali. Queste condizioni non li limitano.")},
            {"id": "proprieta", "titolo": "Proprietà intellettuale e crediti",
             "testo": ("L’app, i testi, i racconti audio e la grafica di ArcoTour appartengono a chi la pubblica. Ti è concesso di usarli personalmente, con l’app, senza copiarli, estrarli o ridistribuirli.\n\n"
                       "Le fotografie appartengono ai rispettivi autori e sono usate con le loro licenze (Wikimedia Commons); i dati delle mappe sono © contributori di OpenStreetMap (licenza ODbL). "
                       "I crediti sono nell’app (Profilo → «Licenze e crediti») e in [fondo alla pagina iniziale](@index.html#crediti).")},
            {"id": "disponibilita", "titolo": "Disponibilità e modifiche",
             "testo": ("L’app e i contenuti possono cambiare, essere aggiornati o sospesi. Le mappe dipendono da OpenStreetMap e dalla connessione a internet; "
                       "la posizione dipende dal GPS del telefono, che può funzionare male in galleria, in metro o tra edifici alti.")},
            {"id": "responsabilita", "titolo": "Responsabilità",
             "testo": ("Nei limiti consentiti dalla legge, ArcoTour è fornito così com’è, senza garanzie che sia sempre disponibile o privo di errori. "
                       "Nulla in queste condizioni esclude o limita diritti e responsabilità che la legge non permette di escludere o limitare.")},
            {"id": "privacy", "titolo": "Privacy",
             "testo": "La tua posizione resta sul tuo telefono e ArcoTour non ha account né pubblicità. Tutti i dettagli sono nell’[informativa sulla privacy](@privacy.html)."},
            {"id": "modifiche", "titolo": "Modifiche a queste condizioni",
             "testo": "Se queste condizioni cambiano, aggiorniamo questa pagina e la data qui sopra, e lo diciamo nell’app prima che le modifiche valgano per te."},
            {"id": "legge", "titolo": "Legge applicabile",
             "testo": "Si applica la legge italiana, fatte salve le norme inderogabili a tutela dei consumatori del Paese in cui vivi."},
            {"id": "contatti", "titolo": "Contatti",
             "testo": "Per domande su queste condizioni scrivi a {email}."},
        ],
    },
    # -------------------------------------------------------------------------------------------------------- 404
    "pagina404": {
        "titolo": "Pagina non trovata · ArcoTour",
        "h1": "Pagina non trovata",
        "testo": "La pagina che cerchi non esiste o è stata spostata.",
        "link": "Torna alla pagina iniziale",
    },
}
