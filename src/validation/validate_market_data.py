from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SECURITY_MASTER_PATH = (
    PROJECT_ROOT / "data" / "reference" / "dim_security.csv"
)

MARKET_DATA_DIR = (
    PROJECT_ROOT / "data" / "raw" / "market_prices"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "market_data_validation_summary.csv"
)


REQUIRED_COLUMNS = [
    "Date",
    "Adj Close",
    "Close",
    "High",
    "Low",
    "Open",
    "Volume",
]


def validate_file(ticker, file_path):

    result = {
        "ticker": ticker,
        "file_exists": file_path.exists(),
        "row_count": 0,
        "missing_values": 0,
        "duplicate_dates": 0,
        "invalid_high_low": 0,
        "invalid_prices": 0,
        "invalid_volume": 0,
        "status": "PASS",
    }

    if not file_path.exists():
        result["status"] = "FAIL"
        return result

    df = pd.read_csv(file_path)

    result["row_count"] = len(df)

    # Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        result["status"] = "FAIL"
        return result

    # Convert Date
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Count missing values
    result["missing_values"] = int(
        df[REQUIRED_COLUMNS].isna().sum().sum()
    )

    # Duplicate trading dates
    result["duplicate_dates"] = int(
        df["Date"].duplicated().sum()
    )

    # High should never be below Low
    result["invalid_high_low"] = int(
        (df["High"] < df["Low"]).sum()
    )

    # Prices should be positive
    price_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
    ]

    result["invalid_prices"] = int(
        (df[price_columns] <= 0)
        .any(axis=1)
        .sum()
    )

    # Volume should not be negative
    result["invalid_volume"] = int(
        (df["Volume"] < 0).sum()
    )

    # Final status
    if (
        result["row_count"] < 500
        or result["missing_values"] > 0
        or result["duplicate_dates"] > 0
        or result["invalid_high_low"] > 0
        or result["invalid_prices"] > 0
        or result["invalid_volume"] > 0
    ):
        result["status"] = "FAIL"

    return result


def main():

    securities = pd.read_csv(
        SECURITY_MASTER_PATH
    )

    results = []

    for ticker in securities["ticker"]:

        filename = (
            ticker.replace(".NS", "")
            + ".csv"
        )

        file_path = (
            MARKET_DATA_DIR / filename
        )

        result = validate_file(
            ticker,
            file_path
        )

        results.append(result)

    validation_df = pd.DataFrame(
        results
    )

    validation_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print()
    print("=" * 70)
    print("MARKET DATA VALIDATION SUMMARY")
    print("=" * 70)

    print(
        validation_df.to_string(
            index=False
        )
    )

    print()
    print(
        "PASS:",
        (validation_df["status"] == "PASS").sum()
    )

    print(
        "FAIL:",
        (validation_df["status"] == "FAIL").sum()
    )

    print()
    print(
        f"Validation report saved to:"
        f"\n{OUTPUT_PATH.relative_to(PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    main()