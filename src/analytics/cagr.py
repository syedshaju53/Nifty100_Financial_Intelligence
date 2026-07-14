"""
Sprint 2 - Day 10
CAGR Engine
"""

from typing import Optional, Tuple


def calculate_cagr(start_value: float, end_value: float, years: int) -> Tuple[Optional[float], str]:
    """
    CAGR = ((Ending / Beginning) ** (1 / Years) - 1) × 100

    Returns:
        (cagr_value, flag)
    """

    # Less than required years
    if years <= 0:
        return None, "INSUFFICIENT"

    # Zero base
    if start_value == 0:
        return None, "ZERO_BASE"

    # Positive -> Negative
    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    # Negative -> Positive
    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    # Negative -> Negative
    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    # Normal CAGR
    cagr = ((end_value / start_value) ** (1 / years) - 1) * 100

    return round(cagr, 2), "OK"


def revenue_cagr(start_sales, end_sales, years):
    return calculate_cagr(start_sales, end_sales, years)


def pat_cagr(start_pat, end_pat, years):
    return calculate_cagr(start_pat, end_pat, years)


def eps_cagr(start_eps, end_eps, years):
    return calculate_cagr(start_eps, end_eps, years)