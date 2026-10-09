from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_RETURNS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "portfolio_daily_returns.csv"
)

PORTFOLIO_MASTER_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "portfolio_master.csv"
)

POSITIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "initial_positions.csv"
)

VAR_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "portfolio_var_summary.csv"
)


# ---------------------------------------------------------
# HISTORICAL VAR
# ---------------------------------------------------------

def calculate_historical_var(
    returns,
    confidence_level
):

    tail_probability = (
        1 - confidence_level
    )

    return_quantile = np.quantile(
        returns,
        tail_probability
    )

    # Convert negative return threshold
    # into a positive loss measure
    var_pct = -return_quantile

    return (
        return_quantile,
        var_pct
    )


# ---------------------------------------------------------
# EXPECTED SHORTFALL
# ---------------------------------------------------------

def calculate_expected_shortfall(
    returns,
    return_quantile
):

    tail_returns = returns[
        returns <= return_quantile
    ]

    if len(tail_returns) == 0:
        return np.nan, 0

    expected_shortfall_pct = (
        -tail_returns.mean()
    )

    return (
        expected_shortfall_pct,
        len(tail_returns)
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    portfolio_returns = pd.read_csv(
        PORTFOLIO_RETURNS_PATH
    )

    portfolio_master = pd.read_csv(
        PORTFOLIO_MASTER_PATH
    )

    positions = pd.read_csv(
        POSITIONS_PATH
    )

    returns = (
        portfolio_returns[
            "portfolio_return"
        ]
        .dropna()
    )

    portfolio_aum = float(
        portfolio_master.loc[
            0,
            "target_aum"
        ]
    )

    portfolio_id = (
        portfolio_master.loc[
            0,
            "portfolio_id"
        ]
    )

    valuation_date = (
        positions.loc[
            0,
            "valuation_date"
        ]
    )

    print()
    print("=" * 70)
    print("HISTORICAL VALUE AT RISK & EXPECTED SHORTFALL")
    print("=" * 70)

    print(
        f"\nPortfolio: {portfolio_id}"
    )

    print(
        f"Valuation date: {valuation_date}"
    )

    print(
        f"Portfolio AUM: ₹{portfolio_aum:,.2f}"
    )

    print(
        f"Historical observations: "
        f"{len(returns)}"
    )

    results = []

    # -----------------------------------------------------
    # CALCULATE 95% AND 99%
    # -----------------------------------------------------

    for confidence_level in [
        0.95,
        0.99
    ]:

        (
            return_quantile,
            var_pct
        ) = calculate_historical_var(
            returns,
            confidence_level
        )

        (
            expected_shortfall_pct,
            tail_observations
        ) = calculate_expected_shortfall(
            returns,
            return_quantile
        )

        var_amount = (
            var_pct
            * portfolio_aum
        )

        expected_shortfall_amount = (
            expected_shortfall_pct
            * portfolio_aum
        )

        results.append(
            {
                "valuation_date":
                    valuation_date,

                "portfolio_id":
                    portfolio_id,

                "method":
                    "Historical",

                "holding_period_days":
                    1,

                "confidence_level":
                    confidence_level,

                "historical_observations":
                    len(returns),

                "tail_observations":
                    tail_observations,

                "var_pct":
                    var_pct,

                "var_amount":
                    var_amount,

                "expected_shortfall_pct":
                    expected_shortfall_pct,

                "expected_shortfall_amount":
                    expected_shortfall_amount,
            }
        )

    # -----------------------------------------------------
    # CREATE OUTPUT
    # -----------------------------------------------------

    var_summary = pd.DataFrame(
        results
    )

    var_summary.to_csv(
        VAR_OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # DISPLAY RESULTS
    # -----------------------------------------------------

    print()
    print("-" * 70)
    print("RISK RESULTS")
    print("-" * 70)

    for _, row in var_summary.iterrows():

        confidence_pct = (
            row[
                "confidence_level"
            ]
            * 100
        )

        print()

        print(
            f"{confidence_pct:.0f}% Historical VaR"
        )

        print(
            f"VaR: "
            f"{row['var_pct']:.4%}"
        )

        print(
            f"VaR amount: "
            f"₹{row['var_amount']:,.2f}"
        )

        print(
            f"Expected Shortfall: "
            f"{row['expected_shortfall_pct']:.4%}"
        )

        print(
            f"Expected Shortfall amount: "
            f"₹{row['expected_shortfall_amount']:,.2f}"
        )

        print(
            f"Tail observations: "
            f"{int(row['tail_observations'])}"
        )

    print()
    print(
        "VaR summary saved to:"
    )

    print(
        VAR_OUTPUT_PATH
        .relative_to(PROJECT_ROOT)
    )


if __name__ == "__main__":
    main()