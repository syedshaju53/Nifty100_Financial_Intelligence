from src.etl.loader import load_excel

df = load_excel("companies.xlsx")

print(df.head())