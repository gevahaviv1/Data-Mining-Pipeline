import os
import sys
import zipfile

REQUIRED_FILES = [
    "code/books_crawler.py",
    "code/process_data.py",
    "report.pdf",
    "output/books_raw.csv",
    "output/books_raw.json",
    "output/books_example.json",
    "output/books_example.jpg",
    "output/books_before_sort.csv",
    "output/books_after_sort.csv",
    "output/books_processed.csv",
    "output/books_processed.json",
    "output/books_processed_preview.csv",
    "output/books_summary.csv",
]

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def collect_ids() -> list:
    print("Enter student IDs (up to 3). Press Enter on an empty line when done.\n")
    ids = []
    for i in range(1, 4):
        sid = input(f"  Student ID #{i} (or Enter to finish): ").strip()
        if not sid:
            break
        ids.append(sid)
    if not ids:
        print("[!] No IDs entered. Aborting.")
        sys.exit(1)
    return ids


def verify_files() -> list:
    missing = []
    for f in REQUIRED_FILES:
        full = os.path.join(PROJECT_ROOT, f)
        if not os.path.isfile(full):
            missing.append(f)
    return missing


def create_zip(ids: list) -> str:
    zip_name = "ex1p_" + "_".join(ids) + ".zip"
    zip_path = os.path.join(PROJECT_ROOT, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in REQUIRED_FILES:
            full = os.path.join(PROJECT_ROOT, f)
            zf.write(full, arcname=f)

    return zip_path


def main():
    os.chdir(PROJECT_ROOT)

    ids = collect_ids()
    print(f"\n[*] Student IDs: {', '.join(ids)}")

    missing = verify_files()
    if missing:
        print("\n[!] WARNING — the following required files are missing:")
        for m in missing:
            print(f"    - {m}")
        ans = input("\nContinue anyway and zip only existing files? (y/n): ").strip().lower()
        if ans != "y":
            print("Aborting.")
            sys.exit(1)

    zip_path = create_zip(ids)
    print(f"\n[*] Submission zip created: {zip_path}")
    print(f"    Size: {os.path.getsize(zip_path) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
