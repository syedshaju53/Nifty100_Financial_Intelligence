# ============================================
# Liquidity Analytics
# ============================================

def current_ratio(current_assets, current_liabilities):
    """Current Assets / Current Liabilities."""
    if current_liabilities == 0:
        return None
    return round(current_assets / current_liabilities, 2)


def quick_ratio(quick_assets, current_liabilities):
    """Quick Assets / Current Liabilities."""
    if current_liabilities == 0:
        return None
    return round(quick_assets / current_liabilities, 2)


def cash_ratio(cash_and_equivalents, current_liabilities):
    """Cash and Equivalents / Current Liabilities."""
    if current_liabilities == 0:
        return None
    return round(cash_and_equivalents / current_liabilities, 2)


def liquidity_label(current_ratio_value):
    """Classify current ratio."""
    if current_ratio_value is None:
        return "Unknown"

    if current_ratio_value >= 2:
        return "Strong"
    elif current_ratio_value >= 1:
        return "Adequate"
    else:
        return "Weak"