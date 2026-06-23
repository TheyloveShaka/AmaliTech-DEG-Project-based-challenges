"""
Helix CPG Partners - The "Sugar Trap" Market Gap Analysis
=========================================================
Public dashboard for the Open Food Facts healthy-snacking opportunity.

Reads the small cleaned artifact produced by the notebook
(data/processed/products_clean.parquet), not the 9 GB raw dataset.

Run locally:  streamlit run streamlit_app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sugar Trap Market Gap", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "processed" / "products_clean.parquet"
PROTEIN_HI = 10   # g/100g "high protein"
SUGAR_LO = 5      # g/100g "low sugar"


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(
            f"Cleaned data not found at `{DATA_PATH}`.\n\n"
            "Run the notebook first to generate **products_clean.parquet**, then place it in "
            "`data/processed/` and commit it."
        )
        st.stop()
    return pd.read_parquet(DATA_PATH)


df = load_data()

# ── Sidebar filters ──
st.sidebar.title("Filters")
cats = sorted(df["primary_category"].dropna().unique())
sel_cats = st.sidebar.multiselect("Category", cats, default=cats)
max_sugar = st.sidebar.slider("Max sugar (g/100g)", 0, 100, 100)
min_protein = st.sidebar.slider("Min protein (g/100g)", 0, 50, 0)

f = df[df["primary_category"].isin(sel_cats)
       & (df["sugars_100g"] <= max_sugar)
       & (df["proteins_100g"] >= min_protein)]
if f.empty:
    st.warning("No products match the current filters.")
    st.stop()

# ── Header + KPIs ──
st.title("The Sugar Trap: Where is the Blue Ocean in the Snack Aisle?")
st.markdown(
    "Finding the **empty quadrant** - categories where supply skews high-sugar / low-protein, "
    "leaving room for a high-protein, low-sugar healthy-snacking line."
)

healthy = (f["healthy_quadrant"]).mean() * 100
k1, k2, k3, k4 = st.columns(4)
k1.metric("Products", f"{len(f):,}")
k2.metric("In healthy quadrant", f"{healthy:.1f}%")
k3.metric("Median sugar", f"{f['sugars_100g'].median():.1f} g")
k4.metric("Median protein", f"{f['proteins_100g'].median():.1f} g")

st.divider()

tab_matrix, tab_opp, tab_trap = st.tabs(
    ["Nutrient Matrix", "Opportunity by Category", "Sugar Trap Index"]
)

# ── Story 3: nutrient matrix scatter ──
with tab_matrix:
    st.subheader("Sugar vs protein - the empty quadrant is top-left")
    sample = f.sample(min(12000, len(f)), random_state=1)
    fig = px.scatter(
        sample, x="sugars_100g", y="proteins_100g", color="primary_category",
        opacity=0.5, labels={"sugars_100g": "Sugar (g/100g)", "proteins_100g": "Protein (g/100g)"},
        hover_data=["product_name"],
    )
    fig.add_hline(y=PROTEIN_HI, line_dash="dash", line_color="grey")
    fig.add_vline(x=SUGAR_LO, line_dash="dash", line_color="grey")
    fig.add_annotation(x=SUGAR_LO / 2, y=45, text="Empty quadrant<br>(high protein, low sugar)",
                       showarrow=False, font=dict(color="#C44E52", size=12))
    fig.update_xaxes(range=[0, 80]); fig.update_yaxes(range=[0, 50])
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"Only **{healthy:.1f}%** of the filtered products sit in the high-protein / "
            f"low-sugar quadrant (>= {PROTEIN_HI}g protein and <= {SUGAR_LO}g sugar).")

# ── Story 4: opportunity by category ──
with tab_opp:
    st.subheader("Which categories are most underserved?")
    cat = (f.groupby("primary_category")
           .agg(products=("code", "count"),
                median_sugar=("sugars_100g", "median"),
                median_protein=("proteins_100g", "median"),
                healthy_share=("healthy_quadrant", "mean"))
           .reset_index())
    cat["healthy_share"] = (cat["healthy_share"] * 100).round(1)
    cat["opportunity_score"] = (cat["products"] / cat["products"].max() * 50
                                + cat["median_sugar"] - cat["healthy_share"]).round(1)
    cat = cat.sort_values("opportunity_score", ascending=False)
    fig = px.bar(cat, x="opportunity_score", y="primary_category", orientation="h",
                 color="opportunity_score", color_continuous_scale="Reds",
                 labels={"opportunity_score": "Opportunity score", "primary_category": ""},
                 title="Higher score = larger, sugarier, fewer healthy options")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
    st.plotly_chart(fig, use_container_width=True)
    top = cat.iloc[0]
    st.success(
        f"**Recommendation:** the biggest opportunity is **{top['primary_category']}** - "
        f"{int(top['products']):,} products, median sugar {top['median_sugar']:.1f}g, but only "
        f"{top['healthy_share']:.1f}% are high-protein / low-sugar."
    )
    st.dataframe(cat, use_container_width=True, hide_index=True)

# ── Candidate's choice: sugar trap index ──
with tab_trap:
    st.subheader("Sugar Trap Index - how sugar-dominant is each category's supply?")
    st.caption("median sugar / (median protein + 1). Higher = shelves full of sugary, "
               "low-protein products, the clearest signal of an unmet healthy-snacking need.")
    cat2 = (f.groupby("primary_category")
            .agg(median_sugar=("sugars_100g", "median"),
                 median_protein=("proteins_100g", "median")).reset_index())
    cat2["sugar_trap"] = (cat2["median_sugar"] / (cat2["median_protein"] + 1)).round(2)
    cat2 = cat2.sort_values("sugar_trap", ascending=False)
    fig = px.bar(cat2, x="sugar_trap", y="primary_category", orientation="h",
                 color="sugar_trap", color_continuous_scale="Oranges",
                 labels={"sugar_trap": "Sugar Trap index", "primary_category": ""})
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Data: Open Food Facts. Built for the Helix CPG market-gap analysis.")
