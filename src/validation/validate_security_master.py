import pandas as pd

file_path = "data/reference/dim_security.csv"

df = pd.read_csv(file_path)

print(df.head())
print()
print("Rows:", len(df))
print("Columns:", list(df.columns))
print()
print("Missing values:")
print(df.isna().sum())
print()
print("Duplicate security_id:", df["security_id"].duplicated().sum())
print("Duplicate ticker:", df["ticker"].duplicated().sum())