from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

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

SECURITY_EXPOSURE_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "security_exposure.csv"
)

SECTOR_EXPOSURE_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sector_exposure.csv"
)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    positions = pd.read_csv(
        POSITIONS_PATH
    )

    portfolio_master = pd.read_csv(
        PORTFOLIO_MASTER_PATH
    )

    target_aum = float(
        portfolio_master.loc[
            0,
            "target_aum"
        ]
    )

    portfolio_id = portfolio_master.loc[
        0,
        "portfolio_id"
    ]

    valuation_date = positions.loc[
        0,
        "valuation_date"
    ]

    print()
    print("=" * 70)
    print("PORTFOLIO EXPOSURE ANALYTICS")
    print("=" * 70)

    print(
        f"\nPortfolio: {portfolio_id}"
    )

    print(
        f"Valuation date: {valuation_date}"
    )

    print(
        f"Total AUM: ₹{target_aum:,.2f}"
    )

    # -----------------------------------------------------
    # 1. SECURITY-LEVEL EXPOSURE
    # -----------------------------------------------------

    security_exposure = positions[
        [
            "portfolio_id",
            "valuation_date",
            "security_id",
            "ticker",
            "company_name",
            "sector",
            "quantity",
            "market_price",
            "market_value",
            "actual_weight_pct",
        ]
    ].copy()

    security_exposure = (
        security_exposure
        .sort_values(
            "actual_weight_pct",
            ascending=False
        )
        .reset_index(drop=True)
    )

    security_exposure[
        "exposure_rank"
    ] = (
        security_exposure.index + 1
    )

    security_exposure.to_csv(
        SECURITY_EXPOSURE_OUTPUT,
        index=False
    )

    # -----------------------------------------------------
    # 2. SECTOR EXPOSURE
    # -----------------------------------------------------

    sector_exposure = (
        security_exposure
        .groupby(
            "sector",
            as_index=False
        )
        .agg(
            market_value=(
                "market_value",
                "sum"
            ),
            exposure_pct=(
                "actual_weight_pct",
                "sum"
            ),
            number_of_positions=(
                "ticker",
                "count"
            ),
        )
    )

    sector_exposure = (
        sector_exposure
        .sort_values(
            "exposure_pct",
            ascending=False
        )
        .reset_index(drop=True)
    )

    sector_exposure[
        "sector_rank"
    ] = (
        sector_exposure.index + 1
    )

    sector_exposure.to_csv(
        SECTOR_EXPOSURE_OUTPUT,
        index=False
    )

    # -----------------------------------------------------
    # 3. PORTFOLIO SUMMARY
    # -----------------------------------------------------

    invested_value = (
        security_exposure[
            "market_value"
        ].sum()
    )

    residual_cash = (
        target_aum
        - invested_value
    )

    cash_weight_pct = (
        residual_cash
        / target_aum
        * 100
    )

    # Largest security
    largest_position = (
        security_exposure.iloc[0]
    )

    # Largest sector
    largest_sector = (
        sector_exposure.iloc[0]
    )

    # Top 5 concentration
    top_5_weight_pct = (
        security_exposure
        .head(5)[
            "actual_weight_pct"
        ]
        .sum()
    )

    # -----------------------------------------------------
    # DISPLAY SECURITY EXPOSURE
    # -----------------------------------------------------

    print()
    print("-" * 70)
    print("TOP 10 SECURITY EXPOSURES")
    print("-" * 70)

    print(
        security_exposure[
            [
                "exposure_rank",
                "ticker",
                "sector",
                "market_value",
                "actual_weight_pct",
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # DISPLAY SECTOR EXPOSURE
    # -----------------------------------------------------

    print()
    print("-" * 70)
    print("SECTOR EXPOSURE")
    print("-" * 70)

    print(
        sector_exposure[
            [
                "sector_rank",
                "sector",
                "number_of_positions",
                "market_value",
                "exposure_pct",
            ]
        ].to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # DISPLAY SUMMARY
    # -----------------------------------------------------

    print()
    print("-" * 70)
    print("EXPOSURE SUMMARY")
    print("-" * 70)

    print(
        f"Largest position: "
        f"{largest_position['ticker']}"
    )

    print(
        f"Largest position weight: "
        f"{largest_position['actual_weight_pct']:.4f}%"
    )

    print(
        f"Largest sector: "
        f"{largest_sector['sector']}"
    )

    print(
        f"Largest sector weight: "
        f"{largest_sector['exposure_pct']:.4f}%"
    )

    print(
        f"Top 5 concentration: "
        f"{top_5_weight_pct:.4f}%"
    )

    print(
        f"Cash weight: "
        f"{cash_weight_pct:.4f}%"
    )

    print()

    print(
        "Security exposure saved to:"
    )

    print(
        SECURITY_EXPOSURE_OUTPUT
        .relative_to(PROJECT_ROOT)
    )

    print()

    print(
        "Sector exposure saved to:"
    )

    print(
        SECTOR_EXPOSURE_OUTPUT
        .relative_to(PROJECT_ROOT)
    )


if __name__ == "__main__":
    main()