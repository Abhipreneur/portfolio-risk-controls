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

MARKET_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "market_prices"
)

LIQUIDITY_PARAMETERS_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "liquidity_parameters.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "liquidity_risk.csv"
)


# ---------------------------------------------------------
# LOAD PARAMETERS
# ---------------------------------------------------------

def load_parameters():

    parameters = pd.read_csv(
        LIQUIDITY_PARAMETERS_PATH
    )

    parameter_dict = dict(
        zip(
            parameters["parameter_name"],
            parameters["parameter_value"]
        )
    )

    adv_lookback_days = int(
        parameter_dict[
            "adv_lookback_days"
        ]
    )

    max_participation_rate = float(
        parameter_dict[
            "max_participation_rate"
        ]
    ) / 100

    return (
        adv_lookback_days,
        max_participation_rate
    )


# ---------------------------------------------------------
# CALCULATE ADV
# ---------------------------------------------------------

def calculate_adv(
    ticker,
    valuation_date,
    lookback_days
):

    filename = (
        ticker.replace(
            ".NS",
            ""
        )
        + ".csv"
    )

    file_path = (
        MARKET_DATA_DIR
        / filename
    )

    df = pd.read_csv(
        file_path
    )

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    valuation_date = pd.to_datetime(
        valuation_date
    )

    # Use only completed data up to valuation date
    df = (
        df[
            df["Date"]
            <= valuation_date
        ]
        .sort_values("Date")
        .copy()
    )

    if len(df) < lookback_days:

        raise ValueError(
            f"Not enough volume history for "
            f"{ticker}"
        )

    recent_volume = (
        df
        .tail(
            lookback_days
        )[
            "Volume"
        ]
    )

    adv = float(
        recent_volume.mean()
    )

    return adv


# ---------------------------------------------------------
# LIQUIDITY CLASSIFICATION
# ---------------------------------------------------------

def classify_liquidity(
    days_to_liquidate
):

    if days_to_liquidate <= 1:
        return "HIGH"

    elif days_to_liquidate <= 3:
        return "MEDIUM"

    else:
        return "LOW"


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    positions = pd.read_csv(
        POSITIONS_PATH
    )

    (
        adv_lookback_days,
        max_participation_rate
    ) = load_parameters()

    valuation_date = (
        positions.loc[
            0,
            "valuation_date"
        ]
    )

    print()
    print("=" * 70)
    print("PORTFOLIO LIQUIDITY RISK ANALYTICS")
    print("=" * 70)

    print(
        f"\nValuation date: "
        f"{valuation_date}"
    )

    print(
        f"ADV lookback: "
        f"{adv_lookback_days} trading days"
    )

    print(
        f"Maximum participation rate: "
        f"{max_participation_rate:.0%}"
    )

    results = []

    # -----------------------------------------------------
    # CALCULATE LIQUIDITY FOR EACH POSITION
    # -----------------------------------------------------

    for _, row in positions.iterrows():

        ticker = row[
            "ticker"
        ]

        quantity = float(
            row[
                "quantity"
            ]
        )

        market_value = float(
            row[
                "market_value"
            ]
        )

        adv_shares = calculate_adv(
            ticker=ticker,
            valuation_date=valuation_date,
            lookback_days=adv_lookback_days
        )

        position_pct_adv = (
            quantity
            / adv_shares
            * 100
        )

        daily_liquidation_capacity = (
            adv_shares
            * max_participation_rate
        )

        days_to_liquidate = (
            quantity
            / daily_liquidation_capacity
        )

        liquidity_class = (
            classify_liquidity(
                days_to_liquidate
            )
        )

        results.append(
            {
                "valuation_date":
                    valuation_date,

                "portfolio_id":
                    row["portfolio_id"],

                "security_id":
                    row["security_id"],

                "ticker":
                    ticker,

                "company_name":
                    row["company_name"],

                "sector":
                    row["sector"],

                "quantity":
                    quantity,

                "market_value":
                    market_value,

                "adv_lookback_days":
                    adv_lookback_days,

                "adv_shares":
                    adv_shares,

                "position_pct_adv":
                    position_pct_adv,

                "max_participation_rate":
                    max_participation_rate,

                "daily_liquidation_capacity":
                    daily_liquidation_capacity,

                "days_to_liquidate":
                    days_to_liquidate,

                "liquidity_class":
                    liquidity_class,
            }
        )

    liquidity = pd.DataFrame(
        results
    )

    liquidity = (
        liquidity
        .sort_values(
            "days_to_liquidate",
            ascending=False
        )
        .reset_index(drop=True)
    )

    liquidity[
        "liquidity_rank"
    ] = (
        liquidity.index + 1
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    liquidity.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print()
    print("-" * 70)
    print("TOP LIQUIDITY RISKS")
    print("-" * 70)

    print(
        liquidity[
            [
                "liquidity_rank",
                "ticker",
                "quantity",
                "adv_shares",
                "position_pct_adv",
                "days_to_liquidate",
                "liquidity_class",
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

    print()

    print(
        f"Maximum days to liquidate: "
        f"{liquidity['days_to_liquidate'].max():.4f}"
    )

    print(
        f"Average days to liquidate: "
        f"{liquidity['days_to_liquidate'].mean():.4f}"
    )

    print()

    print(
        "Liquidity classifications:"
    )

    print(
        liquidity[
            "liquidity_class"
        ]
        .value_counts()
        .to_string()
    )

    print()

    print(
        "Liquidity risk saved to:"
    )

    print(
        OUTPUT_PATH
        .relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()