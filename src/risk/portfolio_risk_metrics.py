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

PORTFOLIO_RETURNS_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "portfolio_daily_returns.csv"
)

PORTFOLIO_METRICS_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "portfolio_risk_summary.csv"
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

    # -----------------------------------------------------
    # CREATE PORTFOLIO WEIGHTS
    # -----------------------------------------------------

    weights = (
        positions
        .set_index("ticker")[
            "actual_weight_pct"
        ]
        / 100
    )

    tickers = weights.index.tolist()

    # Make sure all portfolio securities exist
    # in the historical return dataset.
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

    # -----------------------------------------------------
    # CHECK WEIGHTS
    # -----------------------------------------------------

    equity_weight = weights.sum()

    cash_weight = (
        1 - equity_weight
    )

    print()
    print("=" * 70)
    print("PORTFOLIO MARKET RISK ANALYTICS")
    print("=" * 70)

    print(
        f"\nEquity weight: "
        f"{equity_weight * 100:.6f}%"
    )

    print(
        f"Cash weight: "
        f"{cash_weight * 100:.6f}%"
    )

    # -----------------------------------------------------
    # CALCULATE PORTFOLIO DAILY RETURNS
    # -----------------------------------------------------

    security_returns = (
        returns[tickers]
    )

    portfolio_daily_return = (
        security_returns
        .mul(
            weights,
            axis=1
        )
        .sum(axis=1)
    )
    
    portfolio_returns = pd.DataFrame(
        {
            "Date":
                returns["Date"],

            "portfolio_id":
                portfolio_id,

            "portfolio_return":
                portfolio_daily_return,
        }
    )

    # -----------------------------------------------------
    # CUMULATIVE RETURN
    # -----------------------------------------------------

    portfolio_returns[
        "cumulative_growth"
    ] = (
        1
        + portfolio_returns[
            "portfolio_return"
        ]
    ).cumprod()

    portfolio_returns[
        "cumulative_return"
    ] = (
        portfolio_returns[
            "cumulative_growth"
        ]
        - 1
    )

    # -----------------------------------------------------
    # RUNNING PEAK
    # -----------------------------------------------------

    portfolio_returns[
        "running_peak"
    ] = (
        portfolio_returns[
            "cumulative_growth"
        ]
        .cummax()
    )

    # -----------------------------------------------------
    # DRAWDOWN
    # -----------------------------------------------------

    portfolio_returns[
        "drawdown"
    ] = (
        portfolio_returns[
            "cumulative_growth"
        ]
        / portfolio_returns[
            "running_peak"
        ]
        - 1
    )

    # -----------------------------------------------------
    # RISK METRICS
    # -----------------------------------------------------

    trading_days = 252

    average_daily_return = (
        portfolio_returns[
            "portfolio_return"
        ].mean()
    )

    daily_volatility = (
        portfolio_returns[
            "portfolio_return"
        ].std()
    )

    annualized_volatility = (
        daily_volatility
        * np.sqrt(trading_days)
    )

    cumulative_return = (
        portfolio_returns[
            "cumulative_return"
        ].iloc[-1]
    )

    maximum_drawdown = (
        portfolio_returns[
            "drawdown"
        ].min()
    )

    best_day = (
        portfolio_returns[
            "portfolio_return"
        ].max()
    )

    worst_day = (
        portfolio_returns[
            "portfolio_return"
        ].min()
    )

    # -----------------------------------------------------
    # FIND MAXIMUM DRAWDOWN DATE
    # -----------------------------------------------------

    max_drawdown_row = (
        portfolio_returns.loc[
            portfolio_returns[
                "drawdown"
            ].idxmin()
        ]
    )

    max_drawdown_date = (
        max_drawdown_row[
            "Date"
        ]
    )

    # -----------------------------------------------------
    # CREATE SUMMARY TABLE
    # -----------------------------------------------------

    summary = pd.DataFrame(
        [
            {
                "valuation_date":
                    positions.loc[
                        0,
                        "valuation_date"
                    ],
                    
                "portfolio_id":
                    portfolio_id,

                "return_observations":
                    len(
                        portfolio_returns
                    ),

                "average_daily_return":
                    average_daily_return,

                "daily_volatility":
                    daily_volatility,

                "annualized_volatility":
                    annualized_volatility,

                "cumulative_return":
                    cumulative_return,

                "maximum_drawdown":
                    maximum_drawdown,

                "max_drawdown_date":
                    max_drawdown_date.date(),

                "best_daily_return":
                    best_day,

                "worst_daily_return":
                    worst_day,
            }
        ]
    )

    # -----------------------------------------------------
    # SAVE OUTPUTS
    # -----------------------------------------------------

    portfolio_returns.to_csv(
        PORTFOLIO_RETURNS_OUTPUT,
        index=False
    )

    summary.to_csv(
        PORTFOLIO_METRICS_OUTPUT,
        index=False
    )

    # -----------------------------------------------------
    # DISPLAY SUMMARY
    # -----------------------------------------------------

    print()
    print("-" * 70)
    print("PORTFOLIO RISK SUMMARY")
    print("-" * 70)

    print(
        f"Return observations: "
        f"{len(portfolio_returns)}"
    )

    print(
        f"Average daily return: "
        f"{average_daily_return:.4%}"
    )

    print(
        f"Daily volatility: "
        f"{daily_volatility:.4%}"
    )

    print(
        f"Annualized volatility: "
        f"{annualized_volatility:.4%}"
    )

    print(
        f"Cumulative return: "
        f"{cumulative_return:.4%}"
    )

    print(
        f"Maximum drawdown: "
        f"{maximum_drawdown:.4%}"
    )

    print(
        f"Maximum drawdown date: "
        f"{max_drawdown_date.date()}"
    )

    print(
        f"Best daily return: "
        f"{best_day:.4%}"
    )

    print(
        f"Worst daily return: "
        f"{worst_day:.4%}"
    )

    print()
    print(
        "Portfolio returns saved to:"
    )

    print(
        PORTFOLIO_RETURNS_OUTPUT
        .relative_to(PROJECT_ROOT)
    )

    print()

    print(
        "Portfolio risk summary saved to:"
    )

    print(
        PORTFOLIO_METRICS_OUTPUT
        .relative_to(PROJECT_ROOT)
    )


if __name__ == "__main__":
    main()