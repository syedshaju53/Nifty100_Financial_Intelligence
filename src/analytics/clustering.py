"""
Day 36 — KMeans Financial Clustering

Clusters all 92 Nifty 100 companies into 5 financial archetypes.

Features:
    - return_on_equity_pct
    - debt_to_equity
    - revenue_cagr_5yr
    - fcf_cagr_5yr
    - operating_profit_margin_pct

Outputs:
    output/cluster_labels.csv
    output/cluster_profiles.csv
    reports/elbow_plot.png
"""

from pathlib import Path
import re
import sqlite3

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

N_CLUSTERS = 5
RANDOM_STATE = 42

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """Load company, sector and financial data from SQLite."""

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn,
    )

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn,
    )

    master_exists = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='master_financials'
        """
    ).fetchone()

    if master_exists:

        financials = pd.read_sql(
            "SELECT * FROM master_financials",
            conn,
        )

        print(
            f"Master Financial Rows : {len(financials)}"
        )

    else:

        print(
            "master_financials table not found."
        )

        financials = pd.read_sql(
            "SELECT * FROM profit_loss",
            conn,
        )

    conn.close()

    return companies, sectors, financials


# ============================================================
# NORMALISE YEAR
# ============================================================

def normalise_year(value):
    """Convert a financial year value into a numeric year."""

    if pd.isna(value):
        return np.nan

    text = str(value).strip()

    match = re.search(
        r"(19|20)\d{2}",
        text,
    )

    if match:
        return float(match.group())

    return np.nan


# ============================================================
# CALCULATE FCF CAGR
# ============================================================

def calculate_fcf_cagr(financials):
    """Calculate five-year free-cash-flow CAGR by company."""

    df = financials.copy()

    if "company_id" not in df.columns:
        return pd.DataFrame(
            columns=[
                "company_id",
                "fcf_cagr_5yr",
            ]
        )

    if "year" not in df.columns:
        return pd.DataFrame(
            columns=[
                "company_id",
                "fcf_cagr_5yr",
            ]
        )

    # --------------------------------------------------------
    # If master_financials already contains FCF CAGR,
    # use it directly.
    # --------------------------------------------------------

    existing_fcf_columns = [
        "fcf_cagr_5yr",
        "fcf_cagr",
    ]

    for column in existing_fcf_columns:

        if column in df.columns:

            result = df[
                [
                    "company_id",
                    column,
                ]
            ].copy()

            result[column] = pd.to_numeric(
                result[column],
                errors="coerce",
            )

            result = (
                result
                .sort_values(
                    "company_id"
                )
                .groupby(
                    "company_id",
                    as_index=False,
                )
                .tail(1)
            )

            result = result.rename(
                columns={
                    column: "fcf_cagr_5yr"
                }
            )

            return result[
                [
                    "company_id",
                    "fcf_cagr_5yr",
                ]
            ]

    # --------------------------------------------------------
    # Otherwise calculate from CFO and Capex.
    # --------------------------------------------------------

    cfo_candidates = [
        "cash_from_operating_activity",
        "cash_from_operating_activities",
        "cash_flow_from_operating_activity",
        "cash_flow_from_operating_activities",
        "operating_cash_flow",
        "cfo",
    ]

    capex_candidates = [
        "capital_expenditure",
        "capital_expenditures",
        "capex",
        "capital_expenditure_cash_flow",
        "purchase_of_fixed_assets",
    ]

    cfo_column = None
    capex_column = None

    for column in cfo_candidates:

        if column in df.columns:
            cfo_column = column
            break

    for column in capex_candidates:

        if column in df.columns:
            capex_column = column
            break

    if cfo_column is None:

        return pd.DataFrame(
            columns=[
                "company_id",
                "fcf_cagr_5yr",
            ]
        )

    df["cfo_value"] = pd.to_numeric(
        df[cfo_column],
        errors="coerce",
    )

    if capex_column is not None:

        df["capex_value"] = pd.to_numeric(
            df[capex_column],
            errors="coerce",
        )

        df["fcf_value"] = (
            df["cfo_value"]
            - df["capex_value"].abs()
        )

    else:

        df["fcf_value"] = df["cfo_value"]

    df["year_num"] = df["year"].apply(
        normalise_year
    )

    df = df.dropna(
        subset=[
            "company_id",
            "year_num",
            "fcf_value",
        ]
    )

    results = []

    for company_id, group in df.groupby(
        "company_id"
    ):

        group = group.sort_values(
            "year_num"
        )

        if len(group) < 2:

            results.append(
                {
                    "company_id": company_id,
                    "fcf_cagr_5yr": np.nan,
                }
            )

            continue

        latest = group.iloc[-1]

        target_year = (
            latest["year_num"] - 5
        )

        distances = (
            group["year_num"]
            - target_year
        ).abs()

        previous = group.loc[
            distances.idxmin()
        ]

        previous_value = float(
            previous["fcf_value"]
        )

        latest_value = float(
            latest["fcf_value"]
        )

        years = (
            latest["year_num"]
            - previous["year_num"]
        )

        if (
            years <= 0
            or previous_value <= 0
            or latest_value <= 0
        ):

            cagr = np.nan

        else:

            cagr = (
                (
                    latest_value
                    / previous_value
                )
                ** (1 / years)
                - 1
            ) * 100

        results.append(
            {
                "company_id": company_id,
                "fcf_cagr_5yr": cagr,
            }
        )

    return pd.DataFrame(results)


# ============================================================
# PREPARE DATASET
# ============================================================

def prepare_dataset(
    companies,
    sectors,
    financials,
):
    """
    Prepare the clustering dataset.

    The companies table is the master universe, ensuring
    all 92 companies remain in the dataset even when
    financial records are incomplete.
    """

    companies = companies.copy()
    sectors = sectors.copy()
    financials = financials.copy()

    # --------------------------------------------------------
    # COMPANY IDS
    # --------------------------------------------------------

    companies["company_id"] = (
        companies["id"]
        .astype(str)
        .str.strip()
    )

    sectors["company_id"] = (
        sectors["company_id"]
        .astype(str)
        .str.strip()
    )

    financials["company_id"] = (
        financials["company_id"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # YEAR
    # --------------------------------------------------------

    financials["year_num"] = (
        financials["year"]
        .apply(normalise_year)
    )

    financials = financials.sort_values(
        [
            "company_id",
            "year_num",
        ]
    )

    # --------------------------------------------------------
    # LATEST FINANCIAL RECORD
    # --------------------------------------------------------

    latest = (
        financials
        .dropna(
            subset=["company_id"]
        )
        .groupby(
            "company_id",
            as_index=False,
        )
        .tail(1)
        .copy()
    )

    # --------------------------------------------------------
    # ENSURE REQUIRED FEATURES EXIST
    # --------------------------------------------------------

    financial_features = [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "operating_profit_margin_pct",
    ]

    for feature in financial_features:

        if feature not in latest.columns:

            latest[feature] = np.nan

    latest = latest[
        [
            "company_id",
            "return_on_equity_pct",
            "debt_to_equity",
            "revenue_cagr_5yr",
            "operating_profit_margin_pct",
        ]
    ]

    # --------------------------------------------------------
    # FCF CAGR
    # --------------------------------------------------------

    fcf_cagr = calculate_fcf_cagr(
        financials
    )

    latest = latest.merge(
        fcf_cagr,
        on="company_id",
        how="left",
    )

    # --------------------------------------------------------
    # START WITH ALL COMPANIES
    # --------------------------------------------------------

    dataset = companies[
        ["company_id"]
    ].drop_duplicates()

    # --------------------------------------------------------
    # MERGE FINANCIAL DATA
    # --------------------------------------------------------

    dataset = dataset.merge(
        latest,
        on="company_id",
        how="left",
    )

    # --------------------------------------------------------
    # MERGE SECTOR
    # --------------------------------------------------------

    sector_columns = [
        "company_id"
    ]

    if "broad_sector" in sectors.columns:

        sector_columns.append(
            "broad_sector"
        )

    if "sub_sector" in sectors.columns:

        sector_columns.append(
            "sub_sector"
        )

    sector_data = (
        sectors[
            sector_columns
        ]
        .drop_duplicates(
            "company_id"
        )
    )

    dataset = dataset.merge(
        sector_data,
        on="company_id",
        how="left",
    )

    # --------------------------------------------------------
    # BROAD SECTOR
    # --------------------------------------------------------

    if "broad_sector" not in dataset.columns:

        dataset["broad_sector"] = (
            "Unknown"
        )

    dataset["broad_sector"] = (
        dataset["broad_sector"]
        .fillna("Unknown")
    )

    # --------------------------------------------------------
    # NUMERIC FEATURES
    # --------------------------------------------------------

    for feature in FEATURES:

        if feature not in dataset.columns:

            dataset[feature] = np.nan

        dataset[feature] = pd.to_numeric(
            dataset[feature],
            errors="coerce",
        )

    return dataset


# ============================================================
# SECTOR MEDIAN IMPUTATION
# ============================================================

def sector_median_imputation(df):
    """
    Fill missing values using broad-sector medians.

    If a sector has no value for a feature, the overall
    median is used as a fallback.
    """

    df = df.copy()

    for feature in FEATURES:

        sector_medians = (
            df.groupby(
                "broad_sector"
            )[feature]
            .transform("median")
        )

        df[feature] = (
            df[feature]
            .fillna(sector_medians)
        )

        overall_median = (
            df[feature]
            .median()
        )

        if pd.isna(
            overall_median
        ):

            overall_median = 0.0

        df[feature] = (
            df[feature]
            .fillna(
                overall_median
            )
        )

    return df


# ============================================================
# EXTREME VALUE HANDLING
# ============================================================

def clip_extreme_values(df):
    """
    Limit extreme ratio values to the 1st and 99th percentiles.

    This prevents extreme accounting ratios from dominating
    the StandardScaler and KMeans model.
    """

    df = df.copy()

    for feature in FEATURES:

        lower = df[
            feature
        ].quantile(0.01)

        upper = df[
            feature
        ].quantile(0.99)

        if pd.notna(lower) and pd.notna(upper):

            df[feature] = (
                df[feature]
                .clip(
                    lower=lower,
                    upper=upper,
                )
            )

    return df


# ============================================================
# ELBOW PLOT
# ============================================================

def generate_elbow_plot(
    X_scaled
):
    """Generate and save the KMeans elbow plot."""

    import matplotlib.pyplot as plt

    k_values = range(2, 11)

    inertias = []

    for k in k_values:

        model = KMeans(
            n_clusters=k,
            random_state=RANDOM_STATE,
            n_init=20,
        )

        model.fit(
            X_scaled
        )

        inertias.append(
            model.inertia_
        )

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        list(k_values),
        inertias,
        marker="o",
    )

    plt.axvline(
        x=5,
        linestyle="--",
        label="Selected k=5",
    )

    plt.title(
        "KMeans Elbow Analysis"
    )

    plt.xlabel(
        "Number of Clusters"
    )

    plt.ylabel(
        "Inertia"
    )

    plt.xticks(
        list(k_values)
    )

    plt.grid(
        alpha=0.3
    )

    plt.legend()

    plt.tight_layout()

    output_path = (
        REPORTS_DIR
        / "elbow_plot.png"
    )

    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"\nElbow plot saved : "
        f"{output_path}"
    )


# ============================================================
# CLUSTER NAMES
# ============================================================

def assign_cluster_names(
    profile
):
    """Assign descriptive names based on cluster characteristics."""

    names = {}

    remaining = set(
        profile.index
    )

    # --------------------------------------------------------
    # Emerging Growth
    # --------------------------------------------------------

    if remaining:

        growth_score = (
            profile.loc[
                list(remaining),
                "revenue_cagr_5yr",
            ]
        )

        growth_cluster = (
            growth_score.idxmax()
        )

        names[
            growth_cluster
        ] = "Emerging Growth"

        remaining.remove(
            growth_cluster
        )

    # --------------------------------------------------------
    # High Quality
    # --------------------------------------------------------

    if remaining:

        quality = profile.loc[
            list(remaining)
        ]

        quality_score = (
            quality[
                "return_on_equity_pct"
            ]
            + quality[
                "operating_profit_margin_pct"
            ]
            - quality[
                "debt_to_equity"
            ]
        )

        quality_cluster = (
            quality_score.idxmax()
        )

        names[
            quality_cluster
        ] = "High-Quality Compounders"

        remaining.remove(
            quality_cluster
        )

    # --------------------------------------------------------
    # Leveraged / Financial Growth
    # --------------------------------------------------------

    if remaining:

        leverage_cluster = (
            profile.loc[
                list(remaining),
                "debt_to_equity",
            ].idxmax()
        )

        names[
            leverage_cluster
        ] = "Leveraged / Financial Growth"

        remaining.remove(
            leverage_cluster
        )

    # --------------------------------------------------------
    # High Margin
    # --------------------------------------------------------

    if remaining:

        margin_cluster = (
            profile.loc[
                list(remaining),
                "operating_profit_margin_pct",
            ].idxmax()
        )

        names[
            margin_cluster
        ] = "High-Margin Defensives"

        remaining.remove(
            margin_cluster
        )

    # --------------------------------------------------------
    # Remaining
    # --------------------------------------------------------

    for cluster_id in remaining:

        names[
            cluster_id
        ] = "Value / Turnaround"

    return names


# ============================================================
# RUN CLUSTERING
# ============================================================

def run_clustering():
    """Execute the complete Day 36 clustering workflow."""

    print("=" * 60)
    print("DAY 36 — KMEANS CLUSTERING")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    companies, sectors, financials = (
        load_data()
    )

    print(
        f"Financial Rows : "
        f"{len(financials)}"
    )

    print(
        f"Sector Rows    : "
        f"{len(sectors)}"
    )

    print(
        f"Companies      : "
        f"{len(companies)}"
    )

    # --------------------------------------------------------
    # PREPARE
    # --------------------------------------------------------

    data = prepare_dataset(
        companies,
        sectors,
        financials,
    )

    print(
        f"\nPrepared Companies : "
        f"{len(data)}"
    )

    # --------------------------------------------------------
    # VALIDATE COMPANY UNIVERSE
    # --------------------------------------------------------

    # IMPORTANT:
    # companies table uses "id".
    # prepared dataset uses "company_id".

    expected_ids = set(
        companies[
            "id"
        ]
        .astype(str)
        .str.strip()
    )

    actual_ids = set(
        data[
            "company_id"
        ]
        .astype(str)
        .str.strip()
    )

    missing = sorted(
        expected_ids
        - actual_ids
    )

    extra = sorted(
        actual_ids
        - expected_ids
    )

    if missing:

        print(
            "\nWARNING: Missing companies:"
        )

        print(
            missing
        )

    if extra:

        print(
            "\nWARNING: Unexpected companies:"
        )

        print(
            extra
        )

    # --------------------------------------------------------
    # COMPANY COUNT MUST BE 92
    # --------------------------------------------------------

    if len(data) != len(companies):

        raise ValueError(
            "\nCompany universe mismatch.\n"
            f"Expected : {len(companies)}\n"
            f"Actual   : {len(data)}\n"
            f"Missing  : {missing}"
        )

    print(
        "\nAll companies retained."
    )

    # --------------------------------------------------------
    # IMPUTATION
    # --------------------------------------------------------

    print(
        "\nApplying sector median imputation..."
    )

    data = sector_median_imputation(
        data
    )

    # --------------------------------------------------------
    # CHECK MISSING VALUES
    # --------------------------------------------------------

    missing_values = (
        data[
            FEATURES
        ]
        .isna()
        .sum()
    )

    print(
        "\nMissing values after imputation:"
    )

    print(
        missing_values.to_string()
    )

    if (
        missing_values.sum()
        > 0
    ):

        raise ValueError(
            "Missing values remain "
            "after imputation."
        )

    # --------------------------------------------------------
    # EXTREME VALUE HANDLING
    # --------------------------------------------------------

    data = clip_extreme_values(
        data
    )

    # --------------------------------------------------------
    # STANDARD SCALER
    # --------------------------------------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        data[
            FEATURES
        ]
    )

    print(
        "\nStandardScaler applied."
    )

    # --------------------------------------------------------
    # ELBOW
    # --------------------------------------------------------

    generate_elbow_plot(
        X_scaled
    )

    # --------------------------------------------------------
    # KMEANS
    # --------------------------------------------------------

    print(
        "\nRunning KMeans with "
        "5 clusters..."
    )

    model = KMeans(
        n_clusters=5,
        random_state=42,
        n_init=20,
    )

    cluster_ids = (
        model.fit_predict(
            X_scaled
        )
    )

    data[
        "cluster_id"
    ] = cluster_ids

    # --------------------------------------------------------
    # DISTANCE FROM CENTROID
    # --------------------------------------------------------

    distances = model.transform(
        X_scaled
    )

    data[
        "distance_from_centroid"
    ] = distances[
        np.arange(
            len(data)
        ),
        cluster_ids,
    ]

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    cluster_profile = (
        data
        .groupby(
            "cluster_id"
        )[FEATURES]
        .mean()
    )

    cluster_names = (
        assign_cluster_names(
            cluster_profile
        )
    )

    data[
        "cluster_name"
    ] = data[
        "cluster_id"
    ].map(
        cluster_names
    )

    # --------------------------------------------------------
    # DISTRIBUTION
    # --------------------------------------------------------

    distribution = (
        data
        .groupby(
            [
                "cluster_id",
                "cluster_name",
            ]
        )
        .size()
        .reset_index(
            name="company_count"
        )
        .sort_values(
            "cluster_id"
        )
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "CLUSTER DISTRIBUTION"
    )

    print(
        "=" * 60
    )

    print(
        distribution.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # CLUSTER PROFILE
    # --------------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "CLUSTER PROFILE"
    )

    print(
        "=" * 60
    )

    print(
        cluster_profile
        .round(2)
        .to_string()
    )

    # --------------------------------------------------------
    # COMPANIES BY CLUSTER
    # --------------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "COMPANIES BY CLUSTER"
    )

    print(
        "=" * 60
    )

    for cluster_id in sorted(
        data[
            "cluster_id"
        ].unique()
    ):

        subset = data[
            data[
                "cluster_id"
            ]
            == cluster_id
        ].copy()

        cluster_name = (
            cluster_names[
                cluster_id
            ]
        )

        print(
            f"\nCluster {cluster_id} "
            f"— {cluster_name} "
            f"({len(subset)} companies)"
        )

        print(
            subset[
                [
                    "company_id",
                    "return_on_equity_pct",
                    "debt_to_equity",
                    "revenue_cagr_5yr",
                    "fcf_cagr_5yr",
                    "operating_profit_margin_pct",
                ]
            ]
            .sort_values(
                "company_id"
            )
            .round(2)
            .to_string(
                index=False
            )
        )

    # --------------------------------------------------------
    # SAVE CLUSTER LABELS
    # --------------------------------------------------------

    output = data[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid",
        ]
    ].copy()

    output = output.sort_values(
        "company_id"
    )

    cluster_output = (
        OUTPUT_DIR
        / "cluster_labels.csv"
    )

    output.to_csv(
        cluster_output,
        index=False,
    )

    # --------------------------------------------------------
    # SAVE CLUSTER PROFILES
    # --------------------------------------------------------

    profile_output = (
        cluster_profile
        .reset_index()
    )

    profile_output[
        "cluster_name"
    ] = profile_output[
        "cluster_id"
    ].map(
        cluster_names
    )

    profile_path = (
        OUTPUT_DIR
        / "cluster_profiles.csv"
    )

    profile_output.to_csv(
        profile_path,
        index=False,
    )

    # --------------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "FINAL VALIDATION"
    )

    print(
        "=" * 60
    )

    print(
        f"Expected companies      : "
        f"{len(companies)}"
    )

    print(
        f"Output companies        : "
        f"{len(output)}"
    )

    print(
        f"Unique companies        : "
        f"{output['company_id'].nunique()}"
    )

    print(
        f"Clusters created        : "
        f"{output['cluster_id'].nunique()}"
    )

    print(
        f"Unassigned companies    : "
        f"{output['cluster_id'].isna().sum()}"
    )

    print(
        f"Missing cluster names   : "
        f"{output['cluster_name'].isna().sum()}"
    )

    # --------------------------------------------------------
    # STRICT FINAL CHECK
    # --------------------------------------------------------

    if len(output) != 92:
        raise ValueError(
            "Final output does not contain "
            "92 companies."
        )

    if output[
        "company_id"
    ].nunique() != 92:
        raise ValueError(
            "Final output does not contain "
            "92 unique companies."
        )

    if output[
        "cluster_id"
    ].nunique() != 5:
        raise ValueError(
            "KMeans did not create "
            "exactly 5 clusters."
        )

    if output[
        "cluster_id"
    ].isna().any():
        raise ValueError(
            "Some companies are unassigned."
        )

    if output[
        "cluster_name"
    ].isna().any():
        raise ValueError(
            "Some companies have no "
            "cluster name."
        )

    print(
        "\nCluster labels saved : "
        f"{cluster_output}"
    )

    print(
        "Cluster profiles saved : "
        f"{profile_path}"
    )

    print(
        "\nDay 36 clustering "
        "completed successfully."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_clustering()