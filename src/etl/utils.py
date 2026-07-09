import pandas as pd


def normalize_ticker(ticker):
    """
    Remove spaces and convert ticker to uppercase.
    """

    if pd.isna(ticker):
        return None

    return str(ticker).strip().upper()


def normalize_year(value):
    """
    Convert values like Mar-23 to 2023-03.
    """

    if pd.isna(value):
        return None

    try:
        return pd.to_datetime(value).strftime("%Y-%m")
    except Exception:
        return value