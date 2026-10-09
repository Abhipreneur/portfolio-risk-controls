from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SECURITY_EXPOSURE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "security_exposure.csv"
)

SECTOR_EXPOSURE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sector_exposure.csv"
)

PORTFOLIO_MASTER_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "portfolio_master.csv"
)

RISK_LIMITS_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "risk_limits.csv"
)

HISTORICAL_VAR_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "portfolio_var_summary.csv"
)

CONTROL_RESULTS_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "control_results.csv"
)

CONTROL_EXCEPTIONS_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "control_exceptions.csv"
)

LIQUIDITY_RISK_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "liquidity_risk.csv"
)

STRESS_SUMMARY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stress_test_summary.csv"
)


# ---------------------------------------------------------
# DETERMINE CONTROL STATUS
# ---------------------------------------------------------

def determine_status(
    metric_value,
    warning_threshold,
    critical_threshold
):

    if metric_value >= critical_threshold:
        return "RED"

    elif metric_value >= warning_threshold:
        return "AMBER"

    else:
        return "GREEN"


# ---------------------------------------------------------
# GET CONTROL LIMIT
# ---------------------------------------------------------

def get_control_limit(
    risk_limits,
    control_id
):

    row = risk_limits[
        risk_limits["control_id"]
        == control_id
    ]

    if row.empty:
        raise ValueError(
            f"Control {control_id} "
            "not found in risk_limits.csv"
        )

    return row.iloc[0]


# ---------------------------------------------------------
# APPEND CONTROL RESULT
# ---------------------------------------------------------

def append_result(
    results,
    valuation_date,
    portfolio_id,
    control,
    entity_type,
    entity_name,
    metric_value,
    description
):

    warning_threshold = float(
        control["warning_threshold"]
    )

    critical_threshold = float(
        control["critical_threshold"]
    )

    status = determine_status(
        metric_value,
        warning_threshold,
        critical_threshold
    )

    results.append(
        {
            "valuation_date": valuation_date,
            "portfolio_id": portfolio_id,
            "control_id": control["control_id"],
            "control_name": control["control_name"],
            "entity_type": entity_type,
            "entity_name": entity_name,
            "metric_name": control["metric_name"],
            "metric_value": metric_value,
            "warning_threshold": warning_threshold,
            "critical_threshold": critical_threshold,
            "unit": control["unit"],
            "status": status,
            "exception_description": description,
        }
    )


# ---------------------------------------------------------
# MAIN CONTROL ENGINE
# ---------------------------------------------------------

