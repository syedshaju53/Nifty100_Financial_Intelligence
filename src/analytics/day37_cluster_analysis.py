import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# DAY 37 — CLUSTER PROFILING & STATISTICS
# ============================================================

print("=" * 60)
print("DAY 37 — CLUSTER PROFILING & STATISTICS")
print("=" * 60)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "output"
REPORT_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

conn = sqlite3.connect(DB_PATH)


master = pd.read_sql(
    "SELECT * FROM master_financials",
    conn
)

clusters = pd.read_csv(
    OUTPUT_DIR / "cluster_labels.csv"
)

sectors = pd.read_sql(
    "SELECT * FROM sectors",
    conn
)


# ============================================================
# CLEAN IDS
# ============================================================

for df in [master, clusters]:

    if "company_id" in df.columns:

        df["company_id"] = (
            df["company_id"]
            .astype(str)
            .str.strip()
            .str.upper()
        )


# ============================================================
# BASIC COUNTS
# ============================================================

master_ids = set(
    master["company_id"].dropna()
)

cluster_ids = set(
    clusters["company_id"].dropna()
)


print(
    f"Master financial rows : {len(master)}"
)

print(
    f"Master companies      : {len(master_ids)}"
)

print(
    f"Cluster companies     : {len(cluster_ids)}"
)

print(
    f"Clusters              : {clusters['cluster_id'].nunique()}"
)


# ============================================================
# DATA COVERAGE CHECK
# ============================================================

missing_from_master = sorted(
    cluster_ids - master_ids
)

extra_in_master = sorted(
    master_ids - cluster_ids
)


print("\nData coverage check:")

print(
    "Missing from master  :",
    missing_from_master
)

print(
    "Extra in master      :",
    extra_in_master
)


# ============================================================
# LATEST YEAR
# ============================================================

master["year_num"] = pd.to_numeric(
    master["year"],
    errors="coerce"
)

latest_year = (
    master["year_num"]
    .max()
)

latest = master[
    master["year_num"] == latest_year
].copy()


print(
    f"\nLatest year          : {int(latest_year)}"
)

print(
    f"Latest-year companies: {latest['company_id'].nunique()}"
)


# ============================================================
# MERGE CLUSTERS
# ============================================================

latest = latest.merge(
    clusters[
        [
            "company_id",
            "cluster_id",
            "cluster_name"
        ]
    ],
    on="company_id",
    how="left"
)


# ============================================================
# CLUSTER PROFILE
# ============================================================

print("\nGenerating cluster profiles...")


profile_metrics = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct"
]


for col in profile_metrics:

    if col not in latest.columns:

        latest[col] = np.nan

    latest[col] = pd.to_numeric(
        latest[col],
        errors="coerce"
    )


profile_rows = []


for cluster_id, group in latest.groupby(
    ["cluster_id", "cluster_name"],
    dropna=False
):

    cid, cname = cluster_id

    row = {
        "cluster_id": cid,
        "cluster_name": cname,
        "company_count": group["company_id"].nunique()
    }


    for metric in profile_metrics:

        row[f"{metric}_mean"] = (
            group[metric].mean()
        )

        row[f"{metric}_median"] = (
            group[metric].median()
        )


    profile_rows.append(row)


cluster_profile = pd.DataFrame(
    profile_rows
)


# ============================================================
# ROUND
# ============================================================

numeric_profile_cols = [
    c
    for c in cluster_profile.columns
    if c not in [
        "cluster_id",
        "cluster_name"
    ]
]

cluster_profile[
    numeric_profile_cols
] = cluster_profile[
    numeric_profile_cols
].round(2)


print("\nCluster profile:")

print(
    cluster_profile.to_string(
        index=False
    )
)


# ============================================================
# SAVE CLUSTER PROFILE
# ============================================================

profile_path = (
    OUTPUT_DIR /
    "cluster_profiles.csv"
)

