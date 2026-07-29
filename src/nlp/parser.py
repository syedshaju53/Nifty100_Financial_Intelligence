import sqlite3
import pandas as pd
import re
from pathlib import Path

# -----------------------------------
# Paths
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

OUTPUT = BASE_DIR / "output"
OUTPUT.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# -----------------------------------
# Load Analysis Table
# -----------------------------------

analysis = pd.read_sql(
    "SELECT * FROM analysis",
    conn
)

print("Rows Loaded :", len(analysis))

# -----------------------------------
# Regex
# -----------------------------------

pattern = re.compile(
    r"(\d+)\s*Years?:?\s*([\d.]+)%"
)

parsed_rows = []
failed_rows = []

# -----------------------------------
# Target Columns
# -----------------------------------

metrics = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe"
]

# -----------------------------------
# Parse
# -----------------------------------

for _, row in analysis.iterrows():

    company = row["company_id"]

    for metric in metrics:

        text = str(row[metric])

        match = pattern.search(text)

        if match:

            parsed_rows.append({

                "company_id": company,

                "metric_type": metric,

                "period_years": int(match.group(1)),

                "value_pct": float(match.group(2))

            })

        else:

            failed_rows.append({

                "company_id": company,

                "metric_type": metric,

                "raw_text": text

            })

# -----------------------------------
# Save Parsed Output
# -----------------------------------

parsed_df = pd.DataFrame(parsed_rows)

parsed_df.to_csv(

    OUTPUT / "analysis_parsed.csv",

    index=False

)

print("Parsed :", len(parsed_df))

# -----------------------------------
# Save Failures
# -----------------------------------

failed_df = pd.DataFrame(failed_rows)

failed_df.to_csv(

    OUTPUT / "parse_failures.csv",

    index=False

)

print("Failures :", len(failed_df))

# -----------------------------------
# Cross Validation
# -----------------------------------

master = pd.read_sql("""

SELECT
company_id,
year,
revenue_cagr_5yr,
pat_cagr_5yr

FROM master_financials

""", conn)

validation = []

for _, row in parsed_df.iterrows():

    if row["period_years"] != 5:
        continue

    company = row["company_id"]

    latest = master[
        master["company_id"] == company
    ].sort_values("year")

    if latest.empty:
        continue

    latest = latest.iloc[-1]

    computed = None

    if row["metric_type"] == "compounded_sales_growth":
        computed = latest["revenue_cagr_5yr"]

    elif row["metric_type"] == "compounded_profit_growth":
        computed = latest["pat_cagr_5yr"]

    if pd.notna(computed):

        diff = abs(
            computed - row["value_pct"]
        )

        validation.append({

            "company_id": company,

            "metric": row["metric_type"],

            "parsed": row["value_pct"],

            "computed": computed,

            "difference": diff,

            "review_required": diff > 5

        })

validation_df = pd.DataFrame(validation)

validation_df.to_csv(

    OUTPUT / "cagr_validation.csv",

    index=False

)

print("Validation Completed")

conn.close()

