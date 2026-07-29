import sqlite3
from pathlib import Path

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

# ----------------------------
# Paths
# ----------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT = BASE_DIR / "output"

REPORTS = BASE_DIR / "reports" / "tearsheets"

REPORTS.mkdir(parents=True, exist_ok=True)

DB = BASE_DIR / "db" / "nifty100.db"

styles = getSampleStyleSheet()

title_style = styles["Heading1"]
title_style.alignment = TA_CENTER

heading = styles["Heading2"]

normal = styles["BodyText"]

# ----------------------------
# Load Data
# ----------------------------

conn = sqlite3.connect(DB)

master = pd.read_sql(
    "SELECT * FROM master_financials",
    conn
)

pros = pd.read_csv(
    OUTPUT / "pros_cons_generated.csv"
)

cashflow = pd.read_excel(
    OUTPUT / "cashflow_intelligence.xlsx"
)

companies = sorted(master.company_id.unique())

print("Companies :", len(companies))

# ----------------------------
# Generate One PDF
# ----------------------------

def build_pdf(company):

    pdf = REPORTS / f"{company}_tearsheet.pdf"

    doc = SimpleDocTemplate(
        str(pdf)
    )

    story = []

    story.append(
        Paragraph(
            f"{company} Financial Tearsheet",
            title_style
        )
    )

    story.append(
        Spacer(1, 0.3 * inch)
    )

    latest = (

        master[
            master.company_id == company
        ]

        .sort_values("year")

        .tail(1)

    )
    
    if latest.empty:
        return

    latest = latest.iloc[0]

    kpi_data = [
        ["Metric", "Value"],
        ["Sales", f"{latest['sales']:.2f}"],
        ["Net Profit", f"{latest['net_profit']:.2f}"],
        ["P/E", f"{latest['pe_ratio']:.2f}"],
        ["P/B", f"{latest['pb_ratio']:.2f}"],
        ["ROE", f"{latest['return_on_equity_pct']:.2f}%"],
        ["Debt / Equity", f"{latest['debt_to_equity']:.2f}"],
    ]

    table = Table(kpi_data, colWidths=[220, 180])

    table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.darkblue),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("BACKGROUND",(0,1),(-1,-1),colors.beige),

            ("ALIGN",(0,0),(-1,-1),"CENTER"),

            ("BOTTOMPADDING",(0,0),(-1,0),8)

        ])

    )

    story.append(table)

    story.append(
        Spacer(1,0.25*inch)
    )
    
    company_pros = pros[
        (pros.company_id==company)
        &
        (pros.type=="pro")
    ]

    company_cons = pros[
        (pros.company_id==company)
        &
        (pros.type=="con")
    ]

    story.append(
        Paragraph("<b>Pros</b>",heading)
    )

    if len(company_pros):

        for _,row in company_pros.head(5).iterrows():

            story.append(
                Paragraph(
                    "• "+row["text"],
                    normal
                )
            )

    story.append(
        Spacer(1,0.15*inch)
    )

    story.append(
        Paragraph("<b>Cons</b>",heading)
    )

    if len(company_cons):

        for _,row in company_cons.head(5).iterrows():

            story.append(
                Paragraph(
                    "• "+row["text"],
                    normal
                )
            )
            
    cf = cashflow[
        cashflow.company_id==company
    ]

    if len(cf):

        cf = cf.iloc[0]

        story.append(
            Spacer(1,0.25*inch)
        )

        story.append(

            Paragraph(

                f"<b>Capital Allocation:</b> {cf['capital_allocation']}",

                heading

            )

        )

    doc.build(story)

    print(company,"Done")


# ---------------------------------

for company in companies[:5]:

    build_pdf(company)

print("\nDay 33 Sample Tearsheet Generation Completed")
    