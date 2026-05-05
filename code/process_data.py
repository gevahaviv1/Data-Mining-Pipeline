import json
import math
import sys

import pandas as pd

sys.path.insert(0, "code")

INPUT_PATH = "output/books_raw.csv"
OUTPUT_PATH = "output/books_processed.csv"

SUMMARY_COLUMNS = ["Price in USD", "Year", "StarRating", "NumberOfReviews", "NumberOfAuthors"]


def _strip_nulls(d: dict) -> dict:
    return {
        k: v for k, v in d.items()
        if v is not None and v != ""
        and not (isinstance(v, float) and math.isnan(v))
    }


def _save_assignment_json(df: pd.DataFrame, path: str) -> None:
    clean_rows = [_strip_nulls(row) for row in df.to_dict(orient="records")]
    payload = {"records": {"record": clean_rows}}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


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
    print("SUMMARY STATISTICS (Assignment Step 5)")
    print("=" * 60)
    print(summary.to_string())
    print("=" * 60)

    summary.to_csv("output/books_summary.csv", encoding="utf-8-sig")
    print("[*] Saved output/books_summary.csv")


def main():
    df = load_data(INPUT_PATH)
    print(f"Loaded {len(df)} rows from {INPUT_PATH}\n")

    df = add_num_authors(df)
    df = add_is_expensive(df)

    # --- Step 3: Before / After sorting by Title ---
    print("=" * 60)
    print("FIRST 10 ROWS — BEFORE SORTING")
    print("=" * 60)
    print(df[["Title", "NumberOfAuthors", "Price in NIS", "IsExpensive"]].head(10).to_string())
    df.to_csv("output/books_before_sort.csv", index=False, encoding="utf-8-sig")
    print("[*] Saved output/books_before_sort.csv")

    df = df.sort_values("Title", ascending=True).reset_index(drop=True)

    print("\n" + "=" * 60)
    print("FIRST 10 ROWS — AFTER SORTING BY TITLE (ascending)")
    print("=" * 60)
    print(df[["Title", "NumberOfAuthors", "Price in NIS", "IsExpensive"]].head(10).to_string())
    df.to_csv("output/books_after_sort.csv", index=False, encoding="utf-8-sig")
    print("[*] Saved output/books_after_sort.csv")

    # --- Save processed CSV ---
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n[*] Saved {OUTPUT_PATH} ({len(df)} rows)")

    # --- Save processed JSON (null-stripped, assignment structure) ---
    _save_assignment_json(df, "output/books_processed.json")
    print(f"[*] Saved output/books_processed.json ({len(df)} records)")

    # --- Preview (first 10 rows) ---
    preview = df.head(10)
    preview.to_csv("output/books_processed_preview.csv", index=False, encoding="utf-8-sig")
    print(f"[*] Saved output/books_processed_preview.csv ({len(preview)} rows)")

    # --- Summary statistics ---
    generate_summary(df)

    # --- GroupBy analysis ---
    print("\n\n" + "=" * 60)
    print("GROUPBY ANALYSIS — Mean Synopsis Length by IsExpensive")
    print("=" * 60)
    grouped = df.groupby("IsExpensive")["Synopsis length"].mean()
    for flag, mean_val in grouped.items():
        label = "Expensive (> median)" if flag == 1 else "Not expensive (<= median)"
        print(f"  {label:30s}  {mean_val:.2f}")
    print("=" * 60)

    # --- Top 5 / Bottom 5 by price ---
    df_by_price = df.sort_values("Price in NIS", ascending=False)

    print("\n\n" + "=" * 60)
    print("TOP 5 MOST EXPENSIVE BOOKS")
    print("=" * 60)
    print(df_by_price[["Title", "Price in NIS"]].head(5).to_string(index=False))

    print("\n" + "=" * 60)
    print("TOP 5 LEAST EXPENSIVE BOOKS")
    print("=" * 60)
    print(df_by_price[["Title", "Price in NIS"]].tail(5).to_string(index=False))
    print("=" * 60)


if __name__ == "__main__":
    main()
