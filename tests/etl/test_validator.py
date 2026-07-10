from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from src.etl.loader import load_excel
from src.etl.validator import validate_dataframe

df = load_excel("companies.xlsx")
print(df.columns.tolist())

report = validate_dataframe(df)


report.to_csv(
    "outputs/validation_failures.csv",
    index=False
)

print("Validation report saved successfully.")
