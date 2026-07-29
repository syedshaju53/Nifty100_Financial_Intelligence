import pandas as pd

df = pd.read_excel("data/raw/analysis.xlsx")

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nUnique Companies:", df.iloc[:, 0].nunique())