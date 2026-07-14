def profitability_score(npm):
    if npm >= 20:
        return 20
    elif npm >= 15:
        return 16
    elif npm >= 10:
        return 12
    elif npm >= 5:
        return 8
    else:
        return 4


def roe_score(roe):
    if roe >= 20:
        return 20
    elif roe >= 15:
        return 16
    elif roe >= 10:
        return 12
    elif roe >= 5:
        return 8
    else:
        return 4


def leverage_score(de):
    if de <= 0.5:
        return 20
    elif de <= 1:
        return 16
    elif de <= 2:
        return 12
    elif de <= 3:
        return 8
    else:
        return 4


def efficiency_score(asset_turnover):
    if asset_turnover >= 2:
        return 20
    elif asset_turnover >= 1.5:
        return 16
    elif asset_turnover >= 1:
        return 12
    elif asset_turnover >= 0.5:
        return 8
    else:
        return 4


def total_health_score(p, r, l, e):
    return p + r + l + e


def health_rating(score):
    if score >= 70:
        return "Excellent"
    elif score >= 55:
        return "Good"
    elif score >= 40:
        return "Average"
    else:
        return "Weak"