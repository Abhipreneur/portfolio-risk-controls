import os
import pandas as pd
import yfinance as yf

SECURITY_MASTER_PATH = "data/reference/dim_security.csv"
OUTPUT_DIR = "data/raw/market_prices"

os.makedirs(OUTPUT_DIR, exist_ok=True)

securities = pd.read_csv(SECURITY_MASTER_PATH)

tickers = securities["ticker"].tolist()

print(f"Downloading market data for {len(tickers)} securities...")

for ticker in tickers:
    print(f"Downloading {ticker}...")

    df = yf.download(
        ticker,
        period="3y",
        interval="1d",
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        print(f"WARNING: No data returned for {ticker}")
        continue

    # yfinance may return MultiIndex columns even for a single ticker.
    # Keep only the price-field level: Open, High, Low, Close, etc.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    output_path = os.path.join(
        OUTPUT_DIR,
        f"{ticker.replace('.NS', '')}.csv"
    )

    df.to_csv(output_path, index=False)

    print(f"Saved: {output_path}")

print("Market data download complete.")