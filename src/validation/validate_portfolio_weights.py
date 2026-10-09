import pandas as pd


SECURITY_MASTER_PATH = "data/reference/dim_security.csv"
PORTFOLIO_WEIGHTS_PATH = "data/reference/portfolio_target_weights.csv"


def main():
    securities = pd.read_csv(SECURITY_MASTER_PATH)
    weights = pd.read_csv(PORTFOLIO_WEIGHTS_PATH)

    print("=" * 60)
    print("PORTFOLIO TARGET WEIGHT VALIDATION")
    print("=" * 60)

    # -----------------------------------------------------
    # 1. Row count
    # -----------------------------------------------------

    print("\nNumber of portfolio securities:", len(weights))

    # -----------------------------------------------------
    # 2. Weight total
    # -----------------------------------------------------

    total_weight = weights["target_weight_pct"].sum()

    print("Total target weight:", total_weight)

    # -----------------------------------------------------
    # 3. Duplicate checks
    # -----------------------------------------------------

    duplicate_security_ids = (
        weights["security_id"]
        .duplicated()
        .sum()
    )

    duplicate_tickers = (
        weights["ticker"]
        .duplicated()
        .sum()
    )

    print(
        "Duplicate security IDs:",
        duplicate_security_ids
    )

    print(
        "Duplicate tickers:",
        duplicate_tickers
    )

    # -----------------------------------------------------
    # 4. Check Security IDs exist
    # -----------------------------------------------------

    invalid_security_ids = (
        set(weights["security_id"])
        - set(securities["security_id"])
    )

    print(
        "Invalid security IDs:",
        invalid_security_ids
    )

    # -----------------------------------------------------
    # 5. Check tickers exist
    # -----------------------------------------------------

    invalid_tickers = (
        set(weights["ticker"])
        - set(securities["ticker"])
    )

    print(
        "Invalid tickers:",
        invalid_tickers
    )

    # -----------------------------------------------------
    # 6. Check ID ↔ ticker mapping
    # -----------------------------------------------------

    merged = weights.merge(
        securities[
            [
                "security_id",
                "ticker"
            ]
        ],
        on="security_id",
        how="left",
        suffixes=(
            "_portfolio",
            "_master"
        )
    )

    ticker_mismatches = merged[
        merged["ticker_portfolio"]
        != merged["ticker_master"]
    ]

    print(
        "Security ID / ticker mismatches:",
        len(ticker_mismatches)
    )

    # -----------------------------------------------------
    # Final status
    # -----------------------------------------------------

    passed = (
        total_weight == 100
        and duplicate_security_ids == 0
        and duplicate_tickers == 0
        and len(invalid_security_ids) == 0
        and len(invalid_tickers) == 0
        and len(ticker_mismatches) == 0
    )

    print()

    if passed:
        print("STATUS: PASS")
    else:
        print("STATUS: FAIL")


if __name__ == "__main__":
    main()