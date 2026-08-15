import sqlite3
from pathlib import Path
from html import escape

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    KeepTogether,
)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT = BASE_DIR / "output"
REPORTS = BASE_DIR / "reports" / "tearsheets"
DB = BASE_DIR / "db" / "nifty100.db"

REPORTS.mkdir(parents=True, exist_ok=True)

# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TearsheetTitle",
    parent=styles["Title"],
    fontSize=22,
    leading=26,
    alignment=TA_CENTER,
    spaceAfter=14,
)

subtitle_style = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontSize=9,
    leading=12,
    alignment=TA_CENTER,
    textColor=colors.grey,
    spaceAfter=16,
)

section_style = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontSize=14,
    leading=17,
    spaceBefore=8,
    spaceAfter=8,
)

body_style = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontSize=8.5,
    leading=12,
    spaceAfter=5,
)

small_style = ParagraphStyle(
    "Small",
    parent=styles["BodyText"],
    fontSize=7.5,
    leading=10,
)

# ============================================================
# DATA
# ============================================================

conn = sqlite3.connect(DB)

master = pd.read_sql(
    "SELECT * FROM master_financials",
    conn
)

pros_path = OUTPUT / "pros_cons_generated.csv"
cashflow_path = OUTPUT / "cashflow_intelligence.xlsx"

pros = (
    pd.read_csv(pros_path)
    if pros_path.exists()
    else pd.DataFrame()
)

cashflow = (
    pd.read_excel(cashflow_path)
    if cashflow_path.exists()
    else pd.DataFrame()
)

companies = sorted(
    master["company_id"].dropna().astype(str).unique()
)

print("Companies :", len(companies))


# ============================================================
# HELPERS
# ============================================================

def fmt(value, decimals=2):
    if pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):,.{decimals}f}"
    except Exception:
        return escape(str(value))


def pct(value):
    if pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):,.2f}%"
    except Exception:
        return escape(str(value))


def safe_text(value):
    if pd.isna(value):
        return "N/A"
    return escape(str(value))


def make_table(data, widths=None, header=True):
    table = Table(
        data,
        colWidths=widths,
        repeatRows=1 if header else 0,
        hAlign="LEFT",
    )

    commands = [
        ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]

    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])

    table.setStyle(TableStyle(commands))
    return table


def footer(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.grey)

    canvas.drawString(
        0.55 * inch,
        0.35 * inch,
        "N100 Financial Intelligence Platform"
    )

    canvas.drawRightString(
        7.95 * inch,
        0.35 * inch,
        f"Page {doc.page}"
    )

    canvas.restoreState()


# ============================================================
# TEARSHEET GENERATOR
# ============================================================

