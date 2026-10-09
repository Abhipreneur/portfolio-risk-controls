from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SECURITY_RISK_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "security_risk_contribution.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sector_risk_contribution.csv"
)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    security_risk = pd.read_csv(
        SECURITY_RISK_PATH
    )
    
    portfolio_id = (
        security_risk.loc[
            0,
            "portfolio_id"
        ]
    )

    valuation_date = (
        security_risk.loc[
            0,
            "valuation_date"
        ]
    )

    # -----------------------------------------------------
    # AGGREGATE BY SECTOR
    # -----------------------------------------------------

    sector_risk = (
        security_risk
        .groupby(
            "sector",
            as_index=False
        )
        .agg(
            portfolio_weight_pct=(
                "portfolio_weight_pct",
                "sum"
            ),
            risk_contribution_pct=(
                "risk_contribution_pct",
                "sum"
            ),
            component_annualized_volatility=(
                "component_annualized_volatility",
                "sum"
            ),
            security_count=(
                "ticker",
                "count"
            ),
        )
    )

    # -----------------------------------------------------
    # RISK / WEIGHT RATIO
    # -----------------------------------------------------

    sector_risk[
        "risk_to_weight_ratio"
    ] = (
        sector_risk[
            "risk_contribution_pct"
        ]
        / sector_risk[
            "portfolio_weight_pct"
        ]
    )

    # -----------------------------------------------------
    # EXCESS RISK CONTRIBUTION
    #
    # Positive:
    # sector contributes more risk than its weight.
    #
    # Negative:
    # sector contributes less risk than its weight.
    # -----------------------------------------------------

    sector_risk[
        "risk_minus_weight_pct"
    ] = (
        sector_risk[
            "risk_contribution_pct"
        ]
        - sector_risk[
            "portfolio_weight_pct"
        ]
    )

    sector_risk[
        "valuation_date"
    ] = valuation_date
    
    sector_risk[
        "portfolio_id"
    ] = portfolio_id

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    sector_risk = (
        sector_risk
        .sort_values(
            "risk_contribution_pct",
            ascending=False
        )
        .reset_index(drop=True)
    )

    sector_risk[
        "risk_contribution_rank"
    ] = (
        sector_risk.index
        + 1
    )

    # -----------------------------------------------------
    # REORDER COLUMNS
    # -----------------------------------------------------

    sector_risk = sector_risk[
        [
            "valuation_date",
            "portfolio_id",
            "risk_contribution_rank",
            "sector",
            "security_count",
            "portfolio_weight_pct",
            "risk_contribution_pct",
            "risk_minus_weight_pct",
            "risk_to_weight_ratio",
            "component_annualized_volatility",
        ]
    ]

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    sector_risk.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # RECONCILIATION
    # -----------------------------------------------------

    total_weight = (
        sector_risk[
            "portfolio_weight_pct"
        ].sum()
    )

    total_risk = (
        sector_risk[
            "risk_contribution_pct"
        ].sum()
    )

    total_component_volatility = (
        sector_risk[
            "component_annualized_volatility"
        ].sum()
    )

    print()
    print("=" * 80)
    print("SECTOR RISK CONTRIBUTION ANALYTICS")
    print("=" * 80)

    print(
        f"\nValuation date: "
        f"{valuation_date}"
    )

    print()
    print("-" * 80)
    print("RECONCILIATION")
    print("-" * 80)

    print(
        f"Total equity weight: "
        f"{total_weight:.6f}%"
    )

    print(
        f"Total risk contribution: "
        f"{total_risk:.6f}%"
    )

    print(
        f"Total component volatility: "
        f"{total_component_volatility:.4%}"
    )

    print()
    print("-" * 80)
    print("SECTOR RISK CONTRIBUTION")
    print("-" * 80)

    print(
        sector_risk[
            [
                "risk_contribution_rank",
                "sector",
                "portfolio_weight_pct",
                "risk_contribution_pct",
                "risk_minus_weight_pct",
                "risk_to_weight_ratio",
            ]
        ].to_string(
            index=False
        )
    )

    print()

    print(
        "Sector risk contribution saved to:"
    )

    print(
        OUTPUT_PATH
        .relative_to(PROJECT_ROOT)
    )


if __name__ == "__main__":
    main()