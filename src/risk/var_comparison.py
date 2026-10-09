from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

HISTORICAL_VAR_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "portfolio_var_summary.csv"
)

PARAMETRIC_VAR_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "parametric_var_summary.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "var_method_comparison.csv"
)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    historical = pd.read_csv(
        HISTORICAL_VAR_PATH
    )

    parametric = pd.read_csv(
        PARAMETRIC_VAR_PATH
    )

    historical = historical[
        [
            "confidence_level",
            "var_pct",
            "var_amount",
            "expected_shortfall_pct",
            "expected_shortfall_amount",
        ]
    ].copy()

    historical = historical.rename(
        columns={
            "var_pct": "historical_var_pct",
            "var_amount": "historical_var_amount",
            "expected_shortfall_pct":
                "historical_es_pct",
            "expected_shortfall_amount":
                "historical_es_amount",
        }
    )

    parametric = parametric[
        [
            "confidence_level",
            "var_pct",
            "var_amount",
        ]
    ].copy()

    parametric = parametric.rename(
        columns={
            "var_pct": "parametric_var_pct",
            "var_amount": "parametric_var_amount",
        }
    )

    comparison = historical.merge(
        parametric,
        on="confidence_level",
        how="inner"
    )

    # -----------------------------------------------------
    # DIFFERENCE BETWEEN METHODS
    # -----------------------------------------------------

    comparison[
        "var_difference_pct_points"
    ] = (
        comparison["historical_var_pct"]
        - comparison["parametric_var_pct"]
    )

    comparison[
        "var_difference_amount"
    ] = (
        comparison["historical_var_amount"]
        - comparison["parametric_var_amount"]
    )

    comparison[
        "historical_vs_parametric_pct"
    ] = (
        (
            comparison["historical_var_pct"]
            / comparison["parametric_var_pct"]
        )
        - 1
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    comparison.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    print()
    print("=" * 75)
    print("VAR METHOD COMPARISON")
    print("=" * 75)

    for _, row in comparison.iterrows():

        confidence = (
            row["confidence_level"]
            * 100
        )

        print()

        print(
            f"{confidence:.0f}% Confidence"
        )

        print(
            f"Historical VaR: "
            f"{row['historical_var_pct']:.4%}"
        )

        print(
            f"Parametric VaR: "
            f"{row['parametric_var_pct']:.4%}"
        )

        print(
            f"Historical ES: "
            f"{row['historical_es_pct']:.4%}"
        )

        print(
            "Historical VaR vs Parametric: "
            f"{row['historical_vs_parametric_pct']:.2%}"
        )

        print(
            "VaR amount difference: "
            f"₹{row['var_difference_amount']:,.2f}"
        )

    print()

    print(
        "VaR comparison saved to:"
    )

    print(
        OUTPUT_PATH.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()