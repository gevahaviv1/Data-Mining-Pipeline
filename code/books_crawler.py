import math
import re
from pprint import pprint
from typing import Optional, Tuple

from bs4 import BeautifulSoup

NIS_TO_USD_RATE = 3.01


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


def parse_book_page(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    ficha = _get_ficha_map(soup)

    title = _extract_title(soup)
    category = _extract_category(ficha)
    categories = _extract_categories(soup)
    authors = ficha.get("Author")
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


if __name__ == "__main__":
    result = parse_book_page("book_example.html")
    pprint(result)