cluster_profile.to_csv(
    profile_path,
    index=False
)

print(
    f"\nCluster profiles saved : {profile_path}"
)


# ============================================================
# CORRELATION HEATMAP
# ============================================================

print(
    "\nGenerating correlation heatmap..."
)


correlation_metrics = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "fcf_cagr_5yr",
    "dividend_yield_pct"
]


available_metrics = [
    c
    for c in correlation_metrics
    if c in latest.columns
]


missing_metrics = [
    c
    for c in correlation_metrics
    if c not in latest.columns
]


if missing_metrics:

    print(
        "\nWARNING: Missing KPI columns:"
    )

    print(
        missing_metrics
    )


corr = latest[
    available_metrics
].corr()


plt.figure(
    figsize=(12, 9)
)

plt.imshow(
    corr,
    aspect="auto"
)

plt.xticks(
    range(len(corr.columns)),
    corr.columns,
    rotation=90
)

plt.yticks(
    range(len(corr.columns)),
    corr.columns
)

plt.title(
    "Nifty100 Financial KPI Correlation"
)

plt.colorbar()

plt.tight_layout()


heatmap_path = (
    REPORT_DIR /
    "correlation_heatmap.png"
)

plt.savefig(
    heatmap_path,
    dpi=150
)

plt.close()


print(
    f"Correlation heatmap saved : {heatmap_path}"
)


# ============================================================
# SECTOR OUTLIERS
# ============================================================

print(
    "\nGenerating sector outlier report..."
)


# Try to identify sector column
sector_column = None

for candidate in [
    "broad_sector",
    "sector",
    "sector_name"
]:

    if candidate in sectors.columns:

        sector_column = candidate
        break


if sector_column is None:

    print(
        "WARNING: Sector column not found."
    )

    outlier_report = pd.DataFrame()

else:

    sector_cols = [
        c
        for c in [
            "company_id",
            sector_column
        ]
        if c in sectors.columns
    ]

    sector_map = sectors[
        sector_cols
    ].drop_duplicates(
        "company_id"
    )

    sector_map = sector_map.rename(
        columns={
            sector_column:
            "broad_sector"
        }
    )


    outlier_data = latest.merge(
        sector_map[
            [
                "company_id",
                "broad_sector"
            ]
        ],
        on="company_id",
        how="left"
    )


    outlier_metrics = [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "fcf_cagr_5yr",
        "operating_profit_margin_pct"
    ]


    outlier_rows = []


    for sector, group in outlier_data.groupby(
        "broad_sector",
        dropna=False
    ):

        for metric in outlier_metrics:

            if metric not in group.columns:
                continue

            values = pd.to_numeric(
                group[metric],
                errors="coerce"
            )

            if values.notna().sum() < 3:
                continue

            mean = values.mean()
            std = values.std()

            if pd.isna(std) or std == 0:
                continue


            z_scores = (
                values - mean
            ) / std


            for idx, z in z_scores.items():

                if pd.isna(z):
                    continue

                if abs(z) >= 3:

                    value = values.loc[idx]

                    if abs(z) >= 4:
                        severity = "EXTREME"

                    elif abs(z) >= 3:
                        severity = "HIGH"

                    else:
                        severity = "MEDIUM"


                    outlier_rows.append({
                        "company_id":
                            outlier_data.loc[
                                idx,
                                "company_id"
                            ],

                        "broad_sector":
                            sector,

                        "metric":
                            metric,

                        "value":
                            round(value, 3),

                        "sector_mean":
                            round(mean, 3),

                        "sector_std":
                            round(std, 3),

                        "z_score":
                            round(z, 3),

                        "severity":
                            severity
                    })


    outlier_report = pd.DataFrame(
        outlier_rows
    )


# ============================================================
# SAVE OUTLIERS
# ============================================================

outlier_path = (
    OUTPUT_DIR /
    "outlier_report.csv"
)


