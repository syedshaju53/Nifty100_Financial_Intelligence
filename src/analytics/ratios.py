

from typing import Optional


def net_profit_margin(net_profit: float, sales: float) -> Optional[float]:
    """
    Net Profit Margin = (Net Profit / Sales) × 100
    """
    if sales == 0:
        return None
    return round((net_profit / sales) * 100, 2)


def operating_profit_margin(operating_profit: float, sales: float) -> Optional[float]:
    """
    Operating Profit Margin = (Operating Profit / Sales) × 100
    """
    if sales == 0:
        return None
    return round((operating_profit / sales) * 100, 2)


def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:
    """
    ROE = Net Profit / (Equity Capital + Reserves) × 100
    """

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)


def return_on_capital_employed(
    ebit: float,
    equity_capital: float,
    reserves: float,
    borrowings: float
) -> Optional[float]:
    """
    ROCE = EBIT / (Equity + Reserves + Borrowings) × 100
    """

    capital = equity_capital + reserves + borrowings

    if capital <= 0:
        return None

    return round((ebit / capital) * 100, 2)


def return_on_assets(
    net_profit: float,
    total_assets: float
) -> Optional[float]:
    """
    ROA = Net Profit / Total Assets × 100
    """

    if total_assets == 0:
        return None

    return round((net_profit / total_assets) * 100, 2)

def validate_operating_profit_margin(
    operating_profit: float,
    sales: float,
    source_opm: float
):
    """
    Compare computed OPM with source OPM.
    Returns (computed_opm, mismatch_flag)
    """

    computed = operating_profit_margin(operating_profit, sales)

    if computed is None:
        return None, False

    mismatch = abs(computed - source_opm) > 1

    return computed, mismatch

def roce_benchmark(roce: float, sector: str):
    """
    ROCE Benchmark

    Financial companies:
        ROCE is compared relative to peers.

    Other sectors:
        >= 15% -> Good
        10-15% -> Average
        <10% -> Poor
    """

    if roce is None:
        return "N/A"

    if sector.lower() == "financials":
        return "Sector Relative"

    if roce >= 15:
        return "Good"

    if roce >= 10:
        return "Average"

    return "Poor"


# ==========================================================
# DAY 9 — LEVERAGE & EFFICIENCY RATIOS
# ==========================================================

def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt / Equity
    Return 0 if company is debt free.
    Return None if equity <= 0.
    """
    equity = equity_capital + reserves

    if borrowings == 0:
        return 0

    if equity <= 0:
        return None

    return round(borrowings / equity, 2)


def high_leverage_flag(de_ratio, sector):
    """
    High leverage warning.

    Financial companies are excluded.
    """

    if sector.lower() == "financials":
        return False

    if de_ratio is None:
        return False

    return de_ratio > 5


def interest_coverage_ratio(
    operating_profit,
    other_income,
    interest
):
    """
    Interest Coverage Ratio
    """

    if interest == 0:
        return None

    return round(
        (operating_profit + other_income) / interest,
        2
    )


def icr_label(icr):
    """
    Label debt-free companies.
    """

    if icr is None:
        return "Debt Free"

    return ""


def icr_warning(icr):
    """
    Warning if ICR < 1.5
    """

    if icr is None:
        return False

    return icr < 1.5


def net_debt(
    borrowings,
    investments
):
    """
    Net Debt
    """

    return borrowings - investments


def asset_turnover(
    sales,
    total_assets
):
    """
    Asset Turnover
    """

    if total_assets == 0:
        return None

    return round(
        sales / total_assets,
        2
    )