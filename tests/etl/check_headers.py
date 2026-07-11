from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA = BASE_DIR / "data" / "raw"

files = [
    "stock_prices.xlsx",
    "financial_ratios.xlsx",
    "market_cap.xlsx",
    "peer_groups.xlsx",
    "sectors.xlsx"
]

for file in files:

    print("\n" + "=" * 70)
    print(file)

    for header in [0, 1, 2]:

        print(f"\nHEADER = {header}")

        df = pd.read_excel(RAW_DATA / file, header=header)

        print(df.columns.tolist())