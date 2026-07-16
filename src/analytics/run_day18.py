import sqlite3
import pandas as pd
from pathlib import Path

from src.analytics.peer import calculate_peer_percentiles

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

master = pd.read_sql(
    "SELECT * FROM master_financials",
    conn
)

peer = pd.read_sql(
    "SELECT * FROM peer_groups",
    conn
)

print("Master Rows :", len(master))
print("Peer Groups :", len(peer))

peer_percentiles = calculate_peer_percentiles(
    master,
    peer
)

print("\nPeer Percentile Records :", len(peer_percentiles))

print("\nPreview\n")

print(peer_percentiles.head())

peer_percentiles.to_sql(
    "peer_percentiles",
    conn,
    if_exists="replace",
    index=False
)

print("\npeer_percentiles table created!")

output_dir = BASE_DIR / "output"
output_dir.mkdir(exist_ok=True)

peer_percentiles.to_csv(
    output_dir / "peer_percentiles.csv",
    index=False
)

print("\nCSV Exported!")

conn.close()