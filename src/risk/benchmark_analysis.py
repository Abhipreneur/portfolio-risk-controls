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

BENCHMARK_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "benchmark"
    / "NIFTY50.csv"
)

POSITIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "initial_positions.csv"
)

ALIGNED_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "portfolio_benchmark_returns.csv"
)

SUMMARY_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "benchmark_risk_summary.csv"
)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    portfolio = pd.read_csv(
        PORTFOLIO_RETURNS_PATH
    )

    benchmark = pd.read_csv(
        BENCHMARK_PATH
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

    portfolio["Date"] = pd.to_datetime(
        portfolio["Date"]
    )

    benchmark["Date"] = pd.to_datetime(
        benchmark["Date"]
    )

    valuation_date = pd.to_datetime(
        positions.loc[
            0,
            "valuation_date"
        ]
    )

    # -----------------------------------------------------
    # DEFENSIVE DATE FILTER
    # -----------------------------------------------------

    portfolio = (
        portfolio[
            portfolio["Date"]
            <= valuation_date
        ]
        .copy()
    )

    benchmark = (
        benchmark[
            benchmark["Date"]
            <= valuation_date
        ]
        .copy()
    )

    # -----------------------------------------------------
    # CALCULATE NIFTY DAILY RETURNS
    # -----------------------------------------------------

    benchmark = (
        benchmark[
            [
                "Date",
                "Adj Close"
            ]
        ]
        .sort_values("Date")
        .copy()
    )

    benchmark[
        "benchmark_return"
    ] = (
        benchmark[
            "Adj Close"
        ]
        .pct_change(
            fill_method=None
        )
    )

    benchmark = benchmark.dropna(
        subset=[
            "benchmark_return"
        ]
    )

    # -----------------------------------------------------
    # KEEP PORTFOLIO RETURN
    # -----------------------------------------------------
    
    portfolio = portfolio[
        [
            "Date",
            "portfolio_id",
            "portfolio_return"
        ]
    ].copy()

    # -----------------------------------------------------
    # ALIGN PORTFOLIO AND BENCHMARK
    # -----------------------------------------------------

    aligned = portfolio.merge(
        benchmark[
            [
                "Date",
                "benchmark_return"
            ]
        ],
        on="Date",
        how="inner"
    )

    aligned = (
        aligned
        .sort_values("Date")
        .reset_index(drop=True)
    )

    if aligned.empty:
        raise ValueError(
            "No common return dates found "
            "between portfolio and benchmark."
        )

    # -----------------------------------------------------
    # ACTIVE RETURN
    # -----------------------------------------------------

    aligned[
        "active_return"
    ] = (
        aligned[
            "portfolio_return"
        ]
        - aligned[
            "benchmark_return"
        ]
    )

    # -----------------------------------------------------
    # CORE STATISTICS
    # -----------------------------------------------------

    trading_days = 252

    portfolio_mean_daily = (
        aligned[
            "portfolio_return"
        ].mean()
    )

    benchmark_mean_daily = (
        aligned[
            "benchmark_return"
        ].mean()
    )

    portfolio_daily_volatility = (
        aligned[
            "portfolio_return"
        ].std()
    )

    benchmark_daily_volatility = (
        aligned[
            "benchmark_return"
        ].std()
    )

    portfolio_annualized_volatility = (
        portfolio_daily_volatility
        * np.sqrt(
            trading_days
        )
    )

    benchmark_annualized_volatility = (
        benchmark_daily_volatility
        * np.sqrt(
            trading_days
        )
    )

    # -----------------------------------------------------
    # BETA
    # -----------------------------------------------------

    covariance = (
        aligned[
            [
                "portfolio_return",
                "benchmark_return"
            ]
        ]
        .cov()
        .loc[
            "portfolio_return",
            "benchmark_return"
        ]
    )

    benchmark_variance = (
        aligned[
            "benchmark_return"
        ].var()
    )

    beta = (
        covariance
        / benchmark_variance
    )

    # -----------------------------------------------------
    # CORRELATION
    # -----------------------------------------------------

    correlation = (
        aligned[
            "portfolio_return"
        ]
        .corr(
            aligned[
                "benchmark_return"
            ]
        )
    )

    r_squared = (
        correlation ** 2
    )

    # -----------------------------------------------------
    # TRACKING ERROR
    # -----------------------------------------------------

    daily_tracking_error = (
        aligned[
            "active_return"
        ].std()
    )

    annualized_tracking_error = (
        daily_tracking_error
        * np.sqrt(
            trading_days
        )
    )

    # -----------------------------------------------------
    # ACTIVE RETURN
    # -----------------------------------------------------

    annualized_active_return = (
        aligned[
            "active_return"
        ].mean()
        * trading_days
    )

    # -----------------------------------------------------
    # INFORMATION RATIO
    # -----------------------------------------------------

    if annualized_tracking_error != 0:

        information_ratio = (
            annualized_active_return
            / annualized_tracking_error
        )

    else:

        information_ratio = np.nan
        

    # -----------------------------------------------------
    # CUMULATIVE COMPARISON
    # -----------------------------------------------------

    aligned[
        "portfolio_growth"
    ] = (
        1
        + aligned[
            "portfolio_return"
        ]
    ).cumprod()

    aligned[
        "benchmark_growth"
    ] = (
        1
        + aligned[
            "benchmark_return"
        ]
    ).cumprod()

    portfolio_cumulative_return = (
        aligned[
            "portfolio_growth"
        ].iloc[-1]
        - 1
    )

    benchmark_cumulative_return = (
        aligned[
            "benchmark_growth"
        ].iloc[-1]
        - 1
    )
    
    


    # -----------------------------------------------------
    # ADD DATABASE / POWER BI IDENTIFIERS
    # -----------------------------------------------------

    aligned[
        "benchmark"
    ] = "NIFTY 50"


    aligned = aligned[
        [
            "Date",
            "portfolio_id",
            "benchmark",
            "portfolio_return",
            "benchmark_return",
            "active_return",
            "portfolio_growth",
            "benchmark_growth",
        ]
    ]




    # -----------------------------------------------------
    # CREATE SUMMARY
    # -----------------------------------------------------

    summary = pd.DataFrame(
        [
            {
                "valuation_date":
                    valuation_date.date(),
                    
                "portfolio_id":
                    portfolio_id,

                "benchmark":
                    "NIFTY 50",

                "aligned_return_observations":
                    len(aligned),

                "start_date":
                    aligned[
                        "Date"
                    ].min().date(),

                "end_date":
                    aligned[
                        "Date"
                    ].max().date(),

                "beta":
                    beta,

                "correlation":
                    correlation,

                "r_squared":
                    r_squared,

                "portfolio_annualized_volatility":
                    portfolio_annualized_volatility,

                "benchmark_annualized_volatility":
                    benchmark_annualized_volatility,

                "annualized_tracking_error":
                    annualized_tracking_error,

                "annualized_active_return":
                    annualized_active_return,

                "information_ratio":
                    information_ratio,

                "portfolio_cumulative_return":
                    portfolio_cumulative_return,

                "benchmark_cumulative_return":
                    benchmark_cumulative_return,
            }
        ]
    )

    # -----------------------------------------------------
    # SAVE OUTPUTS
    # -----------------------------------------------------

    aligned.to_csv(
        ALIGNED_OUTPUT_PATH,
        index=False
    )

    summary.to_csv(
        SUMMARY_OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    print()
    print("=" * 75)
    print("PORTFOLIO VS NIFTY 50 BENCHMARK ANALYTICS")
    print("=" * 75)

    print(
        f"\nAligned return observations: "
        f"{len(aligned)}"
    )

    print(
        f"Start date: "
        f"{aligned['Date'].min().date()}"
    )

    print(
        f"End date: "
        f"{aligned['Date'].max().date()}"
    )

    print()
    print("-" * 75)
    print("MARKET RISK")
    print("-" * 75)

    print(
        f"Portfolio beta: "
        f"{beta:.4f}"
    )

    print(
        f"Portfolio / NIFTY correlation: "
        f"{correlation:.4f}"
    )

    print(
        f"R-squared: "
        f"{r_squared:.4f}"
    )

    print(
        f"Portfolio annualized volatility: "
        f"{portfolio_annualized_volatility:.4%}"
    )

    print(
        f"NIFTY annualized volatility: "
        f"{benchmark_annualized_volatility:.4%}"
    )

    print()
    print("-" * 75)
    print("BENCHMARK RELATIVE METRICS")
    print("-" * 75)

    print(
        f"Annualized tracking error: "
        f"{annualized_tracking_error:.4%}"
    )

    print(
        f"Annualized active return: "
        f"{annualized_active_return:.4%}"
    )

    print(
        f"Information ratio: "
        f"{information_ratio:.4f}"
    )

    print()

    print(
        f"Simulated portfolio cumulative return: "
        f"{portfolio_cumulative_return:.4%}"
    )

    print(
        f"NIFTY cumulative return: "
        f"{benchmark_cumulative_return:.4%}"
    )

    print()
    print(
        "Aligned portfolio/benchmark returns saved to:"
    )

    print(
        ALIGNED_OUTPUT_PATH
        .relative_to(PROJECT_ROOT)
    )

    print()

    print(
        "Benchmark risk summary saved to:"
    )

    print(
        SUMMARY_OUTPUT_PATH
        .relative_to(PROJECT_ROOT)
    )


if __name__ == "__main__":
    main()