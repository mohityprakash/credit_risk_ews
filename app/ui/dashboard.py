import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = st.sidebar.text_input("API URL", "http://localhost:8000")

st.title("Credit Risk Early Warning System")
st.caption("Explainable credit-risk news intelligence dashboard")

try:
    articles_resp = requests.get(f"{API_URL}/articles", timeout=10)
    articles_resp.raise_for_status()
    articles = articles_resp.json()
except Exception as exc:
    st.error(f"Unable to load articles: {exc}")
    st.stop()

articles_df = pd.DataFrame(articles)
if articles_df.empty:
    st.info("No articles yet. Run /ingest and /analyze/pending first.")
    st.stop()

articles_df["published_at"] = pd.to_datetime(articles_df["published_at"])

sources = st.multiselect("Filter source", sorted(articles_df["source"].dropna().unique().tolist()))
relevance_only = st.checkbox("Credit relevant only", value=True)

filtered = articles_df.copy()
if sources:
    filtered = filtered[filtered["source"].isin(sources)]
if relevance_only:
    filtered = filtered[filtered["is_credit_relevant"] == True]

st.subheader("Live Article Feed")
st.dataframe(filtered[["id", "published_at", "source", "title", "relevance_score", "url"]], use_container_width=True)

entities_resp = requests.get(f"{API_URL}/entities", timeout=10)
if entities_resp.ok:
    entities_df = pd.DataFrame(entities_resp.json())
    if not entities_df.empty:
        st.subheader("Entity Risk Momentum Leaderboard")
        st.dataframe(
            entities_df[
                [
                    "entity_name",
                    "risk_momentum_score",
                    "article_count_1d",
                    "article_count_7d",
                    "negative_share",
                    "average_risk_score",
                ]
            ],
            use_container_width=True,
        )

        fig = px.bar(
            entities_df.head(15),
            x="entity_name",
            y="risk_momentum_score",
            title="Top 15 Entities by Risk Momentum",
        )
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Credit-Relevant Flow Over Time")
series_df = filtered.set_index("published_at").resample("D").size().reset_index(name="article_count")
line_fig = px.line(series_df, x="published_at", y="article_count", markers=True)
st.plotly_chart(line_fig, use_container_width=True)

selected_id = st.number_input("Article ID for detail", min_value=1, step=1)
if st.button("Load Article Detail"):
    detail = requests.get(f"{API_URL}/articles/{int(selected_id)}", timeout=10)
    if detail.ok:
        payload = detail.json()
        st.write(payload["article"])
        st.write(payload.get("analysis") or "No analysis yet")
    else:
        st.warning("Article not found")
