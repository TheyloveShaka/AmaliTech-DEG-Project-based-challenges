# The "Sugar Trap" Market Gap Analysis - Helix CPG Partners

> Finding the "Blue Ocean" in the snack aisle: categories where supply skews high-sugar /
> low-protein, leaving room for a healthy-snacking line. Built on the Open Food Facts dataset.

<!-- Fill the placeholders <LIKE_THIS> from the notebook's final "Key findings" cell. -->

## A. Executive Summary

Across 218,092 snack products, only **17.3%** sit in the high-protein / low-sugar "empty
quadrant," and the shortfall is heavily concentrated in a few sugar-dominant categories. The
clearest Blue Ocean is **Chocolate & Confectionery**: 26,908 products at a median of **38.0g
sugar** per 100g, yet only **2.1%** meet the high-protein / low-sugar bar. Our Sugar Trap index
(median sugar / median protein) confirms it as the most sugar-dominant shelf at **5.21**, far
ahead of every other category. By contrast, Nuts & Seeds and Dairy & Yogurt already serve that
need (39% and 36% of their products are in the healthy quadrant). **Recommendation:** launch the
healthy-snacking line into **Chocolate & Confectionery** with products at >= 10g protein and
< 5g sugar per 100g.

## B. Project Links

| Deliverable | Link |
|-------------|------|
| Notebook (Google Colab) | https://colab.research.google.com/drive/1IDU1QVRzoetl92BTTo7HsBc1djOZBRqX?usp=sharing |
| Dashboard (Streamlit Cloud) | https://amalitech-deg-project-based-challenges-d9dtxpappv26xqlt8rjgu8i.streamlit.app/ |
| Presentation (slides) | https://docs.google.com/presentation/d/1Soi3fAfZvo3twumDnyopuaNazUAr82LDXIn9h_D4T7k/edit?usp=sharing |

## C. Technical Explanation

**Data cleaning.** The Open Food Facts export is ~9 GB, so the notebook streams it in 100k-row
chunks, keeping only the nutrition columns and stopping once it has a clean ~500k-row subset
(never loading the full file). Each chunk drops rows missing `product_name`, `sugars_100g`, or
`proteins_100g`, and discards biologically impossible values (a per-100g nutrient cannot exceed
100 g; energy is capped at a sane 900 kcal/100g). Messy `categories_tags` strings are mapped to
seven high-level buckets by keyword priority, and the catch-all "Other" bucket is dropped so the
analysis stays snack-relevant.

**Candidate's Choice - the Sugar Trap index.** Defined per category as
`median_sugar / (median_protein + 1)`. A high value means the shelf is full of sugary,
low-protein products - a sharper signal of unmet healthy-snacking demand than raw sugar alone,
because it accounts for what little protein the category already offers.

---

## How this repo is organised

```
.
├── README.md                       <- submission writeup
├── requirements.txt                <- deps for the dashboard + notebook
├── streamlit_app.py                <- the public dashboard (reads the cleaned parquet)
├── notebooks/
│   ├── market_gap.ipynb            <- full analysis (Stories 1-4 + bonus + candidate's choice)
│   └── market_gap.html             <- exported render with charts (brief requires HTML/PDF)
└── data/
    ├── raw/                        <- raw OFF data (git-ignored, never committed)
    └── processed/
        └── products_clean.parquet  <- small cleaned artifact the dashboard reads (committed)
```

## What each User Story maps to

| Story | Where it lives |
|-------|----------------|
| 1 - Ingestion & cleanup | Notebook "Ingest and clean"; chunked read + impossible-value filter |
| 2 - Category wrangler | Notebook "Category wrangler"; `categories_tags` -> 7 buckets |
| 3 - Nutrient matrix | Notebook "Nutrient matrix"; dashboard Nutrient Matrix tab |
| 4 - Recommendation | Notebook "Recommendation"; dashboard Opportunity tab |
| Bonus - Protein sources | Notebook "Hidden-gem protein sources" |
| Candidate's Choice | Notebook "Sugar Trap index"; dashboard Sugar Trap tab |

## Reproduce it

```bash
pip install -r requirements.txt
# Notebook streams the Open Food Facts export, writes data/processed/products_clean.parquet
streamlit run streamlit_app.py
```

Data source: [Open Food Facts](https://world.openfoodfacts.org/data).

---

## Pre-Submission Checklist

- [ ] GitHub repo is public (verify in Incognito)
- [ ] `.ipynb` notebook uploaded
- [ ] HTML or PDF export uploaded
- [ ] Raw dataset NOT committed (`.gitignore` handles it)
- [ ] Relative paths only
- [ ] Dashboard link public (no login)
- [ ] Presentation link public
- [ ] README updated with Executive Summary + technical notes
- [ ] User Stories 1-4 complete
- [ ] Candidate's Choice complete + explained
- [ ] Submission form filled
