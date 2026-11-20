"""Tests du lien vers TradingView (20/11/2026), sans réseau. Chaque code ci-dessous a été ouvert sur tradingview.com
le 20/11/2026 : page trouvée (une page inventée, NASDAQ-ZZZQQQ, renvoie « introuvable »).
Lancer depuis le dossier site : .\.venv\Scripts\python.exe -m pytest tests
"""
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SITE))
from notabourse.liens import liens_cours, symbole_tradingview   # noqa: E402

# (symbole Yahoo, code de bourse Yahoo, code TradingView vérifié)
VERIFIES = [("AAPL", "NMS", "NASDAQ-AAPL"), ("BRK-B", "NYQ", "NYSE-BRK.B"), ("CBOE", "BTS", "CBOE-CBOE"),
            ("MC.PA", "PAR", "EURONEXT-MC"), ("ASML.AS", "AMS", "EURONEXT-ASML"), ("A5G.IR", "ISE", "EURONEXT-A5G"),
            ("SAP.DE", "GER", "XETR-SAP"), ("RR.L", "LSE", "LSE-RR."), ("BT-A.L", "LSE", "LSE-BT.A"),
            ("NOVN.SW", "EBS", "SIX-NOVN"), ("VOLV-B.ST", "STO", "OMXSTO-VOLV_B"), ("NOVO-B.CO", "CPH", "OMXCOP-NOVO_B"),
            ("NDA-FI.HE", "HEL", "OMXHEX-NDA_FI"), ("0700.HK", "HKG", "HKEX-700"), ("0003.HK", "HKG", "HKEX-3"),
            ("7203.T", "JPX", "TSE-7203"), ("005930.KS", "KSC", "KRX-005930"), ("000250.KQ", "KOE", "KRX-000250"),
            ("2330.TW", "TAI", "TWSE-2330"), ("5274.TWO", "TWO", "TPEX-5274"), ("601398.SS", "SHH", "SSE-601398"),
            ("002594.SZ", "SHZ", "SZSE-002594"), ("HDFCBANK.NS", "NSI", "NSE-HDFCBANK"), ("BBD-B.TO", "TOR", "TSX-BBD.B"),
            ("PETR4.SA", "SAO", "BMFBOVESPA-PETR4"), ("GULF-R.BK", "SET", "SET-GULF"), ("2222.SR", "SAU", "TADAWUL-2222"),
            ("GGAL.BA", "BUE", "BCBA-GGAL"), ("PAMPA.SN", "SGO", "BCS-PAMPA"), ("QNBK.QA", "DOH", "QSE-QNBK")]


def test_codes_verifies():
    for symbole, bourse, attendu in VERIFIES:
        assert symbole_tradingview(symbole, bourse) == attendu, symbole


def test_deux_liens_dans_la_langue():
    """Yahoo Finance (débutant) puis TradingView (expérimenté), pages dans la langue du site."""
    assert liens_cours("MC.PA", "PAR", "fr") == [
        ("https://fr.finance.yahoo.com/quote/MC.PA/", "Yahoo Finance", "debutant"),
        ("https://fr.tradingview.com/symbols/EURONEXT-MC/", "TradingView", "experimente")]
    assert liens_cours("MC.PA", "PAR", "en")[1] == (
        "https://www.tradingview.com/symbols/EURONEXT-MC/", "TradingView", "experimente")


def test_bourse_inconnue_yahoo_seul():
    """Mexico (pages TradingView introuvables) et bourses hors de la table : Yahoo Finance seul, même symbole."""
    assert liens_cours("WALMEX.MX", "MEX", "fr") == [
        ("https://fr.finance.yahoo.com/quote/WALMEX.MX/", "Yahoo Finance", "debutant")]
    assert liens_cours("1155.KL", "KLS", "en") == [
        ("https://finance.yahoo.com/quote/1155.KL/", "Yahoo Finance", "debutant")]


def test_symbole_bizarre_aucun_lien():
    assert liens_cours("AAPL)](javascript:x", "NMS", "fr") == []
    assert liens_cours("", "NMS", "fr") == []
