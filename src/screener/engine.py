import yaml
import pandas as pd


def load_config():
    with open("config/screener_config.yaml", "r") as f:
        return yaml.safe_load(f)


def add_composite_score(df):
    score = (
        df["return_on_equity_pct"].fillna(0) * 0.35
        + df["net_profit_margin_pct"].fillna(0) * 0.25
        + df["asset_turnover"].fillna(0) * 0.15
        + (100 - df["debt_to_equity"].fillna(0) * 10) * 0.25
    )

    df["composite_quality_score"] = score.round(2)

    return df


def apply_filters(df):

    config = load_config()

    filters = config["filters"]

    if "return_on_equity_pct" in df.columns:
        df = df[
            df["return_on_equity_pct"] >= filters["roe_min"]
        ]

    if "debt_to_equity" in df.columns:
        df = df[
            df["debt_to_equity"] <= filters["de_max"]
        ]

    if "free_cash_flow" in df.columns:
        df = df[
            df["free_cash_flow"] >= filters["fcf_min"]
        ]

    df = add_composite_score(df)

    df = df.sort_values(
        "composite_quality_score",
        ascending=False
    )

    return df.reset_index(drop=True)