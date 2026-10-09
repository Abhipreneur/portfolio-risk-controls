from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RETURNS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "security_daily_returns.csv"
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
    / "security_risk_contribution.csv"
)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    returns = pd.read_csv(
        RETURNS_PATH
    )

    positions = pd.read_csv(
        POSITIONS_PATH
    )
    
    portfolio_id = (
        positions.loc[
            0,
            "portfolio_id"
        ]
    )       

    returns["Date"] = pd.to_datetime(
        returns["Date"]
    )

    valuation_date = pd.to_datetime(
        positions.loc[
            0,
            "valuation_date"
        ]
    )

    # -----------------------------------------------------
    # PREVENT LOOK-AHEAD
    # -----------------------------------------------------

    returns = (
        returns[
            returns["Date"]
            <= valuation_date
        ]
        .copy()
    )

    # -----------------------------------------------------
    # PORTFOLIO WEIGHTS
    # -----------------------------------------------------

    positions = (
        positions
        .set_index("ticker")
        .copy()
    )

    weights = (
        positions[
            "actual_weight_pct"
        ]
        / 100
    )

    tickers = (
        weights.index
        .tolist()
    )

    # -----------------------------------------------------
    # VERIFY RETURN COLUMNS
    # -----------------------------------------------------

    missing_tickers = [
        ticker
        for ticker in tickers
        if ticker not in returns.columns
    ]

    if missing_tickers:

        raise ValueError(
            f"Missing return columns: "
            f"{missing_tickers}"
        )

    security_returns = (
        returns[
            tickers
        ]
        .copy()
    )

    if security_returns.isna().sum().sum() > 0:

        raise ValueError(
            "Missing values found in "
            "security return matrix."
        )

    # -----------------------------------------------------
    # DAILY COVARIANCE MATRIX
    # -----------------------------------------------------

    covariance_matrix = (
        security_returns
        .cov()
    )

    weight_vector = (
        weights
        .reindex(
            tickers
        )
        .to_numpy()
    )

    covariance_array = (
        covariance_matrix
        .loc[
            tickers,
            tickers
        ]
        .to_numpy()
    )

    # -----------------------------------------------------
    # PORTFOLIO VARIANCE AND VOLATILITY
    # -----------------------------------------------------

    portfolio_variance = float(
        weight_vector.T
        @ covariance_array
        @ weight_vector
    )

    portfolio_daily_volatility = (
        np.sqrt(
            portfolio_variance
        )
    )

    trading_days = 252

    portfolio_annualized_volatility = (
        portfolio_daily_volatility
        * np.sqrt(
            trading_days
        )
    )

    # -----------------------------------------------------
    # MARGINAL RISK CONTRIBUTION
    #
    # Sigma * w
    # ----------
    # sigma_p
    # -----------------------------------------------------

    covariance_with_portfolio = (
        covariance_array
        @ weight_vector
    )

    marginal_risk_contribution = (
        covariance_with_portfolio
        / portfolio_daily_volatility
    )

    # -----------------------------------------------------
    # COMPONENT RISK CONTRIBUTION
    #
    # w_i * MRC_i
    # -----------------------------------------------------

    component_daily_volatility = (
        weight_vector
        * marginal_risk_contribution
    )

    component_annualized_volatility = (
        component_daily_volatility
        * np.sqrt(
            trading_days
        )
    )

    # -----------------------------------------------------
    # PERCENTAGE CONTRIBUTION TO PORTFOLIO RISK
    # -----------------------------------------------------

    risk_contribution_pct = (
        component_daily_volatility
        / portfolio_daily_volatility
        * 100
    )

    # -----------------------------------------------------
    # STANDALONE SECURITY VOLATILITY
    # -----------------------------------------------------

    standalone_daily_volatility = (
        security_returns[
            tickers
        ]
        .std()
        .reindex(
            tickers
        )
        .to_numpy()
    )

    standalone_annualized_volatility = (
        standalone_daily_volatility
        * np.sqrt(
            trading_days
        )
    )

    # -----------------------------------------------------
    # CREATE RESULT
    # -----------------------------------------------------

    result = pd.DataFrame(
        {
            "valuation_date":
                valuation_date.date(),

            "portfolio_id":
                portfolio_id,

            "ticker":
                tickers,

            "portfolio_weight_pct":
                weight_vector
                * 100,

            "standalone_annualized_volatility":
                standalone_annualized_volatility,

            "marginal_daily_risk":
                marginal_risk_contribution,

            "component_daily_volatility":
                component_daily_volatility,

            "component_annualized_volatility":
                component_annualized_volatility,

            "risk_contribution_pct":
                risk_contribution_pct,
        }
    )

    # -----------------------------------------------------
    # ADD COMPANY / SECTOR INFORMATION
    # -----------------------------------------------------

    position_details = (
        positions[
            [
                "security_id",
                "company_name",
                "sector",
            ]
        ]
        .reset_index()
    )

    result = result.merge(
        position_details,
        on="ticker",
        how="left"
    )

    # -----------------------------------------------------
    # RISK / WEIGHT RATIO
    # -----------------------------------------------------

    result[
        "risk_to_weight_ratio"
    ] = (
        result[
            "risk_contribution_pct"
        ]
        / result[
            "portfolio_weight_pct"
        ]
    )

    # -----------------------------------------------------
    # SORT BY RISK CONTRIBUTION
    # -----------------------------------------------------

    result = (
        result
        .sort_values(
            "risk_contribution_pct",
            ascending=False
        )
        .reset_index(drop=True)
    )

    result[
        "risk_contribution_rank"
    ] = (
        result.index
        + 1
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # RECONCILIATION
    # -----------------------------------------------------

    total_risk_contribution = (
        result[
            "risk_contribution_pct"
        ]
        .sum()
    )

    component_volatility_sum = (
        result[
            "component_annualized_volatility"
        ]
        .sum()
    )

    print()
    print("=" * 80)
    print("SECURITY RISK CONTRIBUTION ANALYTICS")
    print("=" * 80)

    print(
        f"\nValuation date: "
        f"{valuation_date.date()}"
    )

    print(
        f"Return observations: "
        f"{len(security_returns)}"
    )

    print(
        f"Portfolio annualized volatility: "
        f"{portfolio_annualized_volatility:.4%}"
    )

    print()
    print("-" * 80)
    print("RISK RECONCILIATION")
    print("-" * 80)

    print(
        f"Sum of risk contributions: "
        f"{total_risk_contribution:.6f}%"
    )

    print(
        f"Sum of annualized component volatility: "
        f"{component_volatility_sum:.4%}"
    )

    print(
        f"Portfolio annualized volatility: "
        f"{portfolio_annualized_volatility:.4%}"
    )

    print()
    print("-" * 80)
    print("TOP 10 RISK CONTRIBUTORS")
    print("-" * 80)

    print(
        result[
            [
                "risk_contribution_rank",
                "ticker",
                "sector",
                "portfolio_weight_pct",
                "standalone_annualized_volatility",
                "risk_contribution_pct",
                "risk_to_weight_ratio",
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

    print()
    print(
        "Risk contribution results saved to:"
    )

    print(
        OUTPUT_PATH
        .relative_to(PROJECT_ROOT)
    )


if __name__ == "__main__":
    main()