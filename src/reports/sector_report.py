import sqlite3
from pathlib import Path

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

# ------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DB = BASE_DIR / "db" / "nifty100.db"

REPORT_DIR = BASE_DIR / "reports" / "sector"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

conn = sqlite3.connect(DB)

master = pd.read_sql(
    "SELECT * FROM master_financials",
    conn
)

sectors = pd.read_sql(
    "SELECT * FROM sectors",
    conn
)

data = master.merge(
    sectors,
    on="company_id",
    how="left"
)

print("Financial Rows :", len(master))
print("Sector Rows    :", len(sectors))
print("Merged Rows    :", len(data))

# ------------------------------------
# Create Sector Report
# ------------------------------------

def create_sector_report(sector_name):

    sector_df = data[data["broad_sector"] == sector_name]

    if sector_df.empty:
        return

    pdf_path = REPORT_DIR / f"{sector_name.replace(' ', '_')}_report.pdf"

    doc = SimpleDocTemplate(str(pdf_path))

    story = []

    story.append(
        Paragraph(
            f"<b>{sector_name} Sector Report</b>",
            styles["Heading1"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            f"Companies : {sector_df['company_id'].nunique()}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 12))
    
    
    latest = (
        sector_df
        .sort_values("year")
        .groupby("company_id")
        .tail(1)
    )

    summary = [

        ["Metric", "Median"],

        ["Sales", round(latest["sales"].median(), 2)],

        ["Net Profit", round(latest["net_profit"].median(), 2)],

        ["ROE", round(latest["return_on_equity_pct"].median(), 2)],

        ["Debt/Equity", round(latest["debt_to_equity"].median(), 2)]

    ]

    table = Table(summary, colWidths=[220, 180])

    table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.darkblue),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("BACKGROUND",(0,1),(-1,-1),colors.beige),

            ("ALIGN",(0,0),(-1,-1),"CENTER")

        ])

    )

    story.append(table)

    story.append(Spacer(1, 20))
    
    story.append(
        Paragraph(
            "<b>Companies</b>",
            styles["Heading2"]
        )
    )

    company_table = [["Company"]]

    for company in sorted(latest["company_id"].unique()):
        company_table.append([company])

    table2 = Table(company_table, colWidths=[400])

    table2.setStyle(

        TableStyle([

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)

        ])

    )

    story.append(table2)

    doc.build(story)

    print(f"Generated: {pdf_path.name}")
    


# ------------------------------------
# Generate reports for all sectors
# ------------------------------------

all_sectors = sorted(data["broad_sector"].dropna().unique())

print("\nGenerating Sector Reports...\n")

for sector in all_sectors:
    create_sector_report(sector)

print("\n" + "=" * 50)
print("All Sector Reports Generated Successfully")
print("=" * 50)
print(f"Total Sector Reports: {len(all_sectors)}")