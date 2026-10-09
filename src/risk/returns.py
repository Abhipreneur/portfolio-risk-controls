from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SECURITY_MASTER_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "dim_security.csv"
)

POSITIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "initial_positions.csv"
)

MARKET_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "market_prices"
)

PRICE_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "aligned_adjusted_close.csv"
)

RETURNS_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "security_daily_returns.csv"
)


# ---------------------------------------------------------
# LOAD PRICE SERIES
# ---------------------------------------------------------

def load_adjusted_close(ticker):

    filename = ticker.replace(".NS", "") + ".csv"

    file_path = (
        MARKET_DATA_DIR
        / filename
    )

    df = pd.read_csv(
        file_path,
        usecols=[
            "Date",
            "Adj Close"
        ]
    )

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    df = df.rename(
        columns={
            "Adj Close": ticker
        }
    )

    return df


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    securities = pd.read_csv(
        SECURITY_MASTER_PATH
    )

    positions = pd.read_csv(
        POSITIONS_PATH
    )

    valuation_date = pd.to_datetime(
        positions.loc[
            0,
            "valuation_date"
        ]
    )

    tickers = securities[
        "ticker"
    ].tolist()

    print()
    print("=" * 70)
    print("HISTORICAL RETURN DATASET")
    print("=" * 70)

    print(
        f"\nSecurities: {len(tickers)}"
    )

    print(
        f"Portfolio valuation date: "
        f"{valuation_date.date()}"
    )

    # -----------------------------------------------------
    # BUILD ALIGNED PRICE MATRIX
    # -----------------------------------------------------

    price_matrix = None

    for ticker in tickers:

        ticker_prices = (
            load_adjusted_close(
                ticker
            )
        )

        if price_matrix is None:

            price_matrix = ticker_prices

        else:

            # Retain only dates available
            # for every security
            price_matrix = (
                price_matrix.merge(
                    ticker_prices,
                    on="Date",
                    how="inner"
                )
            )

    price_matrix = (
        price_matrix
        .sort_values("Date")
        .reset_index(drop=True)
    )

    # -----------------------------------------------------
    # REMOVE DATA AFTER VALUATION DATE
    # -----------------------------------------------------

    price_matrix = (
        price_matrix[
            price_matrix["Date"]
            <= valuation_date
        ]
        .copy()
        .reset_index(drop=True)
    )

    # -----------------------------------------------------
    # DATA CHECKS
    # -----------------------------------------------------

    missing_prices = int(
        price_matrix
        .isna()
        .sum()
        .sum()
    )

    duplicate_dates = int(
        price_matrix[
            "Date"
        ]
        .duplicated()
        .sum()
    )

    print(
        f"Aligned trading days: "
        f"{len(price_matrix)}"
    )

    print(
        f"Missing prices: "
        f"{missing_prices}"
    )

    print(
        f"Duplicate dates: "
        f"{duplicate_dates}"
    )

    print(
        f"Start date: "
        f"{price_matrix['Date'].min().date()}"
    )

    print(
        f"End date: "
        f"{price_matrix['Date'].max().date()}"
    )

    # -----------------------------------------------------
    # CALCULATE DAILY RETURNS
    # -----------------------------------------------------

    returns_matrix = (
        price_matrix
        .set_index("Date")
        .pct_change(
            fill_method=None
        )
        .dropna()
        .reset_index()
    )

    print(
        f"Return observations: "
        f"{len(returns_matrix)}"
    )

    # -----------------------------------------------------
    # SAVE OUTPUTS
    # -----------------------------------------------------

    price_matrix.to_csv(
        PRICE_OUTPUT_PATH,
        index=False
    )

    returns_matrix.to_csv(
        RETURNS_OUTPUT_PATH,
        index=False
    )

    print()
    print(
        "Adjusted price matrix saved to:"
    )

    print(
        PRICE_OUTPUT_PATH
        .relative_to(PROJECT_ROOT)
    )

    print()

    print(
        "Daily return matrix saved to:"
    )

    print(
        RETURNS_OUTPUT_PATH
        .relative_to(PROJECT_ROOT)
    )


if __name__ == "__main__":
    main()