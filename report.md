# Exercise 1 – Web Crawling & Data Processing Report

---

## 1. Crawling Strategy

Our crawler targets `bookdelivery.com`, a site protected by AWS WAF (Web Application Firewall) that serves a JavaScript challenge page to automated HTTP clients, returning a 202 status with an empty body. To overcome this, we launch a visible (non-headless) Chrome browser via Selenium with automation-detection flags disabled. The browser loads the homepage, solves the WAF challenge natively, and produces valid session cookies. These cookies — along with the browser's User-Agent string — are then transferred to a lightweight `requests.Session`, which handles all subsequent HTTP calls at a fraction of the overhead. Category URLs are not hard-coded; instead, they are extracted dynamically from an inline JavaScript variable (`lassubcategorias`) embedded as a `JSON.parse(...)` call in every page's source, yielding the full list of 20 book categories without relying on fragile HTML menu selectors. For each category the crawler paginates through up to 5 listing pages, collecting individual book URLs via an `href` pattern matching `/p/\d+`. Every HTTP request is preceded by a random `time.sleep(1–3 s)` delay to comply with the assignment's politeness rule and avoid overloading the server. Each field extraction inside `parse_book_page` is wrapped in its own `try/except` block so that a single missing tag never crashes the run — the field simply defaults to `None`. The final dataset is exported as both `books.csv` and `books.json` (with `force_ascii=False` for correct Hebrew/Unicode support).

---

## 2. Single Book JSON Example

```json
{
  "Title": "Competition Law: Analysis, Cases, & Materials  - Ioannis Lianos; Valentine Korah; Paolo Siciliani",
  "Category": "Competition law and unfair competition. antitrust legislation",
  "Categories": "Law, International, Companies, Unfair Competition Antitrust Legislation",
  "Authors": "Ioannis Lianos, Valentine Korah, Paolo Siciliani",
  "Price in NIS": 386.36,
  "Year": "2019",
  "Synopsis": "This casebook, designed for a readership of graduate students, policy makers, and practitioners in competition law, aims to provide a comprehensive reference on EU and UK competition law. While the majority of the text comprises analysis supplemented with detailed commentary and analysis of judgments, NCA and Commission decisions, and legislation, the casebook also gives a high-level introduction to the design and history of EU and UK competition law, including an overview of the main actors and their objectives, furnishing students with the understanding of the law required to practise competition law. In particular, the casebook takes an interdisciplinary approach to the subject, featuring a substantial section on the economic context of competition law accessible even to those with no economics background. The book is accompanied by specialist volumes on intellectual property and enforcement and procedure.",
  "Synopsis length": 922,
  "Price in USD": 128.36,
  "StarRating": "None",
  "NumberOfReviews": 0,
  "Language": "English",
  "Format": "Paperback",
  "Dimensions": null,
  "Dimensions unit": null,
  "Weight": null,
  "Weight unit": null,
  "ISBN": "9780198826545"
}
```

---

## 3. Summary Statistics

| Metric   | Price in NIS | StarRating | Synopsis length |
|----------|-------------|------------|-----------------|
| Mean     | 75.91       | 4.85       | 1070.00         |
| Median   | 64.91       | 5.00       | 976.00          |
| Min      | 35.44       | 4.25       | 135.00          |
| Max      | 203.31      | 5.00       | 3478.00         |
| Std      | 36.04       | 0.27       | 646.16          |
| Count    | 50          | 12         | 50              |

> **Note:** `StarRating` has only 12 non-null values because 38 books had zero reviews, for which the rating is stored as the string `"None"` per assignment rules and is excluded from numerical statistics.

---

## 4. Analysis Results

### 4.1 Top 5 Most Expensive Books

| Title | Price in NIS |
|-------|-------------|
| The Numerical Discourses of the Buddha: A Complete Translation of the Anguttara Nikaya | 203.31 |
| Mein Kampf (German Language Edition) | 175.45 |
| Magnum Contact Sheets | 159.12 |
| The Philosophy of Being | 139.91 |
| Mein Kampf: The Official 1939 Edition | 139.36 |

### 4.2 Top 5 Least Expensive Books

| Title | Price in NIS |
|-------|-------------|
| Everybody Is a Poem: Midlife in Rhymes | 42.30 |
| Meditations – Marcus Aurelius | 37.83 |
| Romeo and Juliet (No Fear Shakespeare) | 37.23 |
| Meditations (Collins Classics) | 36.94 |
| The Diary of a Young Girl | 35.44 |

### 4.3 GroupBy Analysis — Mean Synopsis Length by Price Group

| Group                    | Mean Synopsis Length |
|--------------------------|---------------------|
| Not expensive (≤ median) | 911.36              |
| Expensive (> median)     | 1228.64             |

**Interpretation:** Books priced above the median (₪64.91) have a mean synopsis length of 1,228.64 characters, roughly 35% longer than the 911.36-character average for cheaper titles. This indicates that more expensive books tend to have longer, more detailed synopses — likely because they are larger, more specialized works that require more extensive descriptions.

---

*Report generated automatically by `process_data.py`.*
