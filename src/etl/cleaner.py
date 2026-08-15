import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def clean_dataframe(df):
    """
    Perform basic cleaning operations on a DataFrame.
    """

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Remove rows where every column is empty
    df = df.dropna(how="all")

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # Trim whitespace from text columns
    text_columns = df.select_dtypes(include=["object", "string"]).columns

    for col in text_columns:
        df[col] = df[col].str.strip()

    return df

def save_clean_data(df, filename):
    """
    Save cleaned data to data/processed.
    """

    PROCESSED_DIR.mkdir(exist_ok=True)

    output_path = PROCESSED_DIR / filename

    df.to_excel(output_path, index=False)

    print(f"Saved: {output_path}")