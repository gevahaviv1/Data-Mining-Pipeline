import json
import math
import os
import random
import re
import time
from pprint import pprint
from typing import List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://www.bookdelivery.com"
NIS_TO_USD_RATE = 3.01
REQUEST_TIMEOUT = 20

# ---------------------------------------------------------------------------
# Browser / Session helpers
# ---------------------------------------------------------------------------

def _create_session() -> Tuple[requests.Session, str]:
    """Launch a visible Chrome to solve the AWS WAF challenge, then
    transfer the cookies to a lightweight requests.Session."""
    print("[*] Launching browser to solve WAF challenge …")
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=opts)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": 'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'},
    )
    driver.get(BASE_URL)
    time.sleep(12)

    user_agent = driver.execute_script("return navigator.userAgent")
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
    first_page_html = driver.page_source
    driver.quit()
    print("[*] WAF challenge solved – cookies transferred to session.")

    session = requests.Session()
    session.headers["User-Agent"] = user_agent
    for k, v in cookies.items():
        session.cookies.set(k, v)

    return session, first_page_html


def _polite_get(session: requests.Session, url: str) -> Optional[str]:
    """GET with politeness delay and error handling."""
    time.sleep(random.uniform(1, 3))
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        print(f"  [!] Request failed for {url}: {exc}")
        return None

# ---------------------------------------------------------------------------
# Ficha (product‑details table) helpers
# ---------------------------------------------------------------------------

def _get_ficha_map(soup: BeautifulSoup) -> dict:
    """Build a label→value mapping from the product details ('ficha') section."""
    ficha = soup.find("div", class_="ficha")
    if not ficha:
        return {}

    data = {}
    for row in ficha.find_all("div", class_="row"):
        children = [c for c in row.children if hasattr(c, "name") and c.name]
        if len(children) >= 2:
            label = children[0].get_text(strip=True)
            value = children[1].get_text(strip=True)
            data[label] = value
    return data

# ---------------------------------------------------------------------------
# Individual field extractors
# ---------------------------------------------------------------------------

def _extract_title(soup: BeautifulSoup) -> Optional[str]:
    try:
        return soup.find("h1").get_text(strip=True)
    except Exception:
        return None


def _extract_category(ficha: dict) -> Optional[str]:
    try:
        return ficha.get("Categories")
    except Exception:
        return None


def _extract_categories(soup: BeautifulSoup) -> Optional[str]:
    try:
        ficha_div = soup.find("div", class_="ficha")
        if not ficha_div:
            return None
        for row in ficha_div.find_all("div", class_="row"):
            children = [c for c in row.children if hasattr(c, "name") and c.name]
            if len(children) >= 2 and children[0].get_text(strip=True) == "Categories":
                cat_link = children[1].find("a", href=True)
                if cat_link:
                    parts = [
                        p.replace("-", " ").title()
                        for p in cat_link["href"].split("/")
                        if p and p not in ("il-en", "books")
                    ]
                    return ", ".join(parts)
                break
        return None
    except Exception:
        return None


def _extract_price_nis(soup: BeautifulSoup) -> Optional[float]:
    try:
        raw = soup.find("strong", class_="precio").get_text(strip=True)
        return float(re.sub(r"[^\d.]", "", raw))
    except Exception:
        return None


def _convert_price_to_usd(price_nis: Optional[float]) -> Optional[float]:
    try:
        if price_nis is None:
            return None
        return math.ceil(price_nis * 100 / NIS_TO_USD_RATE) / 100
    except Exception:
        return None


def _extract_synopsis(soup: BeautifulSoup) -> Optional[str]:
    try:
        return soup.find(id="texto-descripcion").get_text(strip=True)
    except Exception:
        return None


def _extract_reviews(soup: BeautifulSoup) -> Tuple:
    try:
        resume = soup.find("div", class_="reviews-body-resume")
        total_reviews = 0
        weighted_sum = 0
        if resume:
            for li in resume.find_all("li"):
                cls = " ".join(li.get("class", []))
                star_match = re.search(r"stars-(\d+)", cls)
                count_match = re.search(r"\((\d+)\)", li.get_text())
                if star_match and count_match:
                    stars = int(star_match.group(1))
                    count = int(count_match.group(1))
                    weighted_sum += stars * count
                    total_reviews += count
        if total_reviews > 0:
            star_rating = math.ceil(weighted_sum / total_reviews * 100) / 100
        else:
            star_rating = "None"
        return star_rating, total_reviews
    except Exception:
        return "None", 0


def _extract_dimensions(ficha: dict) -> Tuple:
    try:
        raw = ficha.get("Dimensions")
        if not raw:
            return None, None
        nums = re.findall(r"[\d.]+", raw)
        dimensions = ", ".join(nums) if nums else None
        unit_match = re.search(r"[a-zA-Z]+", raw.replace("x", ""))
        dimensions_unit = unit_match.group() if unit_match else None
        return dimensions, dimensions_unit
    except Exception:
        return None, None


def _extract_weight(ficha: dict) -> Tuple:
    try:
        raw = ficha.get("Weight")
        if not raw:
            return None, None
        w_match = re.search(r"([\d.]+)", raw)
        weight = float(w_match.group(1)) if w_match else None
        wu_match = re.search(r"[a-zA-Z]+", raw)
        weight_unit = wu_match.group() if wu_match else None
        return weight, weight_unit
    except Exception:
        return None, None

# ---------------------------------------------------------------------------
# Page parser (accepts raw HTML string)
# ---------------------------------------------------------------------------

def parse_book_page(html_content: str) -> dict:
    soup = BeautifulSoup(html_content, "html.parser")
    ficha = _get_ficha_map(soup)

    title = _extract_title(soup)
    category = _extract_category(ficha)
    categories = _extract_categories(soup)
    raw_authors = ficha.get("Author")
    authors = raw_authors.replace(";", ",") if raw_authors else None
    price_nis = _extract_price_nis(soup)
    price_usd = _convert_price_to_usd(price_nis)
    year = ficha.get("Year")
    synopsis = _extract_synopsis(soup)
    synopsis_length = len(synopsis) if synopsis else None
    star_rating, number_of_reviews = _extract_reviews(soup)
    language = ficha.get("Language")
    book_format = ficha.get("Format")
    dimensions, dimensions_unit = _extract_dimensions(ficha)
    weight, weight_unit = _extract_weight(ficha)
    isbn = ficha.get("ISBN13") or ficha.get("ISBN")

    return {
        "Title": title,
        "Category": category,
        "Categories": categories,
        "Authors": authors,
        "Price in NIS": price_nis,
        "Year": year,
        "Synopsis": synopsis,
        "Synopsis length": synopsis_length,
        "Price in USD": price_usd,
        "StarRating": star_rating,
        "NumberOfReviews": number_of_reviews,
        "Language": language,
        "Format": book_format,
        "Dimensions": dimensions,
        "Dimensions unit": dimensions_unit,
        "Weight": weight,
        "Weight unit": weight_unit,
        "ISBN": isbn,
    }

# ---------------------------------------------------------------------------
# Crawling helpers
# ---------------------------------------------------------------------------

def get_category_links(html_content: str) -> List[dict]:
    """Extract category names and URLs from the inline JS embedded in any page."""
    match = re.search(
        r"JSON\.parse\('\s*(\[.+?\])\s*'\)",
        html_content,
    )
    if not match:
        print("[!] Could not find category data in page source.")
        return []

    categories = json.loads(match.group(1))
    return [
        {"title": c["title"], "url": BASE_URL + c["url"]}
        for c in categories
    ]


def get_book_links_from_category(
    session: requests.Session,
    category_url: str,
    max_pages: int = 5,
) -> List[str]:
    """Paginate through a category and collect individual book URLs."""
    book_links = []
    for page in range(1, max_pages + 1):
        page_url = f"{category_url}?page={page}"
        print(f"    Fetching page {page}: {page_url}")
        html = _polite_get(session, page_url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        links = {
            BASE_URL + a["href"]
            for a in soup.find_all("a", href=re.compile(r"/p/\d+"))
            if a["href"].startswith("/")
        }
        if not links:
            print(f"    No books found on page {page} – stopping pagination.")
            break

        book_links.extend(sorted(links))
        print(f"    Found {len(links)} books on page {page}")

    unique = list(dict.fromkeys(book_links))
    print(f"    Total unique book links in category: {len(unique)}")
    return unique

# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def main(max_pages: int = 5, max_categories: Optional[int] = None):
    session, first_page_html = _create_session()

    categories = get_category_links(first_page_html)
    if not categories:
        print("[!] No categories found. Exiting.")
        return

    if max_categories is not None:
        categories = categories[:max_categories]

    print(f"\n[*] Crawling {len(categories)} categories (max {max_pages} pages each)\n")

    all_books_data: List[dict] = []

    for cat_idx, cat in enumerate(categories, 1):
        print(f"[{cat_idx}/{len(categories)}] Scraping category: {cat['title']}")
        book_urls = get_book_links_from_category(session, cat["url"], max_pages)

        for book_idx, book_url in enumerate(book_urls, 1):
            print(f"  Fetching book {book_idx}/{len(book_urls)}: {book_url}")
            html = _polite_get(session, book_url)
            if not html:
                continue
            try:
                data = parse_book_page(html)
                all_books_data.append(data)
            except Exception as exc:
                print(f"  [!] Parse error for {book_url}: {exc}")

    print(f"\n[*] Scraping complete – {len(all_books_data)} books collected.")

    if not all_books_data:
        print("[!] No data to save.")
        return

    df = pd.DataFrame(all_books_data)
    os.makedirs("output", exist_ok=True)
    df.to_csv("output/books.csv", index=False, encoding="utf-8-sig")
    records_json = {
        "records": [{"record": row} for row in df.to_dict(orient="records")]
    }
    with open("output/books.json", "w", encoding="utf-8") as jf:
        json.dump(records_json, jf, indent=2, ensure_ascii=False)
    print(f"[*] Saved output/books.csv  ({len(df)} rows)")
    print(f"[*] Saved output/books.json ({len(df)} records)")


if __name__ == "__main__":
    main(max_pages=5)
