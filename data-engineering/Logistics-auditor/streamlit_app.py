"""
Veridi Logistics — "Last Mile" Delivery Performance Auditor
============================================================
Public dashboard for the Olist delivery audit.

It reads the small cleaned artifact produced by the notebook
(data/processed/orders_clean.parquet) — NOT the raw Olist dataset — so it
deploys to Streamlit Cloud with nothing heavy in the repo.

Run locally:   streamlit run streamlit_app.py
Deploy:        push to GitHub -> share.streamlit.io -> point at this file.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Veridi Logistics Auditor", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "processed" / "orders_clean.parquet"

# Brazil state -> region, used to highlight "remote" (North / North-East) states.
REMOTE_STATES = {"RR", "AP", "AM", "AC", "PA", "RO", "MA", "TO", "AL", "PB", "PI", "CE", "RN", "SE", "BA", "PE"}


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(
            f"Cleaned data not found at `{DATA_PATH}`.\n\n"
            "Run the notebook first to generate **orders_clean.parquet**, then place it in "
            "`data/processed/` and commit it. See GUIDE.md."
        )
        st.stop()
    df = pd.read_parquet(DATA_PATH)
    df["is_remote"] = df["customer_state"].isin(REMOTE_STATES)
    return df


df = load_data()
delivered = df[df["is_delivered"]].copy()

# ──────────────────────────────────────────────────────────────────────────
# Sidebar filters
# ──────────────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")
st.sidebar.caption("Filters apply to every chart below.")

all_states = sorted(delivered["customer_state"].dropna().unique())
sel_states = st.sidebar.multiselect("Customer state", all_states, default=all_states)

status_opts = ["On Time", "Late", "Super Late"]
sel_status = st.sidebar.multiselect("Delivery status", status_opts, default=status_opts)

top_cats = (delivered["product_category"].value_counts().head(20).index.tolist())
sel_cats = st.sidebar.multiselect(
    "Product category (top 20)", top_cats, default=[],
    help="Leave empty to include all categories.",
)

f = delivered[delivered["customer_state"].isin(sel_states)
              & delivered["delivery_status"].isin(sel_status)]
if sel_cats:
    f = f[f["product_category"].isin(sel_cats)]

if f.empty:
    st.warning("No orders match the current filters. Widen your selection.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────
# Header + KPI row
# ──────────────────────────────────────────────────────────────────────────
st.title("Veridi Logistics — Delivery Performance Auditor")
st.markdown(
    "Auditing whether we **over-promise and under-deliver** — and whether the pain is "
    "*nationwide* or concentrated in **specific regions**."
)

late_rate = f["is_late"].mean() * 100
avg_review = f["review_score"].mean()
avg_days_late = f.loc[f["is_late"], "days_late"].mean()
super_late_rate = (f["delivery_status"] == "Super Late").mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Delivered orders", f"{len(f):,}")
k2.metric("Late + Super-Late", f"{late_rate:.1f}%")
k3.metric("Super-Late (>5d)", f"{super_late_rate:.1f}%")
k4.metric("Avg review score", f"{avg_review:.2f} / 5")
k5.metric("Avg days late (when late)", f"{avg_days_late:.1f}")

st.divider()

# ──────────────────────────────────────────────────────────────────────────
# Tabs = the four user stories + candidate's choice
# ──────────────────────────────────────────────────────────────────────────
tab3, tab2, tab4, tab_pipe, tab_cat = st.tabs(
    ["Geography", "Delays", "Sentiment", "Pipeline", "Categories"]
)

# --- Story 3: geography ---
with tab3:
    st.subheader("Which states have the worst late-delivery rates?")
    state_perf = (f.groupby("customer_state")
                  .agg(orders=("order_id", "count"),
                       pct_late=("is_late", "mean"),
                       avg_review=("review_score", "mean"),
                       is_remote=("is_remote", "first"))
                  .reset_index())
    state_perf = state_perf[state_perf["orders"] >= 20]
    state_perf["pct_late"] = (state_perf["pct_late"] * 100).round(1)
    state_perf = state_perf.sort_values("pct_late", ascending=False)

    fig = px.bar(
        state_perf.head(20), x="pct_late", y="customer_state", orientation="h",
        color="is_remote", color_discrete_map={True: "#C44E52", False: "#4C72B0"},
        labels={"pct_late": "% late", "customer_state": "State",
                "is_remote": "Remote (N/NE)"},
        title="Late-delivery rate by state (red = remote North/North-East)",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=600)
    st.plotly_chart(fig, use_container_width=True)

    core = f[~f["is_remote"]]["is_late"].mean() * 100
    remote = f[f["is_remote"]]["is_late"].mean() * 100
    c1, c2 = st.columns(2)
    c1.metric("Core states late rate", f"{core:.1f}%")
    c2.metric("Remote states late rate", f"{remote:.1f}%",
              delta=f"{remote - core:+.1f} pts vs core", delta_color="inverse")

# --- Story 2: delays ---
with tab2:
    st.subheader("How early or late are we vs. the promised date?")
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = px.histogram(
            f, x=f["days_difference"].clip(-30, 30), nbins=60,
            labels={"x": "Days_Difference (positive = early, negative = late)"},
            title="Distribution of delivery vs. promise",
        )
        fig.add_vline(x=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        counts = f["delivery_status"].value_counts().reindex(status_opts).fillna(0)
        fig = px.pie(values=counts.values, names=counts.index,
                     color=counts.index,
                     color_discrete_map={"On Time": "#55A868", "Late": "#DD8452",
                                         "Super Late": "#C44E52"},
                     title="Status mix", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)

# --- Story 4: sentiment ---
with tab4:
    st.subheader("Do late deliveries actually cause bad reviews?")
    sent = (f.dropna(subset=["review_score"])
            .groupby("delivery_status")["review_score"].mean()
            .reindex(status_opts))
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(x=sent.index, y=sent.values, color=sent.index,
                     color_discrete_map={"On Time": "#55A868", "Late": "#DD8452",
                                         "Super Late": "#C44E52"},
                     labels={"x": "", "y": "Avg review score"},
                     title="Average review score by delivery outcome")
        fig.update_layout(yaxis_range=[0, 5], showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        tmp = f.dropna(subset=["review_score"]).copy()
        tmp["bucket"] = pd.cut(tmp["days_late"], [-1, 0, 2, 5, 10, 20, 1000],
                               labels=["On time", "1-2", "3-5", "6-10", "11-20", "20+"])
        line = tmp.groupby("bucket")["review_score"].mean().reset_index()
        fig = px.line(line, x="bucket", y="review_score", markers=True,
                      labels={"bucket": "Days late", "review_score": "Avg review"},
                      title="More days late → worse reviews")
        fig.update_layout(yaxis_range=[1, 5])
        st.plotly_chart(fig, use_container_width=True)
    corr = f["days_late"].corr(f["review_score"])
    st.info(f"**Correlation (days late ↔ review score): {corr:.3f}** — "
            "negative means more lateness drives lower scores.")

# --- Candidate's choice: pipeline decomposition ---
with tab_pipe:
    st.subheader("Where does the delay come from — the seller or the carrier?")
    st.caption(
        "Total delivery time split into **handling** (purchase → carrier; a seller problem) "
        "and **transit** (carrier → customer; a logistics problem). This tells Veridi *which "
        "lever to pull* to fix lateness."
    )
    pipe = (f.dropna(subset=["handling_time", "transit_time"])
            .groupby("is_late")[["handling_time", "transit_time"]].mean()
            .rename(index={False: "On-time orders", True: "Late orders"})
            .reset_index().melt(id_vars="is_late", var_name="stage", value_name="days"))
    pipe["group"] = pipe["is_late"]
    fig = px.bar(pipe, x="days", y="group", color="stage", orientation="h",
                 color_discrete_map={"handling_time": "#4C72B0", "transit_time": "#C44E52"},
                 labels={"days": "Average days", "group": ""},
                 title="Handling vs. transit time")
    st.plotly_chart(fig, use_container_width=True)
    st.info("Typically the extra days in late/remote orders pile up in **transit**, not "
            "handling — point the fix at carrier capacity & regional hubs, not seller SLAs.")

# --- Bonus: categories ---
with tab_cat:
    st.subheader("Are some product categories harder to ship on time?")
    cat = (f.groupby("product_category")
           .agg(orders=("order_id", "count"), pct_late=("is_late", "mean"))
           .reset_index())
    cat = cat[cat["orders"] >= 100]
    cat["pct_late"] = (cat["pct_late"] * 100).round(1)
    cat = cat.sort_values("pct_late", ascending=False).head(15)
    fig = px.bar(cat, x="pct_late", y="product_category", orientation="h",
                 labels={"pct_late": "% late", "product_category": "Category (English)"},
                 title="Late rate by product category (worst 15, English names)")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=550)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Data: Olist Brazilian E-Commerce (Kaggle). Built for the Veridi Logistics audit challenge.")
