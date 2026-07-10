from src.etl.normaliser import normalize_ticker, normalize_year

print(normalize_ticker(" tcs "))
print(normalize_ticker(" Reliance "))
print(normalize_year("Mar-23"))
print(normalize_year("Jan-24"))