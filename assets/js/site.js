/* ArcoTour — sito. Due piccoli aiuti; il sito funziona anche senza JavaScript (il menu resta aperto e le domande si aprono a mano). */
(function () {
  var d = document;

  // menu dei telefoni: si apre e si chiude con il pulsante «Menu» (anche con Esc) e si chiude dopo un tocco su un collegamento
  var bottone = d.querySelector('.menu-toggle');
  var nav = d.getElementById('menu-principale');
  if (bottone && nav) {
    var chiudi = function () {
      nav.classList.remove('aperto');
      bottone.setAttribute('aria-expanded', 'false');
    };
    bottone.addEventListener('click', function () {
      var aperto = nav.classList.toggle('aperto');
      bottone.setAttribute('aria-expanded', aperto ? 'true' : 'false');
    });
    d.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('aperto')) { chiudi(); bottone.focus(); }
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest && e.target.closest('a')) { chiudi(); }
    });
  }

  // un collegamento come support.html#ripristino-acquisti apre da solo la domanda giusta
  function apriDomanda() {
    var id = decodeURIComponent(location.hash.replace(/^#/, ''));
    if (!id) { return; }
    var el = d.getElementById(id);
    if (!el) { return; }
    var det = el.tagName === 'DETAILS' ? el : (el.closest ? el.closest('details') : null);
    if (det) { det.open = true; }
  }
  window.addEventListener('hashchange', apriDomanda);
  apriDomanda();
})();
