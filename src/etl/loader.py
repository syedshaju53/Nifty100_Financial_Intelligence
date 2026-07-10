from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DATA = BASE_DIR / "data" / "raw"


def load_excel(file_name, header=1):

    file_path = RAW_DATA / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"{file_name} not found in {RAW_DATA}")

    df = pd.read_excel(file_path, header=header)

    print("=" * 50)
    print(f"Loaded : {file_name}")
    print(f"Rows   : {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print("=" * 50)

    return df