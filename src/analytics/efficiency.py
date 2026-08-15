# ============================================
# Efficiency Analytics
# ============================================

def asset_turnover(revenue, total_assets):
    """Revenue / Total Assets."""
    if total_assets == 0:
        return None

    return round(revenue / total_assets, 2)


def inventory_turnover(cogs, average_inventory):
    """COGS / Average Inventory."""
    if average_inventory == 0:
        return None

    return round(cogs / average_inventory, 2)


def receivables_turnover(revenue, average_receivables):
    """Revenue / Average Receivables."""
    if average_receivables == 0:
        return None

    return round(revenue / average_receivables, 2)


def days_sales_outstanding(average_receivables, revenue):
    """Average Receivables / Revenue × 365."""
    if revenue == 0:
        return None

    return round((average_receivables / revenue) * 365, 2)


def working_capital_turnover(revenue, working_capital):
    """Revenue / Working Capital."""
    if working_capital == 0:
        return None

    return round(revenue / working_capital, 2)