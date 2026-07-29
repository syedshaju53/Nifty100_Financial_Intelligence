import sqlite3
from pathlib import Path

import pandas as pd

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

BASE_DIR = Path(__file__).resolve().parents[2]

DB = BASE_DIR / "db" / "nifty100.db"

OUTPUT = BASE_DIR / "output"

REPORT_DIR = BASE_DIR / "reports" / "portfolio"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

doc = SimpleDocTemplate(
    str(REPORT_DIR / "portfolio_summary.pdf")
)

story = []

conn = sqlite3.connect(DB)

master = pd.read_sql(
    "SELECT * FROM master_financials",
    conn
)

cashflow = pd.read_excel(
    OUTPUT / "cashflow_intelligence.xlsx"
)

companies = sorted(master.company_id.unique())

print("Companies :", len(companies))

for company in companies:

    latest = (
        master[
            master.company_id == company
        ]
        .sort_values("year")
        .tail(1)
    )

    if latest.empty:
        continue

    latest = latest.iloc[0]

    story.append(
        Paragraph(
            f"<b>{company}</b>",
            styles["Heading1"]
        )
    )

    story.append(
        Paragraph(
            f"Latest Financial Year: {int(latest['year'])}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Sales: {latest['sales']:.2f}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Net Profit: {latest['net_profit']:.2f}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"ROE: {latest['return_on_equity_pct']:.2f}%",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Debt/Equity: {latest['debt_to_equity']:.2f}",
            styles["BodyText"]
        )
    )

    cf = cashflow[cashflow.company_id == company]

    if not cf.empty:

        cf = cf.iloc[0]

        story.append(
            Paragraph(
                f"Capital Allocation: {cf['capital_allocation_label']}",
                styles["BodyText"]
            )
        )

    story.append(Spacer(1, 20))
    story.append(PageBreak())
    
    doc.build(story)

print("=" * 50)
print("Portfolio Summary Generated Successfully")
print("=" * 50)

print("Saved to:")
print(REPORT_DIR / "portfolio_summary.pdf")