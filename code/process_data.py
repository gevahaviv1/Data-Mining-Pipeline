import pandas as pd

INPUT_PATH = "output/books_raw.csv"
OUTPUT_PATH = "output/books_processed.csv"

STATS_COLUMNS = ["Price in NIS", "StarRating", "Synopsis length"]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Price in NIS"] = pd.to_numeric(df["Price in NIS"], errors="coerce")
    df["StarRating"] = pd.to_numeric(df["StarRating"], errors="coerce")
    df["Synopsis length"] = pd.to_numeric(df["Synopsis length"], errors="coerce")
    return df


def add_num_authors(df: pd.DataFrame) -> pd.DataFrame:
    def _count(val: str) -> int:
        if not val.strip():
            return 0
        parts = [a.strip() for a in val.replace(",", ";").split(";")]
        return len([p for p in parts if p])

    df["num_authors"] = df["Authors"].fillna("").apply(_count)
    return df


def add_is_expensive(df: pd.DataFrame) -> pd.DataFrame:
    median_price = df["Price in NIS"].median()
    df["is_expensive"] = df["Price in NIS"] > median_price
    print(f"Price in NIS median (threshold): {median_price:.2f}\n")
    return df


def print_summary_statistics(df: pd.DataFrame) -> None:
    print("=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)

    for col in STATS_COLUMNS:
        series = df[col].dropna()
        print(f"\n  {col}")
        print(f"  {'-' * len(col)}")
        print(f"    Mean:   {series.mean():.2f}")
        print(f"    Median: {series.median():.2f}")
        print(f"    Min:    {series.min():.2f}")
        print(f"    Max:    {series.max():.2f}")
        print(f"    Std:    {series.std():.2f}")
        print(f"    Count:  {len(series)}")

    print("\n" + "=" * 60)


def main():
    df = load_data(INPUT_PATH)
    print(f"Loaded {len(df)} rows from {INPUT_PATH}\n")

    df = add_num_authors(df)
    df = add_is_expensive(df)

    print_summary_statistics(df)

    print("\n\nVERIFICATION — first 5 rows:")
    print(df[["Title", "num_authors", "Price in NIS", "is_expensive"]].head().to_string())

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n[*] Saved processed data to {OUTPUT_PATH} ({len(df)} rows)")


if __name__ == "__main__":
    main()
