from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA = BASE_DIR / "data" / "raw"

files = [
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "stock_prices.xlsx",
    "financial_ratios.xlsx",
    "analysis.xlsx",
    "market_cap.xlsx",
    "peer_groups.xlsx",
    "prosandcons.xlsx",
    "sectors.xlsx",
    "documents.xlsx"
]

for file in files:
    print("\n" + "=" * 60)
    print(file)

    df = pd.read_excel(RAW_DATA / file, header=1)

    print(df.columns.tolist())