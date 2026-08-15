import sqlite3
import tempfile
from pathlib import Path
from html import escape

import pandas as pd
import matplotlib.pyplot as plt

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
    Image,
    PageBreak,
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
    if value is None or pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):,.{decimals}f}"
    except Exception:
        return escape(str(value))


def pct(value):
    if value is None or pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):,.2f}%"
    except Exception:
        return escape(str(value))


def safe_text(value):
    if value is None or pd.isna(value):
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
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#17365D"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
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
# CHART GENERATOR
# ============================================================

def create_chart(df, company, column, title, ylabel, chart_dir):

    if column not in df.columns:
        return None

    plot_df = df[["year", column]].copy()

    plot_df[column] = pd.to_numeric(
        plot_df[column],
        errors="coerce"
    )

    plot_df["year"] = pd.to_numeric(
        plot_df["year"],
        errors="coerce"
    )

    plot_df = plot_df.dropna()

    if len(plot_df) < 2:
        return None

    plot_df = plot_df.tail(10)

    fig, ax = plt.subplots(figsize=(8, 3.2))

    ax.plot(
        plot_df["year"],
        plot_df[column],
        marker="o",
        linewidth=2,
    )

    ax.set_title(
        title,
        fontsize=12,
        fontweight="bold",
    )

    ax.set_xlabel("Financial Year")
    ax.set_ylabel(ylabel)

    ax.grid(
        True,
        alpha=0.25,
    )

    ax.set_xticks(
        plot_df["year"]
    )

    ax.tick_params(
        axis="both",
        labelsize=8,
    )

    fig.tight_layout()

    chart_path = (
        chart_dir /
        f"{company}_{column}.png"
    )

    fig.savefig(
        chart_path,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(fig)

    return chart_path


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
        raise ValueError(
            f"No financial data found for {company}"
        )

    df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce"
    )

    df = df.sort_values("year")

    latest = df.iloc[-1]

    # Temporary directory for charts
    with tempfile.TemporaryDirectory(
        prefix=f"{company}_charts_"
    ) as temp_dir:

        chart_dir = Path(temp_dir)

        # ----------------------------------------------------
        # DOCUMENT
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # 1. SNAPSHOT
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "1. Company Snapshot",
                section_style
            )
        )

        snapshot = [
            ["Attribute", "Value"],
            ["Company ID", company],
            [
                "Latest Financial Year",
                safe_text(latest["year"])
            ],
            [
                "Historical Records",
                str(len(df))
            ],
            [
                "First Available Year",
                safe_text(df["year"].min())
            ],
            [
                "Latest Available Year",
                safe_text(df["year"].max())
            ],
        ]

        story.append(
            make_table(
                snapshot,
                [3.0 * inch, 3.7 * inch]
            )
        )

        story.append(
            Spacer(1, 0.15 * inch)
        )

        # ----------------------------------------------------
        # 2. KPI DASHBOARD
        # ----------------------------------------------------

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
            [
                "Metric",
                "Latest Value",
                "Metric",
                "Latest Value",
            ]
        ]

        for i in range(0, len(metrics), 2):

            left = metrics[i]

            right = (
                metrics[i + 1]
                if i + 1 < len(metrics)
                else ("", "")
            )

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

        # ----------------------------------------------------
        # 3. HISTORICAL PERFORMANCE
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "3. Historical Financial Performance",
                section_style
            )
        )

        history = [
            [
                "Year",
                "Sales",
                "Net Profit",
                "Operating Profit",
                "EPS",
            ]
        ]

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

        # ----------------------------------------------------
        # 4. FINANCIAL TREND CHARTS
        # ----------------------------------------------------

        story.append(
            PageBreak()
        )

        story.append(
            Paragraph(
                "4. Financial Trend Analysis",
                section_style
            )
        )

        chart_specs = [
            (
                "sales",
                "Revenue / Sales Trend",
                "Sales",
            ),
            (
                "net_profit",
                "Net Profit Trend",
                "Net Profit",
            ),
            (
                "operating_profit",
                "Operating Profit Trend",
                "Operating Profit",
            ),
            (
                "eps",
                "EPS Trend",
                "EPS",
            ),
        ]

        charts_added = 0

        for column, title, ylabel in chart_specs:

            chart = create_chart(
                df,
                company,
                column,
                title,
                ylabel,
                chart_dir,
            )

            if chart:

                story.append(
                    Paragraph(
                        title,
                        body_style
                    )
                )

                story.append(
                    Image(
                        str(chart),
                        width=6.8 * inch,
                        height=2.65 * inch,
                    )
                )

                story.append(
                    Spacer(
                        1,
                        0.08 * inch
                    )
                )

                charts_added += 1

        if charts_added == 0:

            story.append(
                Paragraph(
                    "Insufficient historical data available "
                    "for trend visualization.",
                    body_style
                )
            )

        # ----------------------------------------------------
        # 5. GROWTH
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "5. Growth & Compounding Analysis",
                section_style
            )
        )

        growth_fields = [
            ("Revenue CAGR — 5 Year", "revenue_cagr_5y"),
            ("PAT CAGR — 5 Year", "pat_cagr_5y"),
            ("EPS CAGR — 5 Year", "eps_cagr_5y"),
            ("FCF CAGR — 5 Year", "fcf_cagr_5y"),
        ]

        growth = [
            ["Growth KPI", "Value"]
        ]

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
                "Growth metrics are interpreted together with "
                "profitability and cash-flow quality rather than "
                "in isolation.",
                small_style
            )
        )

        # ----------------------------------------------------
        # 6. PROFITABILITY
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "6. Profitability & Return Profile",
                section_style
            )
        )

        profitability = [
            ["Metric", "Value"],
            [
                "ROE",
                pct(latest.get("return_on_equity_pct"))
            ],
            [
                "ROCE",
                pct(latest.get("roce_pct"))
            ],
            [
                "Net Profit Margin",
                pct(latest.get("net_profit_margin_pct"))
            ],
            [
                "Operating Margin",
                pct(latest.get("operating_margin_pct"))
            ],
            [
                "Return on Assets",
                pct(latest.get("return_on_assets_pct"))
            ],
        ]

        story.append(
            make_table(
                profitability,
                [4.0 * inch, 2.0 * inch]
            )
        )

        # ----------------------------------------------------
        # 7. VALUATION
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "7. Valuation Assessment",
                section_style
            )
        )

        valuation = [
            ["Valuation Metric", "Latest Value"],
            ["P/E", fmt(latest.get("pe_ratio"))],
            ["P/B", fmt(latest.get("pb_ratio"))],
            ["EV / EBITDA", fmt(latest.get("ev_ebitda"))],
            [
                "Earnings Yield",
                pct(latest.get("earnings_yield_pct"))
            ],
            [
                "Enterprise Value",
                fmt(latest.get("enterprise_value"))
            ],
        ]

        story.append(
            make_table(
                valuation,
                [4.0 * inch, 2.0 * inch]
            )
        )

        # ----------------------------------------------------
        # 8. LEVERAGE
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "8. Leverage & Financial Risk",
                section_style
            )
        )

        leverage = [
            ["Risk Metric", "Value"],
            [
                "Debt / Equity",
                fmt(latest.get("debt_to_equity"))
            ],
            [
                "Interest Coverage",
                fmt(latest.get("interest_coverage"))
            ],
            [
                "Current Ratio",
                fmt(latest.get("current_ratio"))
            ],
            [
                "Quick Ratio",
                fmt(latest.get("quick_ratio"))
            ],
            [
                "Net Debt",
                fmt(latest.get("net_debt"))
            ],
        ]

        story.append(
            make_table(
                leverage,
                [4.0 * inch, 2.0 * inch]
            )
        )

        # ----------------------------------------------------
        # 9. CASH FLOW
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "9. Cash Flow & Capital Allocation",
                section_style
            )
        )

        if (
            not cashflow.empty
            and "company_id" in cashflow.columns
        ):

            cf = cashflow[
                cashflow["company_id"].astype(str)
                == company
            ]

            if not cf.empty:

                cf = cf.iloc[0]

                cf_data = [
                    ["Metric", "Value"]
                ]

                for field in [
                    "free_cash_flow",
                    "fcf_conversion",
                    "cfo_quality",
                    "capital_allocation",
                ]:

                    if field in cf.index:

                        cf_data.append([
                            field.replace(
                                "_",
                                " "
                            ).title(),
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
                        "No additional cash-flow intelligence "
                        "record was available for this company.",
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

        # ----------------------------------------------------
        # 10. PROS & CONS
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "10. Investment Strengths & Risks",
                section_style
            )
        )

        if (
            not pros.empty
            and "company_id" in pros.columns
        ):

            company_pros = pros[
                (
                    pros["company_id"].astype(str)
                    == company
                )
                &
                (
                    pros["type"].astype(str).str.lower()
                    == "pro"
                )
            ].head(5)

            company_cons = pros[
                (
                    pros["company_id"].astype(str)
                    == company
                )
                &
                (
                    pros["type"].astype(str).str.lower()
                    == "con"
                )
            ].head(5)

            story.append(
                Paragraph(
                    "<b>Strengths</b>",
                    body_style
                )
            )

            if not company_pros.empty:

                for _, row in company_pros.iterrows():

                    story.append(
                        Paragraph(
                            "• " +
                            safe_text(row.get("text")),
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

            story.append(
                Spacer(
                    1,
                    0.08 * inch
                )
            )

            story.append(
                Paragraph(
                    "<b>Risks / Cons</b>",
                    body_style
                )
            )

            if not company_cons.empty:

                for _, row in company_cons.iterrows():

                    story.append(
                        Paragraph(
                            "• " +
                            safe_text(row.get("text")),
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

        # ----------------------------------------------------
        # 11. ANALYST SUMMARY
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "11. Analyst Summary",
                section_style
            )
        )

        summary_parts = [
            (
                f"{company} has {len(df)} historical financial "
                "records available in the analytical database."
            ),
            (
                f"The latest financial year represented in the "
                f"dataset is {safe_text(latest['year'])}."
            ),
            (
                f"Latest reported sales are "
                f"{fmt(latest.get('sales'))} and net profit is "
                f"{fmt(latest.get('net_profit'))}."
            ),
            (
                f"Return on equity is "
                f"{pct(latest.get('return_on_equity_pct'))}, "
                f"while debt-to-equity is "
                f"{fmt(latest.get('debt_to_equity'))}."
            ),
            (
                f"The valuation snapshot shows P/E of "
                f"{fmt(latest.get('pe_ratio'))} and P/B of "
                f"{fmt(latest.get('pb_ratio'))}."
            ),
        ]

        for text in summary_parts:

            story.append(
                Paragraph(
                    text,
                    body_style
                )
            )

        # ----------------------------------------------------
        # 12. METHODOLOGY
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "12. Data & Methodology Note",
                section_style
            )
        )

        story.append(
            Paragraph(
                "This tearsheet is generated from the Nifty100 "
                "Financial Intelligence analytical database and "
                "derived output files. Historical metrics are "
                "summarized from the available company-level "
                "financial records. Trend charts use the latest "
                "available historical observations in the database.",
                small_style
            )
        )

        story.append(
            Paragraph(
                "Metrics are presented for analytical and educational "
                "purposes. This report is not investment advice and "
                "should not be treated as a recommendation to buy "
                "or sell any security.",
                small_style
            )
        )

        # ----------------------------------------------------
        # BUILD PDF
        # ----------------------------------------------------

        doc.build(
            story,
            onFirstPage=footer,
            onLaterPages=footer,
        )

    size_kb = pdf.stat().st_size / 1024

    print(
        f"{company} Done ({size_kb:.1f} KB)"
    )


# ============================================================
# BATCH GENERATION
# ============================================================

if __name__ == "__main__":

    success = 0
    failed = []

    print("=" * 60)
    print("GENERATING ALL NIFTY100 TEARSHEETS")
    print("=" * 60)

    for company in companies:

        try:

            build_pdf(company)

            success += 1

        except Exception as e:

            failed.append(
                (company, str(e))
            )

            print(
                f"FAILED: {company} -> {e}"
            )

    print()
    print("=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)

    print("Expected :", len(companies))
    print("Generated:", success)
    print("Failed   :", len(failed))

    if failed:

        print("\nFailures:")

        for company, error in failed:

            print(
                company,
                "->",
                error
            )

    print()
    print(
        "Tearsheet generation completed:",
        success
    )
