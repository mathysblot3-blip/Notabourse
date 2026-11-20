"""Lien vers la page de la société sur TradingView, sous la courbe du cours [M] 20/11/2026.

TradingView nomme une action « BOURSE-SYMBOLE » (EURONEXT-MC pour LVMH, NASDAQ-AAPL pour Apple). Yahoo, d'où viennent
les données du site, donne un code de bourse (PAR, NMS...) et un symbole avec suffixe (MC.PA). Ce fichier traduit
l'un en l'autre. Chaque bourse de la table a été vérifiée sur les pages publiques de TradingView le 20/11/2026 [R]
(tests/test_liens.py garde les exemples vérifiés). Bourse absente de la table : lien vers Yahoo Finance, toujours
juste puisque le symbole est le même. Le lien n'envoie rien tant que le visiteur ne clique pas.
Fonctions sans Streamlit ni réseau : testables avec pytest.
"""
import re   # nettoyage du symbole

# Code de bourse de Yahoo -> préfixe de TradingView
BOURSES_TRADINGVIEW = {
    "NYQ": "NYSE", "NMS": "NASDAQ", "NGM": "NASDAQ", "NCM": "NASDAQ", "ASE": "AMEX", "PCX": "AMEX", "BTS": "CBOE",
    "TOR": "TSX", "SAO": "BMFBOVESPA", "SGO": "BCS", "BUE": "BCBA",   # Mexico (MEX) absent : pages BMV introuvables
                                                                    # (GMEXICOB, AMXB), repli sur Yahoo [R] 20/11
    "PAR": "EURONEXT", "AMS": "EURONEXT", "BRU": "EURONEXT", "LIS": "EURONEXT", "ISE": "EURONEXT",
    "GER": "XETR", "LSE": "LSE", "EBS": "SIX", "MIL": "MIL", "MCE": "BME", "STO": "OMXSTO", "CPH": "OMXCOP",
    "HEL": "OMXHEX", "OSL": "OSL", "VIE": "VIE", "WSE": "GPW", "ATH": "ATHEX", "IST": "BIST",
    "JPX": "TSE", "SHH": "SSE", "SHZ": "SZSE", "HKG": "HKEX", "TAI": "TWSE", "TWO": "TPEX", "KSC": "KRX",
    "KOE": "KRX", "NSI": "NSE", "ASX": "ASX", "NZE": "NZX", "SES": "SGX", "JKT": "IDX", "SET": "SET",
    "TLV": "TASE", "SAU": "TADAWUL", "DOH": "QSE", "JNB": "JSE",
}
URL_TRADINGVIEW = {"fr": "https://fr.tradingview.com/symbols/{code}/", "en": "https://www.tradingview.com/symbols/{code}/"}
URL_YAHOO = {"fr": "https://fr.finance.yahoo.com/quote/{symbole}/", "en": "https://finance.yahoo.com/quote/{symbole}/"}
US = {"NYQ", "NMS", "NGM", "NCM", "ASE", "PCX", "BTS"}                        # bourses américaines : pas de suffixe


def symbole_tradingview(symbole, bourse):
    """« MC.PA » + « PAR » -> « EURONEXT-MC » ; None si la bourse n'est pas dans la table."""
    prefixe = BOURSES_TRADINGVIEW.get(bourse)
    if prefixe is None or not symbole:
        return None
    s = symbole if bourse in US else symbole.rsplit(".", 1)[0]                # suffixe de Yahoo retiré (.PA, .L...)
    if bourse == "HKG":
        s = s.lstrip("0") or "0"                                              # 0700 -> 700
    elif bourse in ("STO", "CPH", "HEL"):
        s = s.replace("-", "_")                                               # VOLV-B -> VOLV_B
    elif bourse == "SET":
        s = re.sub(r"-R$", "", s)                                             # GULF-R (titre sans droit de vote) -> GULF
    else:
        s = s.replace("-", ".")                                               # BRK-B -> BRK.B, BT-A -> BT.A
    if bourse == "LSE" and len(s) <= 2:
        s += "."                                                              # RR -> RR. (code de Londres)
    if not re.fullmatch(r"[A-Z0-9._&]+", s):                                  # caractère inattendu : pas de lien
        return None
    return f"{prefixe}-{s}"


def lien_cours(symbole, bourse, langue):
    """(adresse, nom du site) du lien sous la courbe : TradingView si la bourse est connue, sinon Yahoo Finance."""
    lg = "fr" if langue == "fr" else "en"
    code = symbole_tradingview(symbole, bourse)
    if code:
        return URL_TRADINGVIEW[lg].format(code=code), "TradingView"
    if symbole and re.fullmatch(r"[A-Za-z0-9.\-^=]+", symbole):              # symbole de Yahoo seulement
        return URL_YAHOO[lg].format(symbole=symbole), "Yahoo Finance"
    return None, None
