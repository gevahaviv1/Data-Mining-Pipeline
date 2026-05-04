import re
from pprint import pprint

from bs4 import BeautifulSoup


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


def parse_book_page(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    ficha = _get_ficha_map(soup)

    # --- Title ---
    try:
        title = soup.find("h1").get_text(strip=True)
    except Exception:
        title = None

    # --- Category (top-level from the ficha Categories row) ---
    try:
        category = ficha.get("Categories")
    except Exception:
        category = None

    # --- Categories (breadcrumb path extracted from the category link href) ---
    try:
        categories = None
        ficha_div = soup.find("div", class_="ficha")
        if ficha_div:
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
                        categories = ", ".join(parts)
                    break
    except Exception:
        categories = None

    # --- Authors ---
    try:
        authors = ficha.get("Author")
    except Exception:
        authors = None

    # --- Price in NIS (numeric float only) ---
    try:
        price_tag = soup.find("strong", class_="precio")
        raw_price = price_tag.get_text(strip=True)
        price = float(re.sub(r"[^\d.]", "", raw_price))
    except Exception:
        price = None

    # --- Year ---
    try:
        year = ficha.get("Year")
    except Exception:
        year = None

    # --- Synopsis ---
    try:
        synopsis = soup.find(id="texto-descripcion").get_text(strip=True)
    except Exception:
        synopsis = None

    # --- Synopsis length ---
    synopsis_length = len(synopsis) if synopsis else None

    return {
        "Title": title,
        "Category": category,
        "Categories": categories,
        "Authors": authors,
        "Price in NIS": price,
        "Year": year,
        "Synopsis": synopsis,
        "Synopsis length": synopsis_length,
    }


if __name__ == "__main__":
    result = parse_book_page("book_example.html")
    pprint(result)
