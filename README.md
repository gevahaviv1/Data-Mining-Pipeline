# 🎓 Data Mining Pipeline — Exercise 1

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Algorithm](https://img.shields.io/badge/Algorithm-ID3%20Decision%20Tree-green)
![Status](https://img.shields.io/badge/Status-Complete%20✓-brightgreen)

A university assignment comprising three problems: **web crawling & data processing**, **theoretical questions**, and a **custom Decision Tree implementation (The Hujinator)**. Built with Python, Pandas, Selenium, BeautifulSoup, NumPy, and Matplotlib.

---

## 📁 Project Structure

```
ex1/
├── README.md
├── .gitignore
│
├── code/                              # Problem 1 — Web Crawling & Data Processing
│   ├── books_crawler.py               # Selenium + requests web crawler for bookdelivery.com
│   ├── process_data.py                # Pandas data processing, feature engineering & reporting
│   └── create_submission_zip.py       # Submission packaging script
│
├── output/                            # Generated data files (Problem 1)
│   ├── books_raw.csv                  # Raw scraped data (50 books)
│   ├── books_raw.json                 # Raw data in assignment JSON format
│   ├── books_example.json             # Single book example (null-stripped)
│   ├── books_before_sort.csv          # DataFrame before sorting by Title
│   ├── books_after_sort.csv           # DataFrame after sorting by Title (ascending)
│   ├── books_processed.csv            # Processed data with derived features
│   ├── books_processed.json           # Processed data in assignment JSON format
│   ├── books_processed_preview.csv    # First 10 rows preview
│   └── books_summary.csv             # Summary statistics for 5 required columns
│
├── Hujinator Files/                   # Problem 3 — Decision Tree (The Hujinator)
│   ├── hujinator.py                   # ID3 decision tree (entropy, IG, recursive builder)
│   ├── hujinator_1000.csv             # Training dataset (1000 samples, 6 features)
│   └── visualisation.py              # Tree visualization & summary utilities
│
└── theoretical/                       # Problem 2 — Theoretical Answers
    ├── ex1t_Q2.pdf                    # Theoretical question 2
    ├── ex1t_Q3.pdf                    # Theoretical question 3
    └── hujinator_tree.png             # Decision tree visualization
```

---

## 🕷 Problem 1: Web Crawling & Data Processing

### Overview

A full pipeline that crawls [bookdelivery.com](https://www.bookdelivery.com), extracts structured book data, and performs statistical analysis.

### `code/books_crawler.py`

- **Selenium WAF Bypass** — Solves AWS WAF JavaScript challenges, transfers cookies to a lightweight `requests.Session`.
- **Dynamic Category Discovery** — Extracts category URLs from embedded JSON in page scripts.
- **Polite Crawling** — Random delays (1–3s) between requests, max 5 pages per category.
- **Robust Parsing** — Extracts 17 fields per book (title, price, authors, star rating, dimensions, etc.).
- **JSON Format** — Exports in the required `{"records": {"record": [...]}}` structure with null-stripping.

### `code/process_data.py`

- **Feature Engineering** — Adds `NumberOfAuthors` (integer) and `IsExpensive` (1/0 based on median price).
- **Title Sorting** — Prints first 10 rows before/after sorting by Title; saves both snapshots.
- **Summary Statistics** — Computes mean, std, min, max, median for `Price in USD`, `Year`, `StarRating`, `NumberOfReviews`, `NumberOfAuthors`.
- **GroupBy Analysis** — Mean synopsis length by expensive/not-expensive.
- **Top/Bottom 5** — Identifies most and least expensive books.

### `code/create_submission_zip.py`

Interactive script to package all required files into a submission ZIP archive.

---

## 🎓 Problem 3: The Hujinator — Professor Popularity Predictor

### Overview

A custom **ID3 Decision Tree** that predicts whether a HUJI professor will be classified as **"Beloved"** based on teaching score, position, department, years of experience, and office type.

### Features

- **Custom Entropy Calculation** — Shannon entropy using log₂, with safe handling of zero-probability cases.
- **Information Gain** — Weighted entropy reduction to select the optimal splitting feature at each node.
- **Recursive Tree Building** — Full ID3 implementation with early stopping via `max_depth` and `min_samples_split`.
- **Tree Visualization** — Generates a publication-quality PNG using NetworkX and Matplotlib.

### Post-Mortem & Refactoring

The original code contained **7 critical bugs** that were identified and fixed:

- Inverted entropy formula (missing negation, wrong log base)
- Hardcoded weight instead of proportional subset weighting
- Reversed Information Gain subtraction
- Broken default parameters (`Ellipsis` instead of integers)
- Missing `max_depth` stopping condition
- Absurd gain threshold (200) making the tree collapse to a single leaf
- Incorrect use of `DataFrame.size` vs `len(DataFrame)`

### Key Findings

| Feature | Information Gain |
|---------|---------------:|
| Teaching_Score | 0.7027 |
| Position | 0.0286 |
| Department | 0.0072 |
| Years_at_HUJI | 0.0056 |
| Office_Type | 0.0000 |

**Conclusion:** Teaching quality is the dominant predictor — a high score guarantees "Beloved" status regardless of other factors.

---

## 🛠 Prerequisites & Installation

### Required Libraries

```
pandas
numpy
matplotlib
networkx
requests
beautifulsoup4
selenium
```

### Install

```bash
pip install pandas numpy matplotlib networkx requests beautifulsoup4 selenium
```

---

## 🚀 Usage

### Run the Web Crawler (Problem 1)

```bash
python code/books_crawler.py
```

### Run Data Processing (Problem 1)

```bash
python code/process_data.py
```

### Run the Hujinator (Problem 3)

```bash
cd "Hujinator Files"
python hujinator.py
```

---

## 🧮 How the Decision Tree Works

The algorithm selects features by maximizing **Information Gain (IG)**:

$$IG(S, A) = H(S) - \sum_{v \in \text{Values}(A)} \frac{|S_v|}{|S|} \cdot H(S_v)$$

where $H(S) = -\sum p_i \log_2(p_i)$ is the Shannon entropy. The tree recursively splits on the highest-IG feature until a stopping condition is met: pure leaf, no remaining features, zero gain, max depth, or insufficient samples.
