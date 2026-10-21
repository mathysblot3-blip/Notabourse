// Vérification de l'affichage (20/10/2026), à refaire après chaque changement de visuel.
// Mode d'emploi : ouvrir le site (en local : http://localhost:8501), appuyer sur F12, onglet « Console », coller tout ce
// fichier puis Entrée. Le résultat s'affiche en tableau : chaque ligne doit indiquer « oui ».
// Pour tester plusieurs tailles d'écran : dans les outils F12, bouton « téléphone / tablette » (Ctrl+Maj+M), choisir
// une taille, recharger la page, recoller ce fichier. Tailles testées le 20/10/2026 : 360 x 640, 768 x 900,
// 1280 x 560, 1366 x 650, 1920 x 950.
(() => {
  const resultats = {};                                                       // une ligne par contrôle
  const entete = document.querySelector('[data-testid="stHeader"]');          // barre du haut de Streamlit
  const basEntete = entete ? entete.getBoundingClientRect().bottom : 0;       // elle cache ce qui passe dessous
  const titre = document.querySelector('.ba-bandeau') || document.querySelector('h1');   // titre de la page
  resultats["Titre entièrement sous la barre du haut"] = titre && titre.getBoundingClientRect().top >= basEntete;
  // Aucun élément ne dépasse à droite (sauf la bande défilante, faite pour, et les tableaux, qui défilent dans leur cadre)
  const deborde = [...document.querySelectorAll('[data-testid="stMain"] *')].filter(x =>
    !x.closest('.ba-bande') && !x.closest('[data-testid="stTable"], [data-testid="stDataFrame"]') &&
    x.getBoundingClientRect().right > innerWidth + 1);
  resultats["Rien ne dépasse à droite"] = deborde.length === 0 && document.documentElement.scrollWidth <= innerWidth;
  // Accueil : le texte de présentation se lit en entier sans faire défiler
  const presentation = [...document.querySelectorAll('[data-testid="stMarkdownContainer"] p')]
    .find(p => p.innerText.startsWith('Bourse à lunettes'));
  if (document.querySelector('.ba-bandeau') && presentation) {
    resultats["Présentation visible sans faire défiler"] = presentation.getBoundingClientRect().bottom <= innerHeight;
  }
  // Fiche : les chiffres 0, 50 et 100 de la jauge sont entiers (dans le cadre du graphique)
  const jauge = document.querySelector('.js-plotly-plot');
  if (jauge) {
    const cadre = jauge.getBoundingClientRect();
    resultats["Chiffres de la jauge entiers"] = [...jauge.querySelectorAll('text')]
      .filter(x => ['0', '50', '100'].includes(x.textContent.trim()))
      .every(x => { const r = x.getBoundingClientRect();
        return r.left >= cadre.left && r.right <= cadre.right && r.top >= cadre.top && r.bottom <= cadre.bottom; });
  }
  const lignes = Object.entries(resultats).map(([controle, ok]) => ({controle, ok: ok ? "oui" : "NON"}));
  console.table(lignes);                                                      // tableau dans la console
  return `${innerWidth} x ${innerHeight} : ` + (lignes.every(l => l.ok === "oui") ? "tout est bon" : "à corriger");
})();
