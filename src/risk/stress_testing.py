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

STRESS_SCENARIOS_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "stress_scenarios.csv"
)

POSITION_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stress_test_position_results.csv"
)

SUMMARY_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stress_test_summary.csv"
)


# ---------------------------------------------------------
# APPLY SCENARIO
# ---------------------------------------------------------

def apply_scenario(
    positions,
    scenario_rows
):

    stressed = positions.copy()

    # By default there is no shock.
    stressed["applied_shock_pct"] = 0.0

    # -----------------------------------------------------
    # APPLY PORTFOLIO-WIDE SHOCK FIRST
    # -----------------------------------------------------

    portfolio_rules = scenario_rows[
        scenario_rows["shock_scope"]
        == "PORTFOLIO"
    ]

    for _, rule in portfolio_rules.iterrows():

        if rule["shock_target"] != "ALL":

            raise ValueError(
                "PORTFOLIO stress rule must use "
                "shock_target = ALL"
            )

        stressed[
            "applied_shock_pct"
        ] = float(
            rule["shock_pct"]
        )

    # -----------------------------------------------------
    # APPLY SECTOR OVERRIDES SECOND
    # -----------------------------------------------------

    sector_rules = scenario_rows[
        scenario_rows["shock_scope"]
        == "SECTOR"
    ]

    for _, rule in sector_rules.iterrows():

        sector = rule[
            "shock_target"
        ]

        shock_pct = float(
            rule[
                "shock_pct"
            ]
        )

        mask = (
            stressed["sector"]
            == sector
        )

        if not mask.any():

            raise ValueError(
                f"Sector '{sector}' from stress scenario "
                "was not found in portfolio positions."
            )

        # Sector-specific shock overrides
        # any portfolio-wide shock.
        stressed.loc[
            mask,
            "applied_shock_pct"
        ] = shock_pct

    # -----------------------------------------------------
    # CHECK FOR UNSUPPORTED RULE TYPES
    # -----------------------------------------------------

    valid_scopes = {
        "PORTFOLIO",
        "SECTOR"
    }

    invalid_scopes = set(
        scenario_rows[
            "shock_scope"
        ].unique()
    ) - valid_scopes

    if invalid_scopes:

        raise ValueError(
            f"Unsupported stress scopes: "
            f"{invalid_scopes}"
        )

    return stressed


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

    stress_scenarios = pd.read_csv(
        STRESS_SCENARIOS_PATH
    )

    portfolio_id = (
        portfolio_master.loc[
            0,
            "portfolio_id"
        ]
    )

    target_aum = float(
        portfolio_master.loc[
            0,
            "target_aum"
        ]
    )

    valuation_date = (
        positions.loc[
            0,
            "valuation_date"
        ]
    )

    invested_value = float(
        positions[
            "market_value"
        ].sum()
    )

    residual_cash = (
        target_aum
        - invested_value
    )

    print()
    print("=" * 75)
    print("PORTFOLIO STRESS TESTING")
    print("=" * 75)

    print(
        f"\nPortfolio: "
        f"{portfolio_id}"
    )

    print(
        f"Valuation date: "
        f"{valuation_date}"
    )

    print(
        f"Portfolio AUM: "
        f"₹{target_aum:,.2f}"
    )

    print(
        f"Invested equity value: "
        f"₹{invested_value:,.2f}"
    )

    print(
        f"Residual cash: "
        f"₹{residual_cash:,.2f}"
    )

    all_position_results = []
    scenario_summaries = []

    # -----------------------------------------------------
    # PROCESS EACH SCENARIO
    # -----------------------------------------------------

    scenario_ids = (
        stress_scenarios[
            "scenario_id"
        ]
        .drop_duplicates()
        .tolist()
    )

    for scenario_id in scenario_ids:

        scenario_rows = (
            stress_scenarios[
                stress_scenarios[
                    "scenario_id"
                ] == scenario_id
            ]
            .copy()
        )

        scenario_name = (
            scenario_rows.iloc[0][
                "scenario_name"
            ]
        )

        stressed = apply_scenario(
            positions=positions,
            scenario_rows=scenario_rows
        )

        stressed[
            "scenario_id"
        ] = scenario_id

        stressed[
            "scenario_name"
        ] = scenario_name

        # -------------------------------------------------
        # STRESSED POSITION VALUES
        # -------------------------------------------------

        stressed[
            "stressed_market_value"
        ] = (
            stressed[
                "market_value"
            ]
            * (
                1
                + stressed[
                    "applied_shock_pct"
                ]
                / 100
            )
        )

        stressed[
            "stress_pnl"
        ] = (
            stressed[
                "stressed_market_value"
            ]
            - stressed[
                "market_value"
            ]
        )

        # Positive number representing loss.
        stressed[
            "stress_loss_amount"
        ] = (
            -stressed[
                "stress_pnl"
            ]
        )

        # Position-level loss as % of full portfolio AUM.
        stressed[
            "portfolio_loss_contribution_pct"
        ] = (
            stressed[
                "stress_loss_amount"
            ]
            / target_aum
            * 100
        )

        # -------------------------------------------------
        # SCENARIO TOTALS
        # -------------------------------------------------

        total_stress_pnl = float(
            stressed[
                "stress_pnl"
            ].sum()
        )

        total_loss_amount = (
            -total_stress_pnl
        )

        portfolio_loss_pct = (
            total_loss_amount
            / target_aum
            * 100
        )

        stressed_equity_value = float(
            stressed[
                "stressed_market_value"
            ].sum()
        )

        stressed_portfolio_value = (
            stressed_equity_value
            + residual_cash
        )

        # -------------------------------------------------
        # LOSS CONTRIBUTION WITHIN SCENARIO
        # -------------------------------------------------

        if total_loss_amount > 0:

            stressed[
                "scenario_loss_contribution_pct"
            ] = (
                stressed[
                    "stress_loss_amount"
                ]
                / total_loss_amount
                * 100
            )

        else:

            stressed[
                "scenario_loss_contribution_pct"
            ] = 0.0

        # -------------------------------------------------
        # ADD POSITION RESULTS
        # -------------------------------------------------

        position_columns = [
            "valuation_date",
            "portfolio_id",
            "scenario_id",
            "scenario_name",
            "security_id",
            "ticker",
            "company_name",
            "sector",
            "market_value",
            "applied_shock_pct",
            "stressed_market_value",
            "stress_pnl",
            "stress_loss_amount",
            "portfolio_loss_contribution_pct",
            "scenario_loss_contribution_pct",
        ]

        all_position_results.append(
            stressed[
                position_columns
            ]
        )

        # -------------------------------------------------
        # FIND LARGEST LOSS CONTRIBUTOR
        # -------------------------------------------------

        largest_loss_row = (
            stressed.loc[
                stressed[
                    "stress_loss_amount"
                ].idxmax()
            ]
        )

        # -------------------------------------------------
        # SUMMARY ROW
        # -------------------------------------------------

        scenario_summaries.append(
            {
                "valuation_date":
                    valuation_date,

                "portfolio_id":
                    portfolio_id,

                "scenario_id":
                    scenario_id,

                "scenario_name":
                    scenario_name,

                "starting_portfolio_value":
                    target_aum,

                "starting_equity_value":
                    invested_value,

                "residual_cash":
                    residual_cash,

                "stressed_equity_value":
                    stressed_equity_value,

                "stressed_portfolio_value":
                    stressed_portfolio_value,

                "stress_pnl":
                    total_stress_pnl,

                "stress_loss_amount":
                    total_loss_amount,

                "portfolio_loss_pct":
                    portfolio_loss_pct,

                "largest_loss_contributor":
                    largest_loss_row[
                        "ticker"
                    ],

                "largest_loss_contribution_amount":
                    largest_loss_row[
                        "stress_loss_amount"
                    ],

                "largest_loss_contribution_pct":
                    largest_loss_row[
                        "portfolio_loss_contribution_pct"
                    ],
            }
        )

    # ---------------------------------------------------------
    # COMBINE RESULTS
    # ---------------------------------------------------------

    position_results = pd.concat(
        all_position_results,
        ignore_index=True
    )

    summary = pd.DataFrame(
        scenario_summaries
    )

    summary = (
        summary
        .sort_values(
            "portfolio_loss_pct",
            ascending=False
        )
        .reset_index(drop=True)
    )

    summary[
        "stress_severity_rank"
    ] = (
        summary.index
        + 1
    )

    # ---------------------------------------------------------
    # SAVE RESULTS
    # ---------------------------------------------------------

    position_results.to_csv(
        POSITION_OUTPUT_PATH,
        index=False
    )

    summary.to_csv(
        SUMMARY_OUTPUT_PATH,
        index=False
    )

    # ---------------------------------------------------------
    # DISPLAY SUMMARY
    # ---------------------------------------------------------

    print()
    print("-" * 75)
    print("STRESS TEST SUMMARY")
    print("-" * 75)

    print(
        summary[
            [
                "stress_severity_rank",
                "scenario_id",
                "scenario_name",
                "stress_loss_amount",
                "portfolio_loss_pct",
                "largest_loss_contributor",
            ]
        ].to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # WORST SCENARIO
    # ---------------------------------------------------------

    worst = summary.iloc[0]

    print()
    print("-" * 75)
    print("WORST STRESS SCENARIO")
    print("-" * 75)

    print(
        f"Scenario: "
        f"{worst['scenario_name']}"
    )

    print(
        f"Portfolio loss: "
        f"{worst['portfolio_loss_pct']:.4f}%"
    )

    print(
        f"Loss amount: "
        f"₹{worst['stress_loss_amount']:,.2f}"
    )

    print(
        f"Stressed portfolio value: "
        f"₹{worst['stressed_portfolio_value']:,.2f}"
    )

    print(
        f"Largest loss contributor: "
        f"{worst['largest_loss_contributor']}"
    )

    print()
    print(
        "Position-level stress results saved to:"
    )

    print(
        POSITION_OUTPUT_PATH
        .relative_to(PROJECT_ROOT)
    )

    print()

    print(
        "Stress summary saved to:"
    )

    print(
        SUMMARY_OUTPUT_PATH
        .relative_to(PROJECT_ROOT)
    )


if __name__ == "__main__":
    main()