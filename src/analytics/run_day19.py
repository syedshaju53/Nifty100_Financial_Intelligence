import sqlite3
import pandas as pd
from pathlib import Path

from src.analytics.radar import (
    create_radar,
    METRICS
)

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

REPORT_DIR = BASE_DIR / "reports" / "radar_charts"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

conn = sqlite3.connect(DB_PATH)

master = pd.read_sql(
    "SELECT * FROM master_financials",
    conn
)

peer = pd.read_sql(
    "SELECT * FROM peer_groups",
    conn
)

merged = peer.merge(
    master,
    on="company_id",
    how="left"
)

latest = (
    merged
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
)

count = 0

for peer_group in latest["peer_group_name"].dropna().unique():

    group = latest[
        latest["peer_group_name"] == peer_group
    ]

    peer_avg = (
        group[METRICS]
        .mean(numeric_only=True)
    )

    for _, row in group.iterrows():

        values = []

        averages = []

        for metric in METRICS:

            values.append(row[metric])
            averages.append(peer_avg[metric])

        output = REPORT_DIR / f"{row['company_id']}_radar.png"

        create_radar(
            row["company_id"],
            values,
            averages,
            output
        )

        count += 1

print()

print("Radar Charts Generated :", count)

print("Saved to")

print(REPORT_DIR)

conn.close()