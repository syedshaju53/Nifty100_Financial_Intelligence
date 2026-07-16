import pandas as pd


def quality_compounder(df):
    return df[
        (df["return_on_equity_pct"] > 15) &
        (df["debt_to_equity"] < 1.0) &
        (df["free_cash_flow"] > 0) &
        (df["revenue_cagr_5yr"] > 10)
    ]


def value_pick(df):
    return df[
        (df["pe_ratio"] < 20) &
        (df["pb_ratio"] < 3.0) &
        (df["debt_to_equity"] < 2.0) &
        (df["dividend_yield_pct"] > 1)
    ]


def growth_accelerator(df):
    return df[
        (df["pat_cagr_5yr"] > 20) &
        (df["revenue_cagr_5yr"] > 15) &
        (df["debt_to_equity"] < 2.0)
    ]


def dividend_champion(df):
    return df[
        (df["dividend_yield_pct"] > 2) &
        (df["dividend_payout"] < 80) &
        (df["free_cash_flow"] > 0)
    ]


def debt_free_bluechip(df):
    return df[
        (df["debt_to_equity"] == 0) &
        (df["return_on_equity_pct"] > 12) &
        (df["sales"] > 5000)
    ]


def turnaround_watch(df):

    df = df.copy()

    df["prev_de"] = df.groupby("company_id")["debt_to_equity"].shift(1)

    return df[
        (df["revenue_cagr_5yr"] > 10) &
        (df["free_cash_flow"] > 0) &
        (df["debt_to_equity"] < df["prev_de"])
    ]