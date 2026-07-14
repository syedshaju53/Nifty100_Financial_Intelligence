import sqlite3
import pandas as pd
from pathlib import Path

from src.analytics.ratios import (
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover,
    net_debt
)

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

pl = pd.read_sql("SELECT * FROM profit_loss", conn)
bs = pd.read_sql("SELECT * FROM balance_sheet", conn)

df = pl.merge(
    bs,
    on=["id", "year"],
    how="inner"
)

df["debt_to_equity"] = df.apply(
    lambda x: debt_to_equity(
        x.borrowings,
        x.equity_capital,
        x.reserves
    ),
    axis=1
)

df["interest_coverage"] = df.apply(
    lambda x: interest_coverage_ratio(
        x.operating_profit,
        0,
        1
    ),
    axis=1
)

df["asset_turnover"] = df.apply(
    lambda x: asset_turnover(
        x.sales,
        x.total_assets
    ),
    axis=1
)

df["net_debt"] = df.apply(
    lambda x: net_debt(
        x.borrowings,
        x.investments
    ),
    axis=1
)

print(df[
    [
        "id",
        "year",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "net_debt"
    ]
].head(10))

conn.close()