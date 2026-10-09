from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SECURITY_MASTER_PATH = (
    PROJECT_ROOT / "data" / "reference" / "dim_security.csv"
)

PORTFOLIO_MASTER_PATH = (
    PROJECT_ROOT / "data" / "reference" / "portfolio_master.csv"
)

TARGET_WEIGHTS_PATH = (
    PROJECT_ROOT / "data" / "reference" / "portfolio_target_weights.csv"
)

MARKET_DATA_DIR = (
    PROJECT_ROOT / "data" / "raw" / "market_prices"
)

OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "initial_positions.csv"
)


# ---------------------------------------------------------
# FIND LATEST COMMON COMPLETED TRADING DATE
# ---------------------------------------------------------

def find_latest_common_date(tickers):

    common_dates = None

    for ticker in tickers:

        filename = ticker.replace(".NS", "") + ".csv"
        file_path = MARKET_DATA_DIR / filename

        df = pd.read_csv(
            file_path,
            usecols=["Date"]
        )

        dates = set(
            pd.to_datetime(df["Date"])
        )

        if common_dates is None:
            common_dates = dates
        else:
            common_dates = common_dates.intersection(dates)

    if not common_dates:
        raise ValueError(
            "No common trading date found across all securities."
        )

    # Avoid today's potentially incomplete market bar
    today = pd.Timestamp.today().normalize()

    completed_dates = [
        date
        for date in common_dates
        if date < today
    ]

    if not completed_dates:
        raise ValueError(
            "No completed common trading date found."
        )

    return max(completed_dates)


# ---------------------------------------------------------
# GET CLOSING PRICE FOR ONE SECURITY
# ---------------------------------------------------------

def get_close_price(ticker, valuation_date):

    filename = ticker.replace(".NS", "") + ".csv"
    file_path = MARKET_DATA_DIR / filename

    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])

    row = df[
        df["Date"] == valuation_date
    ]

    if row.empty:
        raise ValueError(
            f"No price found for {ticker} "
            f"on {valuation_date.date()}"
        )

    return float(row.iloc[0]["Close"])


# ---------------------------------------------------------
# BUILD PORTFOLIO
# ---------------------------------------------------------

def main():

    securities = pd.read_csv(
        SECURITY_MASTER_PATH
    )

    portfolio_master = pd.read_csv(
        PORTFOLIO_MASTER_PATH
    )

    target_weights = pd.read_csv(
        TARGET_WEIGHTS_PATH
    )

    portfolio_id = portfolio_master.loc[
        0,
        "portfolio_id"
    ]

    target_aum = float(
        portfolio_master.loc[
            0,
            "target_aum"
        ]
    )

    tickers = target_weights[
        "ticker"
    ].tolist()

    valuation_date = find_latest_common_date(
        tickers
    )

    print()
    print("=" * 65)
    print("INITIAL PORTFOLIO CONSTRUCTION")
    print("=" * 65)

    print(
        f"\nPortfolio: {portfolio_id}"
    )

    print(
        f"Target AUM: ₹{target_aum:,.2f}"
    )

    print(
        f"Common valuation date: "
        f"{valuation_date.date()}"
    )

    positions = []

    # -----------------------------------------------------
    # BUILD EACH POSITION
    # -----------------------------------------------------

    for _, row in target_weights.iterrows():

        security_id = row["security_id"]
        ticker = row["ticker"]
        target_weight_pct = row[
            "target_weight_pct"
        ]

        target_value = (
            target_aum
            * target_weight_pct
            / 100
        )

        market_price = get_close_price(
            ticker,
            valuation_date
        )

        # Whole shares only
        quantity = int(
            target_value // market_price
        )

        market_value = (
            quantity * market_price
        )

        allocation_difference = (
            target_value - market_value
        )

        positions.append(
            {
                "valuation_date": valuation_date.date(),
                "portfolio_id": portfolio_id,
                "security_id": security_id,
                "ticker": ticker,
                "target_weight_pct": target_weight_pct,
                "target_value": target_value,
                "quantity": quantity,
                "market_price": market_price,
                "market_value": market_value,
                "allocation_difference": allocation_difference,
            }
        )

    positions_df = pd.DataFrame(
        positions
    )

    # -----------------------------------------------------
    # CALCULATE PORTFOLIO VALUES
    # -----------------------------------------------------

    invested_value = positions_df[
        "market_value"
    ].sum()

    residual_cash = (
        target_aum - invested_value
    )

    cash_weight_pct = (
        residual_cash
        / target_aum
        * 100
    )

    positions_df[
        "actual_weight_pct"
    ] = (
        positions_df["market_value"]
        / target_aum
        * 100
    )

    positions_df[
        "weight_difference_pct"
    ] = (
        positions_df["actual_weight_pct"]
        - positions_df["target_weight_pct"]
    )

    # -----------------------------------------------------
    # ADD COMPANY / SECTOR DETAILS
    # -----------------------------------------------------

    positions_df = positions_df.merge(
        securities[
            [
                "security_id",
                "company_name",
                "sector"
            ]
        ],
        on="security_id",
        how="left"
    )

    # -----------------------------------------------------
    # REORDER COLUMNS
    # -----------------------------------------------------

    positions_df = positions_df[
        [
            "valuation_date",
            "portfolio_id",
            "security_id",
            "ticker",
            "company_name",
            "sector",
            "target_weight_pct",
            "actual_weight_pct",
            "weight_difference_pct",
            "target_value",
            "quantity",
            "market_price",
            "market_value",
            "allocation_difference",
        ]
    ]

    # -----------------------------------------------------
    # SAVE OUTPUT
    # -----------------------------------------------------

    positions_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # DISPLAY POSITION SUMMARY
    # -----------------------------------------------------

    print()

    print(
        positions_df[
            [
                "ticker",
                "target_weight_pct",
                "actual_weight_pct",
                "quantity",
                "market_price",
                "market_value",
            ]
        ].to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # PORTFOLIO SUMMARY
    # -----------------------------------------------------

    equity_weight_pct = (
        positions_df[
            "actual_weight_pct"
        ].sum()
    )

    total_weight_pct = (
        equity_weight_pct
        + cash_weight_pct
    )

    print()
    print("=" * 65)

    print(
        f"Invested value: ₹{invested_value:,.2f}"
    )

    print(
        f"Residual cash:  ₹{residual_cash:,.2f}"
    )

    print(
        f"Total AUM:      ₹{target_aum:,.2f}"
    )

    print()

    print(
        f"Equity weight:  "
        f"{equity_weight_pct:.6f}%"
    )

    print(
        f"Cash weight:    "
        f"{cash_weight_pct:.6f}%"
    )

    print(
        f"Total weight:   "
        f"{total_weight_pct:.6f}%"
    )

    print()

    print(
        f"Positions saved to:\n"
        f"{OUTPUT_PATH.relative_to(PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    main()