def build_pdf(company):

    company = str(company)

    pdf = REPORTS / f"{company}_tearsheet.pdf"

    df = (
        master[
            master["company_id"].astype(str) == company
        ]
        .copy()
    )

    if df.empty:
        raise ValueError(f"No financial data found for {company}")

    df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce"
    )

    df = df.sort_values("year")

    latest = df.iloc[-1]

    # --------------------------------------------------------
    # DOCUMENT
    # --------------------------------------------------------

    doc = SimpleDocTemplate(
        str(pdf),
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title=f"{company} Financial Tearsheet",
        author="N100 Financial Intelligence Platform",
    )

    story = []

    # --------------------------------------------------------
    # COVER / TITLE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            f"{company} Financial Tearsheet",
            title_style
        )
    )

    story.append(
        Paragraph(
            "N100 Financial Intelligence Platform",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            "Comprehensive financial intelligence report covering "
            "financial performance, profitability, growth, valuation, "
            "leverage, efficiency, cash flow, strengths and risks.",
            body_style
        )
    )

    # --------------------------------------------------------
    # 1. COMPANY SNAPSHOT
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "1. Company Snapshot",
            section_style
        )
    )

    snapshot = [
        ["Attribute", "Value"],
        ["Company ID", company],
        ["Latest Financial Year", safe_text(latest["year"])],
        ["Historical Records", str(len(df))],
        ["First Available Year", safe_text(df["year"].min())],
        ["Latest Available Year", safe_text(df["year"].max())],
    ]

    story.append(
        make_table(
            snapshot,
            [3.0 * inch, 3.7 * inch]
        )
    )

    story.append(Spacer(1, 0.15 * inch))

    # --------------------------------------------------------
    # 2. KPI DASHBOARD
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "2. Latest Financial KPI Dashboard",
            section_style
        )
    )

    metrics = [
        ("Sales", fmt(latest.get("sales"))),
        ("Net Profit", fmt(latest.get("net_profit"))),
        ("Operating Profit", fmt(latest.get("operating_profit"))),
        ("Profit Before Tax", fmt(latest.get("profit_before_tax"))),
        ("ROE", pct(latest.get("return_on_equity_pct"))),
        ("ROCE", pct(latest.get("roce_pct"))),
        ("Net Profit Margin", pct(latest.get("net_profit_margin_pct"))),
        ("Operating Margin", pct(latest.get("operating_margin_pct"))),
        ("Debt / Equity", fmt(latest.get("debt_to_equity"))),
        ("Interest Coverage", fmt(latest.get("interest_coverage"))),
        ("Asset Turnover", fmt(latest.get("asset_turnover"))),
        ("EPS", fmt(latest.get("eps"))),
        ("Free Cash Flow", fmt(latest.get("free_cash_flow"))),
        ("Dividend Yield", pct(latest.get("dividend_yield_pct"))),
        ("P/E", fmt(latest.get("pe_ratio"))),
        ("P/B", fmt(latest.get("pb_ratio"))),
        ("EV / EBITDA", fmt(latest.get("ev_ebitda"))),
        ("Enterprise Value", fmt(latest.get("enterprise_value"))),
    ]

    kpi_data = [
        ["Metric", "Latest Value", "Metric", "Latest Value"]
    ]

    for i in range(0, len(metrics), 2):
        left = metrics[i]
        right = metrics[i + 1] if i + 1 < len(metrics) else ("", "")

        kpi_data.append([
            left[0],
            left[1],
            right[0],
            right[1],
        ])

    story.append(
        make_table(
            kpi_data,
            [
                1.65 * inch,
                1.65 * inch,
                1.65 * inch,
                1.65 * inch,
            ]
        )
    )

    # --------------------------------------------------------
    # 3. HISTORICAL PERFORMANCE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "3. Historical Financial Performance",
            section_style
        )
    )

    history_columns = [
        ("year", "Year"),
        ("sales", "Sales"),
        ("net_profit", "Net Profit"),
        ("operating_profit", "Operating Profit"),
        ("eps", "EPS"),
    ]

    history = [["Year", "Sales", "Net Profit", "Operating Profit", "EPS"]]

    historical = df.tail(10)

    for _, row in historical.iterrows():
        history.append([
            safe_text(row["year"]),
            fmt(row.get("sales")),
            fmt(row.get("net_profit")),
            fmt(row.get("operating_profit")),
            fmt(row.get("eps")),
        ])

    story.append(
        make_table(
            history,
            [
                0.8 * inch,
                1.35 * inch,
                1.35 * inch,
                1.55 * inch,
                1.0 * inch,
            ]
        )
    )

    # --------------------------------------------------------
    # 4. GROWTH ANALYSIS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "4. Growth & Compounding Analysis",
            section_style
        )
    )

    growth_fields = [
        ("Revenue CAGR — 5 Year", "revenue_cagr_5y"),
        ("PAT CAGR — 5 Year", "pat_cagr_5y"),
        ("EPS CAGR — 5 Year", "eps_cagr_5y"),
        ("FCF CAGR — 5 Year", "fcf_cagr_5y"),
    ]

    growth = [["Growth KPI", "Value"]]

    for label, field in growth_fields:
        growth.append([
            label,
            pct(latest.get(field))
        ])

    story.append(
        make_table(
            growth,
            [4.0 * inch, 2.0 * inch]
        )
    )

    story.append(
        Paragraph(
            "Growth metrics are interpreted together with profitability "
            "and cash-flow quality rather than in isolation.",
            small_style
        )
    )

    # --------------------------------------------------------
    # 5. PROFITABILITY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "5. Profitability & Return Profile",
            section_style
        )
    )

    profitability = [
        ["Metric", "Value"],
        ["ROE", pct(latest.get("return_on_equity_pct"))],
        ["ROCE", pct(latest.get("roce_pct"))],
        ["Net Profit Margin", pct(latest.get("net_profit_margin_pct"))],
        ["Operating Margin", pct(latest.get("operating_margin_pct"))],
        ["Return on Assets", pct(latest.get("return_on_assets_pct"))],
    ]

    story.append(
        make_table(
            profitability,
            [4.0 * inch, 2.0 * inch]
        )
    )

    # --------------------------------------------------------
    # 6. VALUATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "6. Valuation Assessment",
            section_style
        )
    )

    valuation = [
        ["Valuation Metric", "Latest Value"],
        ["P/E", fmt(latest.get("pe_ratio"))],
        ["P/B", fmt(latest.get("pb_ratio"))],
        ["EV / EBITDA", fmt(latest.get("ev_ebitda"))],
        ["Earnings Yield", pct(latest.get("earnings_yield_pct"))],
        ["Enterprise Value", fmt(latest.get("enterprise_value"))],
    ]

    story.append(
        make_table(
            valuation,
            [4.0 * inch, 2.0 * inch]
        )
    )

    # --------------------------------------------------------
    # 7. LEVERAGE & LIQUIDITY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "7. Leverage & Financial Risk",
            section_style
        )
    )

    leverage = [
        ["Risk Metric", "Value"],
        ["Debt / Equity", fmt(latest.get("debt_to_equity"))],
        ["Interest Coverage", fmt(latest.get("interest_coverage"))],
        ["Current Ratio", fmt(latest.get("current_ratio"))],
        ["Quick Ratio", fmt(latest.get("quick_ratio"))],
        ["Net Debt", fmt(latest.get("net_debt"))],
    ]

    story.append(
        make_table(
            leverage,
            [4.0 * inch, 2.0 * inch]
        )
    )

    # --------------------------------------------------------
    # 8. CASH FLOW
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "8. Cash Flow & Capital Allocation",
            section_style
        )
    )

    if not cashflow.empty and "company_id" in cashflow.columns:
        cf = cashflow[
            cashflow["company_id"].astype(str) == company
        ]

        if not cf.empty:
            cf = cf.iloc[0]

            cf_data = [["Metric", "Value"]]

            for field in [
                "free_cash_flow",
                "fcf_conversion",
                "cfo_quality",
                "capital_allocation",
            ]:
                if field in cf.index:
                    cf_data.append([
                        field.replace("_", " ").title(),
                        safe_text(cf[field])
                    ])

            story.append(
                make_table(
                    cf_data,
                    [4.0 * inch, 2.0 * inch]
                )
            )
        else:
            story.append(
                Paragraph(
                    "No additional cash-flow intelligence record was "
                    "available for this company.",
                    body_style
                )
            )
    else:
        story.append(
            Paragraph(
                "Cash-flow intelligence dataset unavailable.",
                body_style
            )
        )

    # --------------------------------------------------------
    # 9. PROS & CONS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "9. Investment Strengths & Risks",
            section_style
        )
    )

    if not pros.empty and "company_id" in pros.columns:

        company_pros = pros[
            (pros["company_id"].astype(str) == company)
            & (pros["type"].astype(str).str.lower() == "pro")
        ].head(5)

        company_cons = pros[
            (pros["company_id"].astype(str) == company)
            & (pros["type"].astype(str).str.lower() == "con")
        ].head(5)

        story.append(
            Paragraph("<b>Strengths</b>", body_style)
        )

        if not company_pros.empty:
            for _, row in company_pros.iterrows():
                story.append(
                    Paragraph(
                        "• " + safe_text(row.get("text")),
                        body_style
                    )
                )
        else:
            story.append(
                Paragraph(
                    "No generated strengths available.",
                    body_style
                )
            )

        story.append(Spacer(1, 0.08 * inch))

        story.append(
            Paragraph("<b>Risks / Cons</b>", body_style)
        )

        if not company_cons.empty:
            for _, row in company_cons.iterrows():
                story.append(
                    Paragraph(
                        "• " + safe_text(row.get("text")),
                        body_style
                    )
                )
        else:
            story.append(
                Paragraph(
                    "No generated risks available.",
                    body_style
                )
            )

    # --------------------------------------------------------
    # 10. ANALYST SUMMARY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "10. Analyst Summary",
            section_style
        )
    )

    summary_parts = [
        f"{company} has {len(df)} historical financial records "
        f"available in the analytical database.",
        f"The latest financial year represented in the dataset is "
        f"{safe_text(latest['year'])}.",
        f"Latest reported sales are {fmt(latest.get('sales'))} and "
        f"net profit is {fmt(latest.get('net_profit'))}.",
        f"Return on equity is {pct(latest.get('return_on_equity_pct'))}, "
        f"while debt-to-equity is {fmt(latest.get('debt_to_equity'))}.",
        f"The valuation snapshot shows P/E of {fmt(latest.get('pe_ratio'))} "
        f"and P/B of {fmt(latest.get('pb_ratio'))}.",
    ]

    for text in summary_parts:
        story.append(
            Paragraph(
                text,
                body_style
            )
        )

    story.append(
        Spacer(1, 0.2 * inch)
    )

    # --------------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "<b>Data & Methodology Note</b>",
            section_style
        )
    )

    story.append(
        Paragraph(
            "This tearsheet is generated from the Nifty100 Financial "
            "Intelligence analytical database and derived output files. "
            "Metrics are presented for analytical and educational purposes. "
            "The report is not investment advice and should not be treated "
            "as a recommendation to buy or sell any security.",
            small_style
        )
    )

    doc.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer,
    )

    size_kb = pdf.stat().st_size / 1024

    print(
        f"{company} Done ({size_kb:.1f} KB)"
    )


if __name__ == "__main__":

    for company in companies:
        build_pdf(company)

    print(
        "\nTearsheet generation completed:",
        len(companies)
    )
