"""Screen 3: model performance dashboard. Read-only, reads directly from
results/comparison_table.csv -- no recomputation in the UI."""

import plotly.graph_objects as go
import streamlit as st

from ui.data_access import load_comparison_table
from ui.styles import COLORS, MODEL_COLORS, MODEL_LABELS


def _metric_bar_chart(table, metric: str):
    models = table["model"].to_list()
    values = table[metric].to_list()
    colors = [MODEL_COLORS.get(m, COLORS["text_muted"]) for m in models]
    labels = [MODEL_LABELS.get(m, m) for m in models]

    fig = go.Figure(
        data=[go.Bar(x=labels, y=values, marker_color=colors, text=[f"{v:.3f}" for v in values], textposition="outside")]
    )
    fig.update_layout(
        title=metric,
        plot_bgcolor=COLORS["bg_surface"],
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text_primary"]),
        title_font=dict(family="Fraunces, serif", size=18),
        yaxis=dict(gridcolor=COLORS["border_subtle"], zerolinecolor=COLORS["border_subtle"]),
        xaxis=dict(gridcolor=COLORS["border_subtle"]),
        margin=dict(t=50, b=30, l=30, r=20),
        height=340,
    )
    return fig


def render():
    st.markdown('<div class="mc-eyebrow">Screen 03</div>', unsafe_allow_html=True)
    st.markdown("## Model performance")
    st.write("Every approach evaluated through the identical harness, on identical held-out data.")
    st.markdown('<div class="mc-sprocket"></div>', unsafe_allow_html=True)

    table = load_comparison_table()
    if table is None:
        st.warning("No results found. Run scripts/run_phase1.py (and later phases) to populate results/comparison_table.csv.")
        return

    metric_cols = [c for c in table.columns if c != "model"]
    default_metrics = [c for c in ("recall@10", "ndcg@10") if c in metric_cols] or metric_cols[:2]

    selected_metrics = st.multiselect("Metrics to chart", options=metric_cols, default=default_metrics)

    if selected_metrics:
        chart_cols = st.columns(2)
        for i, metric in enumerate(selected_metrics):
            with chart_cols[i % 2]:
                st.plotly_chart(_metric_bar_chart(table, metric), use_container_width=True)

    st.markdown('<div class="mc-sprocket"></div>', unsafe_allow_html=True)
    st.markdown('<div class="mc-eyebrow" style="margin-bottom:0.6rem;">Full comparison table</div>', unsafe_allow_html=True)

    import polars as pl
    display_table = table.with_columns(
        pl.col("model").map_elements(lambda m: MODEL_LABELS.get(m, m), return_dtype=pl.Utf8)
    ) if "model" in table.columns else table
    st.dataframe(display_table.to_pandas(), use_container_width=True, hide_index=True)