def main():

    security_exposure = pd.read_csv(
        SECURITY_EXPOSURE_PATH
    )

    sector_exposure = pd.read_csv(
        SECTOR_EXPOSURE_PATH
    )

    portfolio_master = pd.read_csv(
        PORTFOLIO_MASTER_PATH
    )

    risk_limits = pd.read_csv(
        RISK_LIMITS_PATH
    )

    historical_var = pd.read_csv(
        HISTORICAL_VAR_PATH
    )
      
    liquidity_risk = pd.read_csv(
        LIQUIDITY_RISK_PATH
    )
    
    stress_summary = pd.read_csv(
        STRESS_SUMMARY_PATH
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

    valuation_date = security_exposure.loc[
        0,
        "valuation_date"
    ]

    results = []

    # -----------------------------------------------------
    # RISK001
    # SINGLE SECURITY CONCENTRATION
    # -----------------------------------------------------

    control = get_control_limit(
        risk_limits,
        "RISK001"
    )

    for _, row in security_exposure.iterrows():

        metric_value = float(
            row["actual_weight_pct"]
        )

        append_result(
            results=results,
            valuation_date=valuation_date,
            portfolio_id=portfolio_id,
            control=control,
            entity_type="Security",
            entity_name=row["ticker"],
            metric_value=metric_value,
            description=(
                f"{row['ticker']} security exposure "
                f"is {metric_value:.4f}%."
            ),
        )

    # -----------------------------------------------------
    # RISK002
    # SECTOR CONCENTRATION
    # -----------------------------------------------------

    control = get_control_limit(
        risk_limits,
        "RISK002"
    )

    for _, row in sector_exposure.iterrows():

        metric_value = float(
            row["exposure_pct"]
        )

        append_result(
            results=results,
            valuation_date=valuation_date,
            portfolio_id=portfolio_id,
            control=control,
            entity_type="Sector",
            entity_name=row["sector"],
            metric_value=metric_value,
            description=(
                f"{row['sector']} sector exposure "
                f"is {metric_value:.4f}%."
            ),
        )

    # -----------------------------------------------------
    # RISK003
    # TOP 5 CONCENTRATION
    # -----------------------------------------------------

    control = get_control_limit(
        risk_limits,
        "RISK003"
    )

    top_5_weight_pct = float(
        security_exposure
        .nlargest(
            5,
            "actual_weight_pct"
        )[
            "actual_weight_pct"
        ]
        .sum()
    )

    append_result(
        results=results,
        valuation_date=valuation_date,
        portfolio_id=portfolio_id,
        control=control,
        entity_type="Portfolio",
        entity_name=portfolio_id,
        metric_value=top_5_weight_pct,
        description=(
            f"Top 5 securities represent "
            f"{top_5_weight_pct:.4f}% "
            "of portfolio AUM."
        ),
    )

    # -----------------------------------------------------
    # RISK004
    # CASH EXPOSURE
    # -----------------------------------------------------

    control = get_control_limit(
        risk_limits,
        "RISK004"
    )

    invested_value = float(
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

    append_result(
        results=results,
        valuation_date=valuation_date,
        portfolio_id=portfolio_id,
        control=control,
        entity_type="Portfolio",
        entity_name=portfolio_id,
        metric_value=cash_weight_pct,
        description=(
            f"Cash exposure is "
            f"{cash_weight_pct:.4f}% "
            "of portfolio AUM."
        ),
    )

    # -----------------------------------------------------
    # GET 99% HISTORICAL VAR ROW
    # -----------------------------------------------------

    var_99 = historical_var[
        historical_var[
            "confidence_level"
        ] == 0.99
    ]

    if var_99.empty:
        raise ValueError(
            "99% Historical VaR row not found "
            "in portfolio_var_summary.csv"
        )

    var_99 = var_99.iloc[0]

    # -----------------------------------------------------
    # RISK005
    # HISTORICAL 99% VAR
    # -----------------------------------------------------

    control = get_control_limit(
        risk_limits,
        "RISK005"
    )

    historical_var_99_pct = (
        float(
            var_99["var_pct"]
        )
        * 100
    )

    append_result(
        results=results,
        valuation_date=valuation_date,
        portfolio_id=portfolio_id,
        control=control,
        entity_type="Portfolio",
        entity_name=portfolio_id,
        metric_value=historical_var_99_pct,
        description=(
            f"99% Historical VaR is "
            f"{historical_var_99_pct:.4f}% "
            "of portfolio AUM."
        ),
    )

    # -----------------------------------------------------
    # RISK006
    # HISTORICAL 99% EXPECTED SHORTFALL
    # -----------------------------------------------------

    control = get_control_limit(
        risk_limits,
        "RISK006"
    )

    historical_es_99_pct = (
        float(
            var_99[
                "expected_shortfall_pct"
            ]
        )
        * 100
    )

    append_result(
        results=results,
        valuation_date=valuation_date,
        portfolio_id=portfolio_id,
        control=control,
        entity_type="Portfolio",
        entity_name=portfolio_id,
        metric_value=historical_es_99_pct,
        description=(
            f"99% Historical Expected Shortfall is "
            f"{historical_es_99_pct:.4f}% "
            "of portfolio AUM."
        ),
    )
    
    # -----------------------------------------------------
    # RISK007
    # DAYS TO LIQUIDATE
    # -----------------------------------------------------

    control = get_control_limit(
        risk_limits,
        "RISK007"
    )

    for _, row in liquidity_risk.iterrows():

        metric_value = float(
            row["days_to_liquidate"]
        )

        append_result(
            results=results,
            valuation_date=valuation_date,
            portfolio_id=portfolio_id,
            control=control,
            entity_type="Security",
            entity_name=row["ticker"],
            metric_value=metric_value,
            description=(
                f"{row['ticker']} requires "
                f"{metric_value:.4f} trading days "
                "to liquidate at the configured "
                "maximum participation rate."
            ),
        )
        
    # -----------------------------------------------------
    # RISK008
    # WORST STRESS SCENARIO LOSS
    # -----------------------------------------------------

    control = get_control_limit(
        risk_limits,
        "RISK008"
    )

    if stress_summary.empty:
        raise ValueError(
            "stress_test_summary.csv is empty"
        )

    worst_stress_row = (
        stress_summary.loc[
            stress_summary[
                "portfolio_loss_pct"
            ].idxmax()
        ]
    )

    worst_stress_loss_pct = float(
        worst_stress_row[
            "portfolio_loss_pct"
        ]
    )

    worst_stress_scenario = (
        worst_stress_row[
            "scenario_name"
        ]
    )

    append_result(
        results=results,
        valuation_date=valuation_date,
        portfolio_id=portfolio_id,
        control=control,
        entity_type="Portfolio",
        entity_name=portfolio_id,
        metric_value=worst_stress_loss_pct,
        description=(
            f"Worst stress scenario is "
            f"'{worst_stress_scenario}' with "
            f"a portfolio loss of "
            f"{worst_stress_loss_pct:.4f}%."
        ),
    )

    # -----------------------------------------------------
    # CREATE RESULTS DATAFRAME
    # -----------------------------------------------------

    control_results = pd.DataFrame(
        results
    )

    # -----------------------------------------------------
    # CREATE EXCEPTION TABLE
    # -----------------------------------------------------

    control_exceptions = (
        control_results[
            control_results[
                "status"
            ].isin(
                [
                    "AMBER",
                    "RED"
                ]
            )
        ]
        .copy()
        .reset_index(drop=True)
    )

    # -----------------------------------------------------
    # ADD EXCEPTION IDS
    # -----------------------------------------------------

    control_exceptions[
        "exception_id"
    ] = [
        f"EXC{i:04d}"
        for i in range(
            1,
            len(control_exceptions) + 1
        )
    ]

    # -----------------------------------------------------
    # ADD WORKFLOW STATUS
    # -----------------------------------------------------

    control_exceptions[
        "exception_status"
    ] = "OPEN"

    # -----------------------------------------------------
    # REORDER EXCEPTION COLUMNS
    # -----------------------------------------------------

    if not control_exceptions.empty:

        control_exceptions = (
            control_exceptions[
                [
                    "exception_id",
                    "valuation_date",
                    "portfolio_id",
                    "control_id",
                    "control_name",
                    "entity_type",
                    "entity_name",
                    "metric_name",
                    "metric_value",
                    "warning_threshold",
                    "critical_threshold",
                    "unit",
                    "status",
                    "exception_status",
                    "exception_description",
                ]
            ]
        )

    # -----------------------------------------------------
    # SAVE OUTPUTS
    # -----------------------------------------------------

    control_results.to_csv(
        CONTROL_RESULTS_OUTPUT,
        index=False
    )

    control_exceptions.to_csv(
        CONTROL_EXCEPTIONS_OUTPUT,
        index=False
    )

    # -----------------------------------------------------
    # STATUS SUMMARY
    # -----------------------------------------------------

    status_summary = (
        control_results[
            "status"
        ]
        .value_counts()
        .reindex(
            [
                "GREEN",
                "AMBER",
                "RED"
            ],
            fill_value=0
        )
    )

    print()
    print("=" * 70)
    print("RISK CONTROL ENGINE")
    print("=" * 70)

    print(
        f"\nPortfolio: {portfolio_id}"
    )

    print(
        f"Valuation date: {valuation_date}"
    )

    print()
    print("CONTROL STATUS SUMMARY")
    print("-" * 70)

    print(
        f"GREEN: {status_summary['GREEN']}"
    )

    print(
        f"AMBER: {status_summary['AMBER']}"
    )

    print(
        f"RED:   {status_summary['RED']}"
    )

    print(
        f"Total controls evaluated: "
        f"{len(control_results)}"
    )

    print(
        f"Open exceptions: "
        f"{len(control_exceptions)}"
    )

    # -----------------------------------------------------
    # DISPLAY EXCEPTIONS
    # -----------------------------------------------------

    print()
    print("-" * 70)
    print("CONTROL EXCEPTIONS")
    print("-" * 70)

    if control_exceptions.empty:

        print(
            "No AMBER or RED exceptions."
        )

    else:

        print(
            control_exceptions[
                [
                    "exception_id",
                    "control_id",
                    "entity_name",
                    "metric_value",
                    "warning_threshold",
                    "critical_threshold",
                    "status",
                ]
            ].to_string(
                index=False
            )
        )

    print()

    print(
        "Control results saved to:"
    )

    print(
        CONTROL_RESULTS_OUTPUT
        .relative_to(PROJECT_ROOT)
    )

    print()

    print(
        "Control exceptions saved to:"
    )

    print(
        CONTROL_EXCEPTIONS_OUTPUT
        .relative_to(PROJECT_ROOT)
    )


if __name__ == "__main__":
    main()