"""Mise en forme des nombres pour l'affichage (français ou anglais), sans Streamlit : utilisée par les pages du site
(vues/) et par les phrases simples de la fiche (phrases.py), et donc testable avec pytest."""
import pandas as pd   # valeurs manquantes et dates


def manquant(x):
    """Vrai si la valeur est absente (None ou NaN)."""
    return x is None or pd.isna(x)


def nombre(x, langue_, decimales=1):
    """Nombre lisible : 1 234,5 en français, 1,234.5 en anglais ; « - » si manquant."""
    if manquant(x):
        return "-"
    texte = f"{x:,.{decimales}f}"                                             # 1,234.5 (format anglais)
    return texte.replace(",", " ").replace(".", ",") if langue_ == "fr" else texte


def pct(x, langue_, decimales=1):
    """Pourcentage lisible : 12,3 % en français, 12.3% en anglais ; « - » si manquant."""
    if manquant(x):
        return "-"
    texte = f"{100 * x:.{decimales}f}"                                        # 0,123 -> « 12.3 »
    return texte.replace(".", ",") + " %" if langue_ == "fr" else texte + "%"


def pct_signe(x, langue_, decimales=1):
    """Pourcentage avec son signe : +12,3 % ou -4,0 %."""
    if manquant(x):
        return "-"
    return ("+" if x > 0 else "") + pct(x, langue_, decimales)               # le « - » est déjà mis par pct


def dollars(x, langue_):
    """Montant en dollars : 5 013 Md$ en français, $5,013bn en anglais."""
    if manquant(x):
        return "-"
    if abs(x) >= 1e9:                                                         # milliards
        return f"{nombre(x / 1e9, langue_, 0)} Md$" if langue_ == "fr" else f"${nombre(x / 1e9, langue_, 0)}bn"
    return f"{nombre(x / 1e6, langue_, 0)} M$" if langue_ == "fr" else f"${nombre(x / 1e6, langue_, 0)}m"   # millions


def date(d, langue_):
    """Date lisible : 30/09/2025 en français, 2025-09-30 en anglais."""
    if manquant(d):
        return "-"
    d = pd.Timestamp(d)
    return d.strftime("%d/%m/%Y") if langue_ == "fr" else d.strftime("%Y-%m-%d")