outlier_report.to_csv(
    outlier_path,
    index=False
)


print(
    f"\nOutliers detected : {len(outlier_report)}"
)

print(
    f"Outlier report saved : {outlier_path}"
)


if not outlier_report.empty:

    print("\nTop outliers:")

    print(
        outlier_report
        .sort_values(
            "z_score",
            key=lambda x: x.abs(),
            ascending=False
        )
        .head(10)
        .to_string(index=False)
    )


# ============================================================
# PORTFOLIO STATISTICS
# ============================================================

print(
    "\nGenerating portfolio statistics..."
)


portfolio_metrics = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "fcf_cagr_5yr",
    "dividend_yield_pct"
]


stats_rows = []


for metric in portfolio_metrics:

    if metric not in latest.columns:
        continue

    values = pd.to_numeric(
        latest[metric],
        errors="coerce"
    ).dropna()


    if values.empty:
        continue


    stats_rows.append({
        "kpi": metric,
        "count": int(values.count()),
        "p10": values.quantile(0.10),
        "p25": values.quantile(0.25),
        "p50": values.quantile(0.50),
        "p75": values.quantile(0.75),
        "p90": values.quantile(0.90),
        "mean": values.mean(),
        "std": values.std()
    })


portfolio_stats = pd.DataFrame(
    stats_rows
)


if not portfolio_stats.empty:

    portfolio_stats[
        [
            "p10",
            "p25",
            "p50",
            "p75",
            "p90",
            "mean",
            "std"
        ]
    ] = portfolio_stats[
        [
            "p10",
            "p25",
            "p50",
            "p75",
            "p90",
            "mean",
            "std"
        ]
    ].round(3)


print("\nPortfolio statistics:")

print(
    portfolio_stats.to_string(
        index=False
    )
)


# ============================================================
# SAVE PORTFOLIO STATS
# ============================================================

portfolio_path = (
    OUTPUT_DIR /
    "portfolio_stats.csv"
)

portfolio_stats.to_csv(
    portfolio_path,
    index=False
)


print(
    f"\nPortfolio statistics saved : {portfolio_path}"
)


# ============================================================
# FINAL VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("DAY 37 FINAL VALIDATION")
print("=" * 60)


print(
    f"Universe companies       : {len(cluster_ids)}"
)

print(
    f"Cluster companies        : {clusters['company_id'].nunique()}"
)

print(
    f"Master companies         : {len(master_ids)}"
)

print(
    f"Latest-year companies    : {latest['company_id'].nunique()}"
)

print(
    f"Clusters profiled        : {cluster_profile['cluster_id'].nunique()}"
)

print(
    f"Outlier rows             : {len(outlier_report)}"
)

print(
    f"KPI statistics           : {len(portfolio_stats)}"
)


print("\nData coverage gap:")

print(
    f"Missing master companies : {len(missing_from_master)}"
)

if missing_from_master:

    print(
        "Missing companies       :",
        missing_from_master
    )


# ============================================================
# REQUIRED FILES
# ============================================================

required_files = [
    profile_path,
    outlier_path,
    portfolio_path,
    heatmap_path
]


print("\nRequired files:")


all_files_ok = True


for path in required_files:

    exists = path.exists()

    print(
        ("PASS " if exists else "FAIL "),
        path
    )

    if not exists:
        all_files_ok = False


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 60)


if (
    all_files_ok
    and len(portfolio_stats) >= 10
    and len(missing_from_master) == 0
):

    print(
        "DAY 37 COMPLETED SUCCESSFULLY"
    )

elif (
    all_files_ok
    and len(missing_from_master) > 0
):

    print(
        "DAY 37 COMPLETED WITH DATA COVERAGE REVIEW"
    )

    print(
        "Missing companies require source-data remediation:"
    )

    print(
        missing_from_master
    )

else:

    print(
        "DAY 37 REQUIRES REVIEW"
    )


print("=" * 60)


conn.close()