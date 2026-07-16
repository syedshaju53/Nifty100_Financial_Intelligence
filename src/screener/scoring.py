import pandas as pd


def normalize(series, inverse=False):

    s = series.fillna(series.median())

    minimum = s.min()
    maximum = s.max()

    if maximum == minimum:
        score = pd.Series([50] * len(s), index=s.index)
    else:
        score = ((s - minimum) / (maximum - minimum)) * 100

    if inverse:
        score = 100 - score

    return score


def calculate_composite_score(df):

    data = df.copy()

    # ----------------------------
    # Profitability (35%)
    # ----------------------------

    roe = normalize(data["return_on_equity_pct"])
    npm = normalize(data["net_profit_margin_pct"])
    opm = normalize(data["operating_profit_margin_pct"])

    profitability = (
        roe * 0.15 +
        npm * 0.10 +
        opm * 0.10
    )

    # ----------------------------
    # Cash Flow (30%)
    # ----------------------------

    fcf = normalize(data["free_cash_flow"])

    cash_quality = (
        fcf * 0.30
    )

    # ----------------------------
    # Growth (20%)
    # ----------------------------

    revenue = normalize(data["revenue_cagr_5yr"])
    pat = normalize(data["pat_cagr_5yr"])

    growth = (
        revenue * 0.10 +
        pat * 0.10
    )

    # ----------------------------
    # Leverage (15%)
    # ----------------------------

    de = normalize(data["debt_to_equity"], inverse=True)

    icr = normalize(data["interest_coverage"])

    leverage = (
        de * 0.10 +
        icr * 0.05
    )

    data["composite_quality_score"] = (
        profitability +
        cash_quality +
        growth +
        leverage
    ).round(2)

    return data