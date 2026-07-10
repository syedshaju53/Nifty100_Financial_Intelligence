import pandas as pd
def normalize_ticker(ticker):
    """
    Normalize stock ticker values.
    """

    if pd.isna(ticker):
        return None

    return str(ticker).strip().upper()

def normalize_year(value):
    """
    Convert different year formats into YYYY-MM.
    """

    if pd.isna(value):
        return None

    try:
        return pd.to_datetime(value).strftime("%Y-%m")
    except Exception:
        return value