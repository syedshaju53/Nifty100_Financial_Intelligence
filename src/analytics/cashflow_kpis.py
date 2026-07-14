# ============================================
# Day 11 - Cash Flow KPIs
# Sprint 2
# ============================================

def free_cash_flow(cfo, cfi):
    """
    Free Cash Flow = CFO + CFI
    """
    return cfo + cfi


def cfo_quality_score(cfo, pat):
    """
    CFO / PAT
    """
    if pat == 0:
        return None, None

    score = cfo / pat

    if score > 1:
        label = "High Quality"
    elif score >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return round(score, 2), label


def capex_intensity(cfi, sales):
    """
    abs(CFI) / Sales × 100
    """
    if sales == 0:
        return None, None

    intensity = abs(cfi) / sales * 100

    if intensity < 3:
        label = "Asset Light"
    elif intensity <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return round(intensity, 2), label


def fcf_conversion_rate(fcf, operating_profit):
    """
    FCF / Operating Profit × 100
    """
    if operating_profit == 0:
        return None

    return round((fcf / operating_profit) * 100, 2)


def capital_allocation_pattern(cfo, cfi, cff, quality="Moderate"):

    cfo_sign = "+" if cfo >= 0 else "-"
    cfi_sign = "+" if cfi >= 0 else "-"
    cff_sign = "+" if cff >= 0 else "-"

    signs = (cfo_sign, cfi_sign, cff_sign)

    if signs == ("+", "-", "-"):

        if quality == "High Quality":
            label = "Shareholder Returns"
        else:
            label = "Reinvestor"

    elif signs == ("+", "+", "-"):
        label = "Liquidating Assets"

    elif signs == ("-", "+", "+"):
        label = "Distress Signal"

    elif signs == ("-", "-", "+"):
        label = "Growth Funded by Debt"

    elif signs == ("+", "+", "+"):
        label = "Cash Accumulator"

    elif signs == ("-", "-", "-"):
        label = "Pre-Revenue"

    elif signs == ("+", "-", "+"):
        label = "Mixed"

    else:
        label = "Other"

    return {
        "cfo_sign": cfo_sign,
        "cfi_sign": cfi_sign,
        "cff_sign": cff_sign,
        "pattern_label": label,
    }


# ============================================
# Demo
# ============================================

if __name__ == "__main__":

    fcf = free_cash_flow(8500, -3200)

    score, quality = cfo_quality_score(8500, 7000)

    capex, capex_label = capex_intensity(-3200, 25000)

    conversion = fcf_conversion_rate(fcf, 9000)

    pattern = capital_allocation_pattern(
        8500,
        -3200,
        -1800,
        quality
    )

    print("\n========== DAY 11 ==========")
    print("Free Cash Flow :", fcf)
    print("CFO Quality :", score, quality)
    print("CapEx Intensity :", capex, capex_label)
    print("FCF Conversion :", conversion)
    print("Capital Allocation :", pattern)