# NotaBourse : le site

Site web public où l'on tape le nom d'une entreprise cotée et où l'on obtient sa **note NotaBourse** (étoiles, note sur
100, note M) avec le détail du calcul. La note vient du travail de recherche de Mathys Blot (formule C8) ; le site
l'applique aux données de Yahoo Finance. **Ceci n'est pas un conseil en investissement.**

Réalisé par Mathys Blot. État : en construction (étape d sur g : interface).

## Ce que contient ce dossier

| Fichier ou dossier | Rôle |
|---|---|
| `notabourse/` | Le calcul, sans interface : données (`sources.py`), classement (`classement.py`), ratios (`ratios.py`), composantes (`composantes.py`), garde-fou (`garde_fou.py`), note (`note.py`), enchaînement (`calcul.py`), constantes (`constantes.py`), contenu de la fiche (`fiche.py`), phrases simples (`phrases.py`), mise en forme des nombres (`formats.py`) |
| `app.py`, `vues/`, `traductions/` | L'interface : navigation (`app.py`), page de recherche et fiche (`vues/recherche.py`), page Méthode (`vues/methode.py`), textes en français et en anglais (`traductions/`, dont la page Méthode : `methode_fr.md` et `methode_en.md`, à corriger directement) |
| `reference/` | Fichiers de référence du S&P 500 (`ff12_sic.csv` : table des 12 secteurs de Fama et French) |
| `tests/` | Tests automatiques (`test_calcul.py` pour les calculs, `test_phrases.py` pour les phrases et les textes) et cas de test lus sur Internet (`cas_de_test.py`, résultat dans `cas_de_test.md`) |
| `CHOIX.md` | Tous les choix de conception, avec leur nature (repris de la recherche, avis de Mathys, proposé, résultat de test) |
| `requirements.txt` | Bibliothèques Python et leurs versions |

## Installation sur un PC Windows (une seule fois)

Ouvrir PowerShell dans le dossier `site`, puis taper ces commandes une par une.

```powershell
py -3.12 -m venv .venv
```
Crée un « environnement virtuel » : un dossier `.venv` qui contient un Python 3.12 réservé au site, pour ne pas mélanger
ses bibliothèques avec celles de la recherche.

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```
Met à jour `pip`, le programme qui installe les bibliothèques.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
Installe toutes les bibliothèques listées dans `requirements.txt`, aux versions indiquées (plusieurs minutes).

## Secret à créer soi-même (jamais dans le dépôt)

La SEC demande à chaque programme de s'identifier. Créer le fichier `.streamlit/secrets.toml` (il est ignoré par git)
avec une seule ligne, en remplaçant par son nom et son adresse :

```toml
SEC_USER_AGENT = "Prénom Nom adresse@exemple.com"
```

## Lancer les tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```
Lance les tests automatiques (sans Internet) : chaque point vert est un test réussi.

```powershell
.\.venv\Scripts\python.exe tests\cas_de_test.py
```
Calcule les ratios des sociétés du cahier des charges avec les données Yahoo du jour et écrit `tests/cas_de_test.md`.

## Construire la référence S&P 500

```powershell
.\.venv\Scripts\python.exe reference\construire_reference.py
```
Télécharge les données des ~500 membres du S&P 500 (liste de Wikipédia), calcule leurs ratios et leurs notes entre eux,
et écrit `reference/reference.parquet` (ratios dérivés seulement), `reference/croissances.parquet` et
`reference/membres_sp500.csv`. Environ 40 minutes ; si le calcul est interrompu, le relancer reprend où il s'était
arrêté (cache dans `cache/`). Le robot de GitHub le relancera chaque semaine (étape f).

```powershell
.\.venv\Scripts\python.exe reference\construire_correspondance.py
```
Construit `reference/correspondance_yahoo.csv` (industrie Yahoo vers groupe et secteur, pour les sociétés qui ne
déposent pas à la SEC) et la liste des cas à trancher `reference/correspondance_yahoo.md`. Lancé une fois, puis figé.

## Sources des données

Yahoo Finance (bibliothèque yfinance, non officielle, sans garantie), SEC (codes SIC et dates de dépôt), Wikipédia (liste
des membres du S&P 500), Kenneth French (table des secteurs). Le site n'affiche les données que d'une société à la fois.
