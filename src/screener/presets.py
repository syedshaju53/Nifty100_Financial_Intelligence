import pandas as pd


def _latest_per_company(df):
    data = df.copy()

    # If company_id is unavailable, treat the input as already
    # representing the latest/current records.
    if "company_id" not in data.columns:
        return data

    if "_year_num" in data.columns:
        data = data.sort_values("_year_num")

    data = data.drop_duplicates("company_id", keep="last")

    return data


def quality_compounder(df):
    """Identify companies with strong returns, low leverage, FCF and growth."""
    data = _latest_per_company(df)

    return data[
        (data["return_on_equity_pct"] > 15)
        & (data["debt_to_equity"] < 1.0)
        & (data["free_cash_flow"] > 0)
        & (data["revenue_cagr_5yr"] > 10)
    ]


def value_pick(df):
    """Identify attractively valued companies with moderate leverage."""
    data = _latest_per_company(df)

    return data[
        (data["pe_ratio"] < 20)
        & (data["pb_ratio"] < 3.0)
        & (data["debt_to_equity"] < 2.0)
        & (data["dividend_yield_pct"] > 1)
    ]


def growth_accelerator(df):
    """Identify companies with strong earnings and revenue growth."""
    data = _latest_per_company(df)

    return data[
        (data["pat_cagr_5yr"] > 20)
        & (data["revenue_cagr_5yr"] > 15)
        & (data["debt_to_equity"] < 2.0)
    ]


def dividend_champion(df):
    """Identify companies with sustainable dividends and positive FCF."""
    data = _latest_per_company(df)

    return data[
        (data["dividend_yield_pct"] > 2)
        & (data["dividend_payout"] < 80)
        & (data["free_cash_flow"] > 0)
    ]


def debt_free_bluechip(df):
    """Identify debt-free companies with strong returns and sales."""
    data = _latest_per_company(df)

    return data[
        (data["debt_to_equity"] == 0)
        & (data["return_on_equity_pct"] > 12)
        & (data["sales"] > 5000)
    ]


def turnaround_watch(df):
    """Identify companies showing growth, positive FCF and declining leverage."""
    data = df.copy()

    if "year" in data.columns:
        data["_year_num"] = (
            data["year"]
            .astype(str)
            .str.extract(r"(\d{4})")[0]
            .astype(float)
        )

        data = data.sort_values(["company_id", "_year_num"])

    data["prev_de"] = data.groupby("company_id")["debt_to_equity"].shift(1)

    data = data[
        (data["revenue_cagr_5yr"] > 10)
        & (data["free_cash_flow"] > 0)
        & (data["debt_to_equity"] < data["prev_de"])
    ]

    return data.drop(columns=["_year_num"], errors="ignore")
