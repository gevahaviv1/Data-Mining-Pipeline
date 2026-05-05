import pandas as pd

INPUT_PATH = "output/books.csv"
OUTPUT_PATH = "output/books_processed.csv"

STATS_COLUMNS = ["Price in NIS", "StarRating", "Synopsis length"]
SUMMARY_COLUMNS = ["Price in USD", "Year", "StarRating", "NumberOfReviews", "NumberOfAuthors"]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["Price in NIS", "Price in USD", "Year", "StarRating",
                "NumberOfReviews", "Synopsis length"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def add_num_authors(df: pd.DataFrame) -> pd.DataFrame:
    def _count(val: str) -> int:
        if not val.strip():
            return 0
        parts = [a.strip() for a in val.replace(",", ";").split(";")]
        return len([p for p in parts if p])

    df["NumberOfAuthors"] = df["Authors"].fillna("").apply(_count)
    return df


def add_is_expensive(df: pd.DataFrame) -> pd.DataFrame:
    median_price = df["Price in NIS"].median()
    df["IsExpensive"] = (df["Price in NIS"] > median_price).astype(int)
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

    print("\n\nVERIFICATION — first 10 rows:")
    preview = df.head(10)
    print(preview[["Title", "NumberOfAuthors", "Price in NIS", "IsExpensive"]].to_string())

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n[*] Saved processed data to {OUTPUT_PATH} ({len(df)} rows)")

    df.to_json(
        "output/books_processed.json", orient="records", indent=2, force_ascii=False,
    )
    print(f"[*] Saved output/books_processed.json ({len(df)} records)")

    preview.to_csv("output/books_processed_preview.csv", index=False, encoding="utf-8-sig")
    print(f"[*] Saved output/books_processed_preview.csv ({len(preview)} rows)")

    generate_summary(df)

    print("\n\n" + "=" * 60)
    print("GROUPBY ANALYSIS — Mean Synopsis Length by is_expensive")
    print("=" * 60)
    grouped = df.groupby("IsExpensive")["Synopsis length"].mean()
    for flag, mean_val in grouped.items():
        label = "Expensive (> median)" if flag == 1 else "Not expensive (<= median)"
        print(f"  {label:30s}  {mean_val:.2f}")
    print("=" * 60)

    df_sorted = df.sort_values("Price in NIS", ascending=False)
    df_sorted.to_csv("output/books_sorted.csv", index=False, encoding="utf-8-sig")
    print(f"\n[*] Saved sorted data to output/books_sorted.csv")

    print("\n\n" + "=" * 60)
    print("TOP 5 MOST EXPENSIVE BOOKS")
    print("=" * 60)
    top5 = df_sorted[["Title", "Price in NIS"]].head(5)
    print(top5.to_string(index=False))

    print("\n" + "=" * 60)
    print("TOP 5 LEAST EXPENSIVE BOOKS")
    print("=" * 60)
    bottom5 = df_sorted[["Title", "Price in NIS"]].tail(5)
    print(bottom5.to_string(index=False))
    print("=" * 60)


def generate_summary(df: pd.DataFrame) -> None:
    numeric_df = df[SUMMARY_COLUMNS].copy()
    for col in SUMMARY_COLUMNS:
        numeric_df[col] = pd.to_numeric(numeric_df[col], errors="coerce")

    summary = numeric_df.agg(["mean", "std", "min", "max", "median"]).round(2)
    total_row = pd.DataFrame(
        {col: [len(df)] for col in SUMMARY_COLUMNS}, index=["total_rows"],
    )
    summary = pd.concat([summary, total_row])

    print("\n\n" + "=" * 60)
    print("ASSIGNMENT SUMMARY STATISTICS")
    print("=" * 60)
    print(summary.to_string())
    print("=" * 60)

    summary.to_csv("output/books_summary.csv", encoding="utf-8-sig")
    print(f"[*] Saved output/books_summary.csv")


if __name__ == "__main__":
    main()
