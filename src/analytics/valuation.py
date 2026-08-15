# ============================================
# Nifty100 Financial Intelligence
# Valuation Analytics
# ============================================

def price_to_earnings(price, eps):
    """
    P/E Ratio = Market Price / Earnings Per Share

    Returns None when EPS is zero or negative because
    a conventional P/E ratio is not meaningful.
    """
    if eps is None or eps <= 0:
        return None

    return round(price / eps, 2)


def price_to_book(price, book_value_per_share):
    """
    P/B Ratio = Market Price / Book Value Per Share

    Returns None when book value is zero or negative.
    """
    if book_value_per_share is None or book_value_per_share <= 0:
        return None

    return round(price / book_value_per_share, 2)


def earnings_yield(eps, price):
    """
    Earnings Yield = EPS / Market Price × 100
    """
    if price is None or price <= 0:
        return None

    return round((eps / price) * 100, 2)


def peg_ratio(pe_ratio, earnings_growth):
    """
    PEG Ratio = P/E Ratio / Earnings Growth Rate

    earnings_growth should be supplied as a percentage.
    Example:
        P/E = 20
        Growth = 10%
        PEG = 2.0
    """
    if pe_ratio is None or earnings_growth is None:
        return None

    if earnings_growth <= 0:
        return None

    return round(pe_ratio / earnings_growth, 2)


def enterprise_value(market_cap, total_debt, cash):
    """
    Enterprise Value = Market Capitalisation + Debt - Cash
    """
    if market_cap is None:
        return None

    total_debt = 0 if total_debt is None else total_debt
    cash = 0 if cash is None else cash

    return round(market_cap + total_debt - cash, 2)


def ev_to_ebitda(enterprise_value_value, ebitda):
    """
    EV/EBITDA = Enterprise Value / EBITDA
    """
    if enterprise_value_value is None:
        return None

    if ebitda is None or ebitda <= 0:
        return None

    return round(enterprise_value_value / ebitda, 2)


def valuation_label(pe_ratio=None, pb_ratio=None, peg=None):
    """
    Simple valuation classification.

    Rules:
        P/E <= 15 and P/B <= 3 -> Undervalued
        P/E <= 25 and P/B <= 5 -> Fairly Valued
        Otherwise -> Expensive

    PEG below 1 can strengthen the undervalued signal.
    """

    if pe_ratio is None and pb_ratio is None:
        return "Unknown"

    # Strong growth-adjusted valuation
    if peg is not None and peg < 1:
        return "Undervalued"

    if pe_ratio is not None and pb_ratio is not None:

        if pe_ratio <= 15 and pb_ratio <= 3:
            return "Undervalued"

        if pe_ratio <= 25 and pb_ratio <= 5:
            return "Fairly Valued"

        return "Expensive"

    if pe_ratio is not None:

        if pe_ratio <= 15:
            return "Undervalued"

        if pe_ratio <= 25:
            return "Fairly Valued"

        return "Expensive"

    if pb_ratio is not None:

        if pb_ratio <= 3:
            return "Undervalued"

        if pb_ratio <= 5:
            return "Fairly Valued"

        return "Expensive"

    return "Unknown"


def valuation_summary(
    price,
    eps=None,
    book_value_per_share=None,
    earnings_growth=None,
    market_cap=None,
    total_debt=None,
    cash=None,
    ebitda=None,
):
    """
    Generate a complete valuation summary.
    """

    pe = price_to_earnings(price, eps)
    pb = price_to_book(price, book_value_per_share)
    ey = earnings_yield(eps, price)

    peg = None

    if pe is not None:
        peg = peg_ratio(pe, earnings_growth)

    ev = None
    ev_ebitda = None

    if market_cap is not None:
        ev = enterprise_value(
            market_cap,
            total_debt,
            cash,
        )

        if ev is not None:
            ev_ebitda = globals()["ev_to_ebitda"](
                ev,
                ebitda,
            )

    label = valuation_label(
        pe_ratio=pe,
        pb_ratio=pb,
        peg=peg,
    )

    return {
        "pe_ratio": pe,
        "pb_ratio": pb,
        "earnings_yield": ey,
        "peg_ratio": peg,
        "enterprise_value": ev,
        "ev_to_ebitda": ev_ebitda,
        "valuation_label": label,
    }


if __name__ == "__main__":

    result = valuation_summary(
        price=1500,
        eps=75,
        book_value_per_share=400,
        earnings_growth=12,
        market_cap=150000,
        total_debt=20000,
        cash=10000,
        ebitda=18000,
    )

    print("\n========== VALUATION ANALYTICS ==========")

    for key, value in result.items():
        print(f"{key}: {value}")