import pandas as pd

df = pd.read_excel("data/raw/companies.xlsx", header=None)

print(df.head(10))