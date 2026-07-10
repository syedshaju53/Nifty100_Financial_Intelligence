from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from src.etl.loader import load_excel
from src.etl.cleaner import clean_dataframe,save_clean_data

df = load_excel("companies.xlsx")

clean_df = clean_dataframe(df)

print(clean_df.head())

save_clean_data(clean_df, "companies_clean.xlsx")