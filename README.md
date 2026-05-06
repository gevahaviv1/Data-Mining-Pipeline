# 🎓 The Hujinator — Professor Popularity Predictor

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Algorithm](https://img.shields.io/badge/Algorithm-ID3%20Decision%20Tree-green)
![Status](https://img.shields.io/badge/Status-Bug--Free%20✓-brightgreen)

A custom implementation of the **ID3 Decision Tree algorithm** built from scratch using Python. The Hujinator predicts whether a Hebrew University (HUJI) professor will be classified as **"Beloved"** by students, based on features such as teaching score, position, department, years of experience, and office type.

---

## ✨ Features

- **Custom Entropy Calculation** — Shannon entropy using log₂, with safe handling of zero-probability cases.
- **Information Gain** — Weighted entropy reduction to select the optimal splitting feature at each node.
- **Recursive Tree Building** — Full ID3 implementation with early stopping via `max_depth` and `min_samples_split` pruning parameters.
- **Tree Visualization** — Generates a publication-quality PNG image of the decision tree using NetworkX and Matplotlib.
- **Console Summary** — Prints total node count and leaf count after training.

---

## 📁 File Structure

```
Hujinator Files/
├── hujinator.py            # Core decision tree logic (entropy, IG, recursive builder)
├── hujinator_1000.csv      # Training dataset (1000 samples, 6 features + target)
├── visualisation.py        # Tree visualization & summary utilities
├── hujinator_tree.png      # Generated tree image (after running the script)
└── README.md               # This file
```

| File | Description |
|------|-------------|
| `hujinator.py` | Main script — loads data, builds the decision tree, and triggers visualization. |
| `hujinator_1000.csv` | Dataset with columns: `Student_ID`, `Position`, `Department`, `Teaching_Score`, `Years_at_HUJI`, `Office_Type`, `Beloved`. |
| `visualisation.py` | Helper module providing `print_tree_summary()` and `generate_tree_image()` functions. |

---

## 🛠 Prerequisites & Installation

### Required Libraries

```
pandas
numpy
matplotlib
networkx
```

### Install

```bash
pip install pandas numpy matplotlib networkx
```

---

## 🚀 Usage

Run the main script from within the project directory:

```bash
cd "Hujinator Files"
python hujinator.py
```

This will:
1. Load `hujinator_1000.csv`
2. Build the decision tree using all features (excluding `Student_ID`)
3. Print a tree summary (total nodes & leaves) to the console
4. Save the tree visualization as `hujinator_tree.png`

---

## 🧮 How It Works

The algorithm selects features by maximizing **Information Gain (IG)**, defined as:

$$IG(S, A) = H(S) - \sum_{v \in \text{Values}(A)} \frac{|S_v|}{|S|} \cdot H(S_v)$$

where $H(S) = -\sum p_i \log_2(p_i)$ is the Shannon entropy of the target variable. The tree recursively splits on the feature with the highest IG until a stopping condition is met: pure leaf, no remaining features, zero gain, maximum depth reached, or insufficient samples to split.

---

## 🔧 Post-Mortem & Refactoring

The original code contained **7 critical bugs** introduced during development, including:

- Inverted entropy formula (missing negation, wrong log base)
- Hardcoded weight instead of proportional subset weighting
- Reversed Information Gain subtraction
- Broken default parameters (`Ellipsis` instead of integers)
- Missing `max_depth` stopping condition
- Absurd gain threshold (200) making the tree collapse to a single leaf
- Incorrect use of `DataFrame.size` vs `len(DataFrame)`

All bugs were identified through a systematic Post-Mortem Analysis and corrected. The current codebase is mathematically verified and produces correct, pruned decision trees.

---

## 📊 Key Findings

| Feature | Information Gain |
|---------|---------------:|
| Teaching_Score | 0.7027 |
| Position | 0.0286 |
| Department | 0.0072 |
| Years_at_HUJI | 0.0056 |
| Office_Type | 0.0000 |

**Conclusion:** Teaching quality is the dominant predictor of professor popularity — a high score guarantees "Beloved" status regardless of other factors.
