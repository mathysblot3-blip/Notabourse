"""Pays d'une société : nom en français et en anglais, et drapeau [M] 20/11/2026.

Yahoo donne le pays du siège en anglais (« United States », « Ireland »...). Ce fichier le traduit en code ISO à deux
lettres (« us », « ie »), puis en nom français ou anglais. Le drapeau est une petite image PNG rangée dans
static/drapeaux/<code>.png (images de flagcdn.com, drapeaux du domaine public), servie par le site lui-même : le
navigateur du visiteur ne contacte aucun autre site. Script de téléchargement : reference/telecharger_drapeaux.py.
Fonctions sans Streamlit : testables avec pytest.
"""
from pathlib import Path   # chemins de fichiers

DOSSIER_DRAPEAUX = Path(__file__).resolve().parents[1] / "static" / "drapeaux"   # site/static/drapeaux
DOSSIER_TABLEAU = DOSSIER_DRAPEAUX.parent / "drapeaux_tableau"                # mêmes drapeaux, avec du vide autour
ADRESSE_DRAPEAU = "app/static/drapeaux_tableau/{code}.png"                    # adresse vue par le navigateur (tableau)

# Nom anglais de Yahoo -> (code ISO, nom français, nom anglais). Les 40 pays du classement, puis les sièges sociaux
# fréquents des sociétés cotées (paradis fiscaux compris : Bermudes, îles Caïmans, Jersey...).
PAYS_YAHOO = {
    "United States": ("us", "États-Unis", "United States"), "Canada": ("ca", "Canada", "Canada"),
    "Brazil": ("br", "Brésil", "Brazil"), "Mexico": ("mx", "Mexique", "Mexico"),
    "Argentina": ("ar", "Argentine", "Argentina"), "Chile": ("cl", "Chili", "Chile"),
    "France": ("fr", "France", "France"), "Germany": ("de", "Allemagne", "Germany"),
    "United Kingdom": ("gb", "Royaume-Uni", "United Kingdom"), "Switzerland": ("ch", "Suisse", "Switzerland"),
    "Netherlands": ("nl", "Pays-Bas", "Netherlands"), "Sweden": ("se", "Suède", "Sweden"),
    "Italy": ("it", "Italie", "Italy"), "Spain": ("es", "Espagne", "Spain"), "Denmark": ("dk", "Danemark", "Denmark"),
    "Norway": ("no", "Norvège", "Norway"), "Finland": ("fi", "Finlande", "Finland"),
    "Belgium": ("be", "Belgique", "Belgium"), "Austria": ("at", "Autriche", "Austria"),
    "Portugal": ("pt", "Portugal", "Portugal"), "Ireland": ("ie", "Irlande", "Ireland"),
    "Poland": ("pl", "Pologne", "Poland"), "Greece": ("gr", "Grèce", "Greece"), "Turkey": ("tr", "Turquie", "Turkey"),
    "Türkiye": ("tr", "Turquie", "Turkey"), "Japan": ("jp", "Japon", "Japan"),
    "South Korea": ("kr", "Corée du Sud", "South Korea"), "Korea": ("kr", "Corée du Sud", "South Korea"),
    "Hong Kong": ("hk", "Hong Kong", "Hong Kong"), "China": ("cn", "Chine", "China"),
    "Taiwan": ("tw", "Taïwan", "Taiwan"), "India": ("in", "Inde", "India"), "Australia": ("au", "Australie", "Australia"),
    "New Zealand": ("nz", "Nouvelle-Zélande", "New Zealand"), "Singapore": ("sg", "Singapour", "Singapore"),
    "Indonesia": ("id", "Indonésie", "Indonesia"), "Thailand": ("th", "Thaïlande", "Thailand"),
    "Malaysia": ("my", "Malaisie", "Malaysia"), "South Africa": ("za", "Afrique du Sud", "South Africa"),
    "Israel": ("il", "Israël", "Israel"), "Saudi Arabia": ("sa", "Arabie saoudite", "Saudi Arabia"),
    "Qatar": ("qa", "Qatar", "Qatar"),
    # Sièges fréquents hors des 40 pays du classement
    "Bermuda": ("bm", "Bermudes", "Bermuda"), "Cayman Islands": ("ky", "Îles Caïmans", "Cayman Islands"),
    "Jersey": ("je", "Jersey", "Jersey"), "Guernsey": ("gg", "Guernesey", "Guernsey"),
    "Isle of Man": ("im", "Île de Man", "Isle of Man"), "Luxembourg": ("lu", "Luxembourg", "Luxembourg"),
    "Monaco": ("mc", "Monaco", "Monaco"), "Liechtenstein": ("li", "Liechtenstein", "Liechtenstein"),
    "Gibraltar": ("gi", "Gibraltar", "Gibraltar"), "Cyprus": ("cy", "Chypre", "Cyprus"), "Malta": ("mt", "Malte", "Malta"),
    "Iceland": ("is", "Islande", "Iceland"), "Czech Republic": ("cz", "Tchéquie", "Czech Republic"),
    "Czechia": ("cz", "Tchéquie", "Czech Republic"), "Hungary": ("hu", "Hongrie", "Hungary"),
    "Romania": ("ro", "Roumanie", "Romania"), "Bulgaria": ("bg", "Bulgarie", "Bulgaria"),
    "Slovakia": ("sk", "Slovaquie", "Slovakia"), "Slovenia": ("si", "Slovénie", "Slovenia"),
    "Croatia": ("hr", "Croatie", "Croatia"), "Serbia": ("rs", "Serbie", "Serbia"), "Estonia": ("ee", "Estonie", "Estonia"),
    "Latvia": ("lv", "Lettonie", "Latvia"), "Lithuania": ("lt", "Lituanie", "Lithuania"),
    "Ukraine": ("ua", "Ukraine", "Ukraine"), "Russia": ("ru", "Russie", "Russia"), "Georgia": ("ge", "Géorgie", "Georgia"),
    "Kazakhstan": ("kz", "Kazakhstan", "Kazakhstan"), "Mongolia": ("mn", "Mongolie", "Mongolia"),
    "United Arab Emirates": ("ae", "Émirats arabes unis", "United Arab Emirates"),
    "Kuwait": ("kw", "Koweït", "Kuwait"), "Bahrain": ("bh", "Bahreïn", "Bahrain"), "Oman": ("om", "Oman", "Oman"),
    "Jordan": ("jo", "Jordanie", "Jordan"), "Egypt": ("eg", "Égypte", "Egypt"), "Morocco": ("ma", "Maroc", "Morocco"),
    "Nigeria": ("ng", "Nigeria", "Nigeria"), "Kenya": ("ke", "Kenya", "Kenya"), "Ghana": ("gh", "Ghana", "Ghana"),
    "Mauritius": ("mu", "Maurice", "Mauritius"), "Zambia": ("zm", "Zambie", "Zambia"),
    "Botswana": ("bw", "Botswana", "Botswana"), "Philippines": ("ph", "Philippines", "Philippines"),
    "Vietnam": ("vn", "Viêt Nam", "Vietnam"), "Pakistan": ("pk", "Pakistan", "Pakistan"),
    "Bangladesh": ("bd", "Bangladesh", "Bangladesh"), "Sri Lanka": ("lk", "Sri Lanka", "Sri Lanka"),
    "Macau": ("mo", "Macao", "Macau"), "Macao": ("mo", "Macao", "Macau"), "Cambodia": ("kh", "Cambodge", "Cambodia"),
    "Papua New Guinea": ("pg", "Papouasie-Nouvelle-Guinée", "Papua New Guinea"),
    "Colombia": ("co", "Colombie", "Colombia"), "Peru": ("pe", "Pérou", "Peru"), "Uruguay": ("uy", "Uruguay", "Uruguay"),
    "Panama": ("pa", "Panama", "Panama"), "Costa Rica": ("cr", "Costa Rica", "Costa Rica"),
    "Bahamas": ("bs", "Bahamas", "Bahamas"), "Puerto Rico": ("pr", "Porto Rico", "Puerto Rico"),
    "Curacao": ("cw", "Curaçao", "Curaçao"), "Curaçao": ("cw", "Curaçao", "Curaçao"),
    "British Virgin Islands": ("vg", "Îles Vierges britanniques", "British Virgin Islands"),
    "Marshall Islands": ("mh", "Îles Marshall", "Marshall Islands"), "Liberia": ("lr", "Liberia", "Liberia"),
    "Falkland Islands": ("fk", "Îles Malouines", "Falkland Islands"),
}


def pays_de(nom_yahoo, langue):
    """(code ISO, nom dans la langue) du pays donné par Yahoo ; (None, nom de Yahoo) s'il est inconnu ; (None, None)
    s'il manque."""
    if not nom_yahoo or not isinstance(nom_yahoo, str):
        return None, None
    trouve = PAYS_YAHOO.get(nom_yahoo.strip())
    if trouve is None:
        return None, nom_yahoo.strip()                                        # pays rare : nom anglais, sans drapeau
    code, fr, en = trouve
    return code, fr if langue == "fr" else en


def a_un_drapeau(code):
    """Vrai si l'image du drapeau de ce code est bien rangée dans static/drapeaux."""
    return bool(code) and (DOSSIER_DRAPEAUX / f"{code}.png").exists()


def adresse_drapeau(code):
    """Adresse de l'image du drapeau pour le tableau du classement (servie par le site), ou None s'il n'y en a pas."""
    return ADRESSE_DRAPEAU.format(code=code) if (DOSSIER_TABLEAU / f"{code}.png").exists() else None


def codes_utiles():
    """Tous les codes de pays du site : ceux de PAYS_YAHOO (les 40 du classement y sont)."""
    return sorted({code for code, _, _ in PAYS_YAHOO.values()})
