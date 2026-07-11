from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[2]

sys.path.append(str(BASE_DIR))

from src.etl.db_loader import load_all_tables

load_all_tables()

