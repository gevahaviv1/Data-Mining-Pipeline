from bs4 import BeautifulSoup


def parse_book_page(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("h1").get_text(strip=True)

    return {"Title": title}


if __name__ == "__main__":
    result = parse_book_page("book_example.html")
    print(result)
