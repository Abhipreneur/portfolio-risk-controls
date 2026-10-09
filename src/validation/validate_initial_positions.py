from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

POSITIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "initial_positions.csv"
)

PORTFOLIO_MASTER_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "portfolio_master.csv"
)


def main():

    positions = pd.read_csv(POSITIONS_PATH)

    portfolio_master = pd.read_csv(
        PORTFOLIO_MASTER_PATH
    )

    target_aum = float(
        portfolio_master.loc[
            0,
            "target_aum"
        ]
    )

    print("=" * 65)
    print("INITIAL POSITION VALIDATION")
    print("=" * 65)

    # -----------------------------------------------------
    # BASIC COUNTS
    # -----------------------------------------------------

    print(
        "\nNumber of positions:",
        len(positions)
    )

    # -----------------------------------------------------
    # DUPLICATES
    # -----------------------------------------------------

    duplicate_tickers = (
        positions["ticker"]
        .duplicated()
        .sum()
    )

    duplicate_security_ids = (
        positions["security_id"]
        .duplicated()
        .sum()
    )

    print(
        "Duplicate tickers:",
        duplicate_tickers
    )

    print(
        "Duplicate security IDs:",
        duplicate_security_ids
    )

    # -----------------------------------------------------
    # MISSING VALUES
    # -----------------------------------------------------

    missing_values = int(
        positions.isna().sum().sum()
    )

    print(
        "Missing values:",
        missing_values
    )

    # -----------------------------------------------------
    # INVALID QUANTITIES / PRICES
    # -----------------------------------------------------

    invalid_quantity = int(
        (positions["quantity"] <= 0).sum()
    )

    invalid_market_price = int(
        (positions["market_price"] <= 0).sum()
    )

    print(
        "Invalid quantities:",
        invalid_quantity
    )

    print(
        "Invalid market prices:",
        invalid_market_price
    )

    # -----------------------------------------------------
    # MARKET VALUE RECONCILIATION
    # -----------------------------------------------------

    calculated_market_value = (
        positions["quantity"]
        * positions["market_price"]
    )

    market_value_difference = (
        calculated_market_value
        - positions["market_value"]
    ).abs()

    reconciliation_failures = int(
        (market_value_difference > 0.01).sum()
    )

    print(
        "Market value reconciliation failures:",
        reconciliation_failures
    )

    # -----------------------------------------------------
    # PORTFOLIO TOTALS
    # -----------------------------------------------------

    invested_value = positions[
        "market_value"
    ].sum()

    residual_cash = (
        target_aum - invested_value
    )

    equity_weight = (
        positions["actual_weight_pct"]
        .sum()
    )

    cash_weight = (
        residual_cash
        / target_aum
        * 100
    )

    total_weight = (
        equity_weight
        + cash_weight
    )

    print()
    print(
        f"Invested value: ₹{invested_value:,.2f}"
    )

    print(
        f"Residual cash:  ₹{residual_cash:,.2f}"
    )

    print(
        f"Equity weight:  {equity_weight:.6f}%"
    )

    print(
        f"Cash weight:    {cash_weight:.6f}%"
    )

    print(
        f"Total weight:   {total_weight:.6f}%"
    )

    # -----------------------------------------------------
    # TARGET VS ACTUAL WEIGHT DEVIATION
    # -----------------------------------------------------

    max_weight_difference = (
        positions[
            "weight_difference_pct"
        ]
        .abs()
        .max()
    )

    print(
        "Maximum absolute weight deviation:",
        f"{max_weight_difference:.6f}%"
    )

    # -----------------------------------------------------
    # FINAL STATUS
    # -----------------------------------------------------

    passed = (
        len(positions) == 25
        and duplicate_tickers == 0
        and duplicate_security_ids == 0
        and missing_values == 0
        and invalid_quantity == 0
        and invalid_market_price == 0
        and reconciliation_failures == 0
        and abs(total_weight - 100) < 0.0001
    )

    print()

    if passed:
        print("STATUS: PASS")
    else:
        print("STATUS: FAIL")


if __name__ == "__main__":
    main()