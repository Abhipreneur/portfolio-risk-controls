from pathlib import Path

import pandas as pd
import yfinance as yf


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALIGNED_PRICES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "aligned_adjusted_close.csv"
)

POSITIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "initial_positions.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "benchmark"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "NIFTY50.csv"
)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    aligned_prices = pd.read_csv(
        ALIGNED_PRICES_PATH
    )

    positions = pd.read_csv(
        POSITIONS_PATH
    )

    aligned_prices["Date"] = pd.to_datetime(
        aligned_prices["Date"]
    )

    start_date = (
        aligned_prices["Date"]
        .min()
    )

    valuation_date = pd.to_datetime(
        positions.loc[
            0,
            "valuation_date"
        ]
    )

    # yfinance treats end date as exclusive,
    # so add one day to include valuation date.
    end_date = (
        valuation_date
        + pd.Timedelta(days=1)
    )

    ticker = "^NSEI"

    print()
    print("=" * 70)
    print("BENCHMARK DATA INGESTION")
    print("=" * 70)

    print(
        f"\nBenchmark: NIFTY 50 ({ticker})"
    )

    print(
        f"Requested start date: "
        f"{start_date.date()}"
    )

    print(
        f"Portfolio valuation date: "
        f"{valuation_date.date()}"
    )

    df = yf.download(
        ticker,
        start=start_date.strftime(
            "%Y-%m-%d"
        ),
        end=end_date.strftime(
            "%Y-%m-%d"
        ),
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        raise ValueError(
            "No NIFTY 50 benchmark data downloaded."
        )

    # Handle yfinance MultiIndex output.
    if isinstance(
        df.columns,
        pd.MultiIndex
    ):
        df.columns = (
            df.columns
            .get_level_values(0)
        )

    df = df.reset_index()

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    # Defensive filter against any future data.
    df = (
        df[
            df["Date"]
            <= valuation_date
        ]
        .copy()
    )

    required_columns = [
        "Date",
        "Adj Close",
        "Close",
        "High",
        "Low",
        "Open",
        "Volume",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing benchmark columns: "
            f"{missing_columns}"
        )

    df = df[
        required_columns
    ]

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print()
    print("-" * 70)
    print("BENCHMARK DATA SUMMARY")
    print("-" * 70)

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Missing values: "
        f"{df.isna().sum().sum()}"
    )

    print(
        f"Duplicate dates: "
        f"{df['Date'].duplicated().sum()}"
    )

    print(
        f"Start date: "
        f"{df['Date'].min().date()}"
    )

    print(
        f"End date: "
        f"{df['Date'].max().date()}"
    )

    print()
    print(
        "Benchmark data saved to:"
    )

    print(
        OUTPUT_PATH.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()