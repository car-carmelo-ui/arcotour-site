"""Site texts in ENGLISH. Same structure and same ids as tools/contenuti_it.py (a check verifies they match).

Writing rules (the same as the app, docs/store-testi.md "Cosa NON dire"): no promise the app does not keep; the passes are
TEMPORARY and do not renew (never "permanent" or "unlimited"); the map needs internet, stories/texts/photos do not;
no museum hours or tickets; iPhone only; the app is not on sale yet; no personal data, email or legal detail made up.
App labels are quoted exactly as the app shows them (“Start the tour”, “Your tour”, “Take me there”, “Restore purchases”…).
Mini-markup: see tools/contenuti_it.py.
"""

T = {
    "lingua": "en",
    "locale": "en_GB",
    "nome_lingua": "English",
    "ui": {
        "salta": "Skip to content",
        "menu": "Menu",
        "menu_aria": "Main menu",
        "lingua_aria": "Site language",
        "home_aria": "ArcoTour, home page",
        "foto": "Photo",
        "tappe": "stops",
        "tappa": "stop",
        "a_piedi": "On foot",
        "in_metro": "By metro",
        "e_altre": "and {n} more stops",
        "vai_a": "Go to",
        "bozza_titolo": "Draft under review.",
        "bozza_testo": "This page will be completed with the publisher’s details and, for the legal parts, checked by a lawyer before launch.",
        "da_completare": "to be completed",
        "legenda_da_confermare": "The highlighted points are already written, but still to be confirmed.",
        "segnaposto": {
            "titolare": "[to be completed: name or company name]",
            "indirizzo": "[to be completed: address]",
            "email": "[to be completed: support email]",
        },
        "data_aggiornamento": "13 October 2026",
    },
    "nav": [
        {"id": "roma", "etichetta": "Routes", "href": "@index.html#roma"},
        {"id": "audioguide", "etichetta": "Audio guides", "href": "@index.html#audioguide"},
        {"id": "mappe", "etichetta": "Maps and transport", "href": "@index.html#mappe"},
        {"id": "pass", "etichetta": "Passes", "href": "@index.html#pass"},
        {"id": "supporto", "etichetta": "Support", "href": "@support.html"},
    ],
    "piede": {
        "frase": "From arriving in the city to the end of the tour, public transport included.",
        "titolo_link": "The site",
        "link": [
            {"etichetta": "Support", "href": "@support.html"},
            {"etichetta": "Privacy policy", "href": "@privacy.html"},
            {"etichetta": "Terms of use", "href": "@terms.html"},
            {"etichetta": "Credits", "href": "@index.html#crediti"},
        ],
        "marchi": "iPhone and App Store are trademarks of Apple Inc., registered in the U.S. and other countries.",
        "copyright": "© 2026 ArcoTour. All rights reserved.",
        "foto_nota": "The photographs belong to their authors: credits and licences are at the bottom of the home page.",
    },
    # ------------------------------------------------------------------------------------------------------ home
    "home": {
        "titolo": "ArcoTour · Walking audio tours of Rome",
        "descrizione": "ArcoTour is the audio guide for exploring Rome on foot: ten walking and metro routes, with stories in Italian and English that start by themselves at every stop.",
        "occhiello": "Walking audio tours · Rome",
        "h1": "Rome on foot, with the right voice in the right place.",
        "lead": "ArcoTour is the audio guide for exploring the historic centre of Rome as you walk. Pick a route and walk: when you reach a stop, the story starts by itself, even with your phone in your pocket and the screen off.",
        "cta_principale": "Explore the routes",
        "cta_secondaria": "How it works",
        "disponibilita": {
            "prossimamente": "Coming soon to the App Store · iPhone only",
            "disponibile": "Available on the App Store · iPhone only",
        },
        "fatti": [
            {"valore": "10", "etichetta": "routes in the centre of Rome"},
            {"valore": "2", "etichetta": "languages: Italian and English"},
            {"valore": "0", "etichetta": "accounts to create"},
        ],
        "come": {
            "occhiello": "How it works",
            "h2": "Pick, walk, listen.",
            "passi": [
                {"titolo": "Pick a route",
                 "testo": "Ten routes in the centre of Rome, on foot or by metro: from the Colosseum to the Janiculum, from Trastevere to the Trident."},
                {"titolo": "Press “Start the tour” and walk",
                 "testo": "With your phone in your pocket. For the stories to start by themselves, allow location, also while the app is in the background."},
                {"titolo": "Listen at every stop",
                 "testo": "When you arrive, the voice starts by itself, in Italian or English. If GPS is not enough, tap the stop number."},
            ],
        },
        "roma": {
            "occhiello": "Rome, the first destination",
            "h2": "Ten routes to discover the historic centre.",
            "lead": "From ancient Rome to Baroque palaces, from Trastevere to the Janiculum: routes on foot and by metro, with a story for every stop.",
            "tutti": "All the routes",
            "nota": "In the app the routes can be combined with optional detours and details along the way.",
        },
        "audioguide": {
            "occhiello": "Audio guides",
            "h2": "Stories that start by themselves.",
            "testo": ("At every stop the story starts when you arrive, even with your phone in your pocket and the screen off.\n\n"
                      "The voices are synthetic, generated with artificial intelligence. The texts do not come out of nowhere: they start from facts with a stated source and are approved before they become audio."),
            "punti": [
                "In Italian and in English.",
                "Stories, texts and photos are inside the app: they also work without internet.",
                "Listen with attention to your surroundings and obey traffic lights and traffic.",
            ],
            "citazione": "Facts first, then the story.",
            "citazione_nota": "It is the rule every ArcoTour text is born from.",
        },
        "mappe": {
            "occhiello": "Maps and public transport",
            "h2": "From arriving in the city to the end of the tour, public transport included.",
            "lead": "ArcoTour also helps you get around: you see where the nearby stops are and how to walk to them.",
            "schede": [
                {"titolo": "Transport", "testo": "The Transport tab shows the nearby public transport stops and lines, with the route of each line."},
                {"titolo": "Take me there", "testo": "It guides you on foot to the stop you chose."},
                {"titolo": "Your tour", "testo": "Pick the places you like on the map: the app puts them in the order that makes you walk the least."},
            ],
            "nota": "The maps are from OpenStreetMap and need internet to be shown.",
        },
        "pass": {
            "occhiello": "Rome passes",
            "h2": "The app is free. Stories unlock with a pass.",
            "lead": "Three temporary passes for Rome. One-time payment, no automatic renewal: the time counts from the moment you buy and, when it is up, access to the stories ends by itself.",
            "per_ogni": "All the tours of Rome",
            "dall_acquisto": "From purchase, for {durata}",
            "bollini": ["One-time payment", "No automatic renewal"],
            "punti": [
                "The three passes unlock the same content: only the duration changes.",
                "Durations do not add up: with several valid passes, the one that expires last applies.",
                "The introduction to Rome, the tour sheets, the Transport tab and “Take me there” always stay free.",
                "A Rome pass does not unlock other cities.",
            ],
            "nota": "Indicative prices for Italy: the final price is the one the App Store shows when you buy. Purchases will be available when the app launches.",
            "link": "Questions about passes and restoring purchases",
        },
        "privacy": {
            "occhiello": "Privacy",
            "h2": "GPS coordinates stay on the device.",
            "testo": ("ArcoTour has no accounts, no ads and no analytics or tracking tools.\n\n"
                      "It uses the internet for only two things: downloading maps from OpenStreetMap and, if you buy a pass, talking to Apple’s App Store. "
                      "To display the maps, OpenStreetMap receives the technical data of the request and the requested map area, which may approximately indicate the area where the user is located."),
            "link": "Read the privacy policy",
        },
        "crediti": {
            "h2": "Credits",
            "foto": ("The photographs come from Wikimedia Commons and belong to their authors, who released them under the licences listed "
                     "below. They are resized for the web."),
            "colonne": {"foto": "Photo", "autore": "Author", "licenza": "Licence", "fonte": "Source"},
            "fonte_link": "File page",
            "mappe": "The app’s map data is © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the ODbL licence.",
            "caratteri": "Fonts: Playfair Display and Inter, under the SIL Open Font License 1.1 ([Inter](@@assets/fonts/OFL-Inter.txt), [Playfair Display](@@assets/fonts/OFL-PlayfairDisplay.txt)).",
        },
        "json_ld_descrizione": "Walking audio tours of Rome: routes on foot and by metro, with stories in Italian and English that start by themselves at every stop.",
    },
    # -------------------------------------------------------------------------------------------------- support
    "supporto": {
        "titolo": "Support · ArcoTour",
        "descrizione": "ArcoTour support: frequently asked questions about tours, location, maps, Rome passes and restoring purchases, and how to contact us.",
        "occhiello": "Support",
        "h1": "How can we help?",
        "lead": "Here are the answers to the most frequent questions about ArcoTour. If they are not enough, write to us.",
        "contatto": {
            "titolo": "Write to us",
            "testo": ("For support, reports and suggestions write to {email}.\n\n"
                      "To help us understand, tell us your iPhone model, your iOS version and your ArcoTour version (you can find it in Profile)."),
        },
        "indice": "Frequently asked questions",
        "gruppi": [
            {"id": "iniziare", "titolo": "Getting started", "domande": [
                {"id": "come-iniziare", "q": "How do I start a tour?",
                 "a": ("Open the app, choose Rome and a route, then press “Start the tour” and walk. When you reach a stop the story starts by itself.\n\n"
                       "If GPS is not enough (in tunnels or on the metro, for example), tap the stop number to start the story by hand.")},
                {"id": "dispositivi", "q": "Which devices does it work on?",
                 "a": "ArcoTour is designed for iPhone, with iOS 15 or later. Version 1.0 has no dedicated iPad version."},
                {"id": "lingua", "q": "How do I change the language?",
                 "a": ("The app starts in Italian if your phone is in Italian, otherwise in English. To change it, use the IT/EN selector at the top right: "
                       "it applies to the interface, the texts and the audio stories.")},
            ]},
            {"id": "posizione", "titolo": "Location and stories", "domande": [
                {"id": "racconti-non-partono", "q": "The stories do not start by themselves when I reach a stop.",
                 "a": ("Check in iOS Settings → Privacy & Security → Location Services → ArcoTour that access is “While Using the App” or “Always” and that “Precise Location” is on. "
                       "Then open the tour and press “Start the tour”: the app must be running (it can be with the screen off or in the background).\n\n"
                       "GPS works badly inside tunnels or on the metro. If the arrival is not recognised, you can always tap the stop number to start the story by hand.")},
                {"id": "schermo-spento", "q": "Does it work with the screen off or the phone in my pocket?",
                 "a": ("Yes. During a tour the app uses location and audio even with the screen locked or in the background, so the story starts even when your phone is in your pocket. "
                       "While location is in use, iOS shows an indicator.")},
                {"id": "posizione-privacy", "q": "Why does ArcoTour use my location? Does it go to anyone?",
                 "a": ("It uses it to start the story when you reach a stop, to show you the public transport stops nearby and to guide you on foot to a stop.\n\n"
                       "GPS coordinates stay on the device: they are not saved, they do not reach us and they are not shared with anyone. "
                        "To display the maps, OpenStreetMap receives the technical data of the request and the requested map area, which may approximately indicate the area where the user is located. You can withdraw the permission at any time in iOS Settings. "
                       "Details in the [privacy policy](@privacy.html).")},
            ]},
            {"id": "mappe-mezzi", "titolo": "Maps and public transport", "domande": [
                {"id": "internet", "q": "Do I need internet?",
                 "a": ("The audio stories, the texts and the photos are inside the app and work without a network. The maps are downloaded from OpenStreetMap: without internet you see the ones already seen, "
                       "and a new area stays empty (the markers and the controls still work). Buying a pass needs internet.")},
                {"id": "mappa-vuota", "q": "The map is empty or in pieces.",
                 "a": ("With a weak connection parts of the map may be missing: the app tells you and tries again by itself a few times. "
                       "Check your connection and reopen the screen. The markers and the controls work anyway.")},
                {"id": "mezzi", "q": "What do the Transport tab and “Take me there” do?",
                 "a": "The Transport tab shows the public transport stops and lines nearby. “Take me there” guides you on foot to the stop you chose."},
            ]},
            {"id": "pass", "titolo": "Rome passes and purchases", "domande": [
                {"id": "come-funzionano-i-pass", "q": "How do the Rome passes work?",
                 "a": ("They are three temporary passes: **Rome 24 hours** ({p24}), **Rome 72 hours** ({p72}) and **Rome Complete** (10 days, that is 240 hours, {p10}). "
                       "One-time payment, no automatic renewal.\n\n"
                       "The time counts from the moment you buy. When the time is up, access to the stories simply ends. The prices shown are for Italy: the final price "
                       "is the one the App Store shows, in your currency.")},
                {"id": "cosa-sblocca", "q": "What does a pass unlock, and what stays free?",
                 "a": ("A pass unlocks the tour stories (“Start the tour”), “Your tour” and the arrival stories. The three passes unlock the same content: only the duration changes. "
                       "A Rome pass does not unlock other cities.\n\n"
                       "The introduction to Rome, the tour sheets (stops, photos and description), the Transport tab and “Take me there” always stay free.")},
                {"id": "durata-scadenza", "q": "How long does a pass last? What happens when it expires?",
                 "a": ("From the moment you buy, for the exact number of hours: 24, 72 or 240 (10 days). The Rome Complete pass lasts 10 days from purchase: it is not permanent or unlimited.\n\n"
                       "Durations do not add up: with several valid passes, the one that expires last applies. For example, 24 hours bought at noon and another 24 hours bought 12 hours later "
                       "end 36 hours after the first purchase, not 48. After a pass expires you can buy a new one whenever you like.")},
                {"id": "abbonamento", "q": "Is it a subscription? Do I have to cancel anything?",
                 "a": "No. The passes are not subscriptions and do not renew by themselves: there is nothing to cancel."},
                {"id": "ripristino-acquisti", "q": "I bought a pass but I cannot see it. How do I restore purchases?",
                 "a": ("Open Profile and look at the pass card: it says “Active pass” and until when it is valid. If it is not there, press “Details” and then “Restore purchases” "
                       "(you need internet and the same Apple account you paid with).\n\n"
                       "If that does not solve it, write to us at {email} with the date of the purchase.")},
                {"id": "rimborsi", "q": "How do I ask for a refund?",
                 "a": ("Refunds are decided by Apple: go to [reportaproblem.apple.com](https://reportaproblem.apple.com). "
                       "A purchase refunded by Apple no longer gives access to the paid content.")},
            ]},
            {"id": "privacy-dati", "titolo": "Privacy and data", "domande": [
                {"id": "account", "q": "Do I have to create an account?",
                 "a": "No. ArcoTour has no accounts and no ads."},
                {"id": "informativa", "q": "Where can I find the privacy policy?",
                 "a": "Inside the app, in Profile → “Privacy policy”, and here: [privacy policy](@privacy.html)."},
                {"id": "crediti-foto", "q": "Who do the photos and the maps belong to?",
                 "a": ("The photos come from Wikimedia Commons, with the authors’ credits and licences; the maps are from OpenStreetMap. "
                       "Credits are in the app (Profile → “Licenses and credits”) and at the bottom of the site’s [home page](@index.html#crediti).")},
            ]},
            {"id": "contenuti", "titolo": "Content", "domande": [
                {"id": "errori", "q": "I found a mistake in a story or a photo.",
                 "a": ("Write to us at {email} with the route, the stop and what is wrong. The voices are synthetic, generated with artificial intelligence, "
                       "and the texts start from facts with a stated source: every report helps us correct.")},
                {"id": "orari-biglietti", "q": "Does the app give museum hours and tickets?",
                 "a": "No: they change often. Always check the official websites of the places you visit."},
            ]},
        ],
    },
    # -------------------------------------------------------------------------------------------------- privacy
    "privacy": {
        "titolo": "Privacy policy · ArcoTour",
        "descrizione": "ArcoTour privacy policy: GPS coordinates stay on the device, no accounts, no ads, no analytics tools.",
        "occhiello": "Privacy",
        "h1": "Privacy policy",
        "sottotitolo": "The ArcoTour app (version 1.0, Rome) and this website",
        "aggiornata_etichetta": "App policy updated on ",
        "indice": "On this page",
        "parte_app": "The app",
        "parte_sito": "This website",
        "sito": {
            "id": "sito-web",
            "titolo": "Cookies, browsing data and email",
            "testo": ("This website does not use cookies, has no analytics or tracking tools and does not load fonts, images or scripts from other services: everything you see is hosted here.\n\n"
                      "The site is hosted on GitHub Pages (GitHub, Inc.). As GitHub explains, when a GitHub Pages site is visited, the visitor’s IP address is logged and stored by GitHub "
                      "for security purposes, whether or not the visitor has a GitHub account. We do not use this data. How GitHub handles it is explained in its "
                      "[privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement) and on the page "
                      "[What is GitHub Pages?](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection).\n\n"
                      "If you email us, we use your address and the content of your message only to reply to you. How long we keep them is explained in the "
                      "“Your rights” section. The support mailbox is hosted by Google (Gmail)."),
        },
    },
    # ------------------------------------------------------------------------------------------------- terms
    "condizioni": {
        "titolo": "Terms of use · ArcoTour",
        "descrizione": "ArcoTour terms of use: how the app works, the Rome passes (24 hours, 72 hours, 10 days, one-time payment, no renewal), restoring purchases and refunds.",
        "occhiello": "Terms",
        "h1": "Terms of use",
        "sottotitolo": "The ArcoTour app (iPhone) and this website",
        "aggiornate": "Last updated: {data}.",
        "sezioni": [
            {"id": "chi-siamo", "titolo": "Who provides the service",
             "testo": ("ArcoTour is provided by {titolare}, {indirizzo}. For any question write to {email}.\n\n"
                       "By downloading or using the app you accept these terms. They apply together with Apple’s "
                       "[standard licence agreement for apps](https://www.apple.com/legal/internet-services/itunes/dev/stdeula/), which covers all apps on the App Store.")},
            {"id": "servizio", "titolo": "What ArcoTour is",
             "testo": ("ArcoTour is an audio guide for iPhone that walks with you through historic centres. Version 1.0 covers Rome: routes on foot and by metro, audio stories in Italian and English, "
                       "maps, public transport stops and the “Your tour” feature. It needs iOS 15 or later; there is no dedicated iPad version.\n\n"
                       "The app is free to download. The tour stories unlock with a paid pass (see “The Rome passes”).")},
            {"id": "uso", "titolo": "Using ArcoTour safely",
             "testo": ("- Walk safely: obey traffic lights and traffic, and stay aware of your surroundings.\n"
                       "- Routes and directions are an aid: they do not replace signs, local rules and common sense.\n"
                       "- Opening hours, tickets and access for the places you visit are not in the app and they change: always check the official websites.\n"
                       "- For the stories to start by themselves you need to allow location, also while the app is in the background; you can withdraw the permission at any time.")},
            {"id": "contenuti", "titolo": "The content",
             "testo": ("The stories are read by synthetic voices, generated with artificial intelligence. The texts start from facts with a stated source and are approved before they become audio, "
                       "but they may contain inaccuracies: if you find any, write to us.\n\n"
                       "The content is for information and cultural purposes.")},
            {"id": "pass", "titolo": "The Rome passes",
             "testo": ("- **What they are.** Three temporary passes for Rome: **Rome 24 hours**, **Rome 72 hours** and **Rome Complete** (10 days, that is 240 hours). They unlock the same content: only the duration changes. "
                       "A Rome pass does not unlock other cities.\n"
                       "- **What they unlock.** The tour stories (“Start the tour”), “Your tour” and the arrival stories. The introduction to Rome, the tour sheets, the Transport tab and “Take me there” stay free.\n"
                       "- **Prices.** {p24}, {p72} and {p10} in Italy. The final price is the one the App Store shows when you buy.\n"
                       "- **One-time payment, no automatic renewal.** The passes are not subscriptions and do not renew by themselves. The Rome Complete pass lasts 10 days from purchase: it is not permanent or unlimited.\n"
                       "- **Duration.** From the moment of the verified purchase, for the exact number of hours. When it expires, access to the stories ends by itself. Durations do not add up: with several valid passes, the one that expires last applies.\n"
                       "- **Payment.** The purchase is made with your Apple account; payment and invoicing are handled by Apple.\n"
                       "- **Restore.** From Profile → “Details” → “Restore purchases”, with the same Apple account (you need internet).\n"
                       "- **Refunds.** Apple handles them ([reportaproblem.apple.com](https://reportaproblem.apple.com)). A refunded purchase no longer gives access to the paid content.")},
            {"id": "recesso", "titolo": "Consumer rights",
             "testo": ("If you are a consumer, the rights the law gives you remain those provided by the applicable rules and by Apple’s terms for App Store purchases, "
                       "including those on withdrawal and digital content. These terms do not limit them.")},
            {"id": "proprieta", "titolo": "Intellectual property and credits",
             "testo": ("The app, the texts, the audio stories and the graphics of ArcoTour belong to its publisher. You may use them personally, through the app, without copying, extracting or redistributing them.\n\n"
                       "The photographs belong to their authors and are used under their licences (Wikimedia Commons); the map data is © OpenStreetMap contributors (ODbL licence). "
                       "Credits are in the app (Profile → “Licenses and credits”) and at the [bottom of the home page](@index.html#crediti).")},
            {"id": "disponibilita", "titolo": "Availability and changes",
             "testo": ("The app and its content may change, be updated or be suspended. The maps depend on OpenStreetMap and on your internet connection; "
                       "positioning depends on your phone’s GPS, which can work badly in tunnels, on the metro or among tall buildings.")},
            {"id": "responsabilita", "titolo": "Liability",
             "testo": ("To the extent permitted by law, ArcoTour is provided as it is, with no guarantee that it is always available or free of errors. "
                       "Nothing in these terms excludes or limits rights and liability that the law does not allow to be excluded or limited.")},
            {"id": "privacy", "titolo": "Privacy",
             "testo": "ArcoTour has no accounts or ads. GPS coordinates stay on the device. To display the maps, OpenStreetMap receives the technical data of the request and the requested map area, which may approximately indicate the area where the user is located. All the details are in the [privacy policy](@privacy.html)."},
            {"id": "modifiche", "titolo": "Changes to these terms",
             "testo": "If these terms change, we update this page and the date above, and we say so in the app before the changes apply to you."},
            {"id": "legge", "titolo": "Governing law",
             "testo": "Italian law applies, without prejudice to the mandatory consumer-protection rules of the country where you live."},
            {"id": "contatti", "titolo": "Contact",
             "testo": "For questions about these terms write to {email}."},
        ],
    },
    # ---------------------------------------------------------------------------------------------------- 404
    "pagina404": {
        "titolo": "Page not found · ArcoTour",
        "h1": "Page not found",
        "testo": "The page you are looking for does not exist or has moved.",
        "link": "Back to the home page",
    },
}
