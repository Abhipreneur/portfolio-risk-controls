from pathlib import Path
from statistics import NormalDist

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

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "parametric_var_summary.csv"
)


# ---------------------------------------------------------
# PARAMETRIC VAR
# ---------------------------------------------------------

def calculate_parametric_var(
    mean_return,
    volatility,
    confidence_level
):

    tail_probability = (
        1 - confidence_level
    )

    # Standard normal inverse CDF
    z_score = (
        NormalDist()
        .inv_cdf(tail_probability)
    )

    return_quantile = (
        mean_return
        + z_score * volatility
    )

    # Convert negative return threshold
    # into positive loss measure
    var_pct = (
        -return_quantile
    )

    return (
        z_score,
        return_quantile,
        var_pct
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

    mean_return = (
        returns.mean()
    )

    daily_volatility = (
        returns.std()
    )

    print()
    print("=" * 70)
    print("PARAMETRIC VALUE AT RISK")
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

    print(
        f"Average daily return: "
        f"{mean_return:.4%}"
    )

    print(
        f"Daily volatility: "
        f"{daily_volatility:.4%}"
    )

    results = []

    # -----------------------------------------------------
    # 95% AND 99% PARAMETRIC VAR
    # -----------------------------------------------------

    for confidence_level in [
        0.95,
        0.99
    ]:

        (
            z_score,
            return_quantile,
            var_pct
        ) = calculate_parametric_var(
            mean_return,
            daily_volatility,
            confidence_level
        )

        var_amount = (
            var_pct
            * portfolio_aum
        )

        results.append(
            {
                "valuation_date":
                    valuation_date,

                "portfolio_id":
                    portfolio_id,

                "method":
                    "Parametric-Normal",

                "holding_period_days":
                    1,

                "confidence_level":
                    confidence_level,

                "historical_observations":
                    len(returns),

                "mean_daily_return":
                    mean_return,

                "daily_volatility":
                    daily_volatility,

                "z_score":
                    z_score,

                "return_quantile":
                    return_quantile,

                "var_pct":
                    var_pct,

                "var_amount":
                    var_amount,
            }
        )

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    summary = pd.DataFrame(
        results
    )

    summary.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # ---------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("PARAMETRIC VAR RESULTS")
    print("-" * 70)

    for _, row in summary.iterrows():

        confidence_pct = (
            row[
                "confidence_level"
            ]
            * 100
        )

        print()

        print(
            f"{confidence_pct:.0f}% "
            "Parametric VaR"
        )

        print(
            f"Z-score: "
            f"{row['z_score']:.4f}"
        )

        print(
            f"VaR: "
            f"{row['var_pct']:.4%}"
        )

        print(
            f"VaR amount: "
            f"₹{row['var_amount']:,.2f}"
        )

    print()

    print(
        "Parametric VaR summary saved to:"
    )

    print(
        OUTPUT_PATH
        .relative_to(PROJECT_ROOT)
    )


if __name__ == "__main__":
    main()