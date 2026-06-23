# The "Last Mile" Logistics Auditor — Veridi Logistics

> Delivery-performance audit of the Olist Brazilian e-commerce dataset, answering the CEO's
> question: **are we failing specific regions, or is this a nationwide problem?**

## A. Executive Summary

Veridi is **not** systematically late — **91.9%** of the 96,470 delivered orders arrive **on or
before** the promised date — so this is **not a nationwide problem**. The pain is a concentrated
**8.1% tail** of late orders that clusters in **specific remote regions**: the North/North-East
runs a **13.7%** late rate versus **7.9%** in the core states, led by **Alagoas (23.9%)**,
**Maranhão (19.7%)**, and **Piauí (16.0%)**. Lateness has a direct, measurable effect on
sentiment — average review score collapses from **4.29/5** for on-time orders to **3.46** for
late and **1.78** for super-late ones (correlation **−0.276** between days-late and score).
Our pipeline decomposition pinpoints the cause: late orders spend **25.2 days in carrier transit
vs. 7.4 days** for on-time orders, while seller handling barely differs — so the bottleneck is
the **carrier last mile to remote states**, not the sellers. **Recommendation:** stop padding
national delivery estimates and invest in regional carrier capacity/hubs for the North/North-East,
where over-promising is doing the most reputational damage.

## B. Project Links

| Deliverable                         | Link                                                                                  |
| ----------------------------------- | ------------------------------------------------------------------------------------- |
| Notebook (Google Colab)             | https://colab.research.google.com/drive/1exJGsLmxyIze0sokeHgnQr78WAyPEZ0q?usp=sharing |
| Dashboard (Streamlit Cloud)         | https://amalitech-deg-project-based-challenges-uh2ab99qkhbakqtiy5nypk.streamlit.app/  |
| Presentation (slides PDF/PPT)       | <SLIDES_LINK>                                                                         |
| Video walkthrough (optional, 2 min) | <YOUTUBE_LINK>                                                                        |

## C. Technical Explanation

**Data cleaning.** I deduplicated reviews to **one row per order** (keeping the latest review
answer) and collapsed the multi-item `order_items` table to **one primary item per order**
_before_ joining — this prevents the 1-to-many row inflation the brief warns about (an
`assert len(master) == len(orders)` guards it). Dates are parsed with `errors="coerce"`, and
orders that never reached the customer (`canceled`/`unavailable` or a null delivery date) are
**flagged via `is_delivered` and excluded** from all delay/sentiment metrics. `Days_Difference`
follows the brief's convention (`estimated − actual`), and I added an intuitive `days_late`
(0 if on time) for charting.

**Candidate's Choice — Delivery-pipeline decomposition.** I split total delivery time into
**handling time** (purchase → carrier; a _seller_ problem) and **transit time** (carrier →
customer; a _carrier_ problem). This matters because the fix is completely different depending
on which leg is slow: the analysis shows late/remote orders lose their extra days in **transit**,
so Veridi should invest in carrier capacity and regional hubs rather than chasing seller SLAs.
That turns "we're late" into a targeted, costed action — the difference between a chart and a
decision.

---

## How this repo is organised

```
.
├── README.md                       <- you are here (submission writeup)
├── requirements.txt                <- deps for the dashboard + notebook
├── streamlit_app.py                <- the public dashboard (reads the cleaned parquet)
├── notebooks/
│   ├── logistics_auditor.ipynb     <- the full analysis (Stories 1-4 + bonus + candidate's choice)
│   └── logistics_auditor.html      <- exported render with charts (brief requires HTML/PDF export)
└── data/
    ├── raw/                        <- raw Olist CSVs go here (git-ignored, never committed)
    └── processed/
        └── orders_clean.parquet    <- small cleaned artifact the dashboard reads (committed)
```

## What each User Story maps to

| Story                     | Where it lives                                                           |
| ------------------------- | ------------------------------------------------------------------------ |
| 1 — Schema Builder        | Notebook §"Story 1"; row-inflation `assert`                              |
| 2 — Delay Calculator      | Notebook §"Story 2"; `days_difference`, On Time / Late / Super Late      |
| 3 — Geographic Heatmap    | Notebook §"Story 3"; dashboard **Geography** tab                         |
| 4 — Sentiment Correlation | Notebook §"Story 4"; dashboard **Sentiment** tab                         |
| Bonus - Translation       | Notebook "Bonus" section; English categories in dashboard Categories tab |
| Candidate's Choice        | Notebook "Candidate's Choice" section; dashboard Pipeline tab            |

## Reproduce it

```bash
pip install -r requirements.txt
# 1) Download the Olist dataset from Kaggle into data/raw/
# 2) Run notebooks/logistics_auditor.ipynb  -> writes data/processed/orders_clean.parquet
# 3) Launch the dashboard:
streamlit run streamlit_app.py
```

Data source: [Olist Brazilian E-Commerce Dataset (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

---

## Pre-Submission Checklist (from the brief)

- [ ] GitHub repo is **public** (verify in an Incognito window)
- [ ] `.ipynb` notebook uploaded
- [ ] **HTML or PDF export** of the notebook uploaded
- [ ] Raw dataset **NOT** committed (`.gitignore` handles this)
- [ ] Code uses **relative paths**
- [ ] Dashboard link is **public** (no login)
- [ ] Presentation link is **public**
- [ ] This README updated with Executive Summary + technical notes
- [ ] User Stories 1–4 complete
- [ ] Candidate's Choice complete + explained here
- [ ] Submission form filled: https://forms.cloud.microsoft/e/CeQN2mCyUr
