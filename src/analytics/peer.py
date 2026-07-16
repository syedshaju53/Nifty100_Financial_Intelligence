import pandas as pd


METRICS = [
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover"
]


def calculate_peer_percentiles(master_df, peer_df):

    records = []

    # Merge peer groups with financial data
    merged = peer_df.merge(
        master_df,
        on="company_id",
        how="left"
    )

    # Process each peer group
    for peer_group in merged["peer_group_name"].dropna().unique():

        group = merged[
            merged["peer_group_name"] == peer_group
        ].copy()

        if len(group) == 0:
            continue

        for metric in METRICS:

            if metric not in group.columns:
                continue

            # Lower D/E is better
            ascending = metric == "debt_to_equity"

            group["percentile"] = (
                group[metric]
                .rank(
                    pct=True,
                    ascending=ascending
                )
                * 100
            ).round(2)

            for _, row in group.iterrows():

                records.append({

                    "company_id": row["company_id"],

                    "peer_group_name": peer_group,

                    "metric": metric,

                    "value": row[metric],

                    "percentile_rank": row["percentile"],

                    "year": row["year"]

                })

    return pd.DataFrame(records)