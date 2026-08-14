"""Screen 2: recommendations view, with side-by-side comparison across all
5 approaches."""

import streamlit as st

from ui.data_access import get_recommendations, load_model_registry
from ui.styles import MODEL_COLORS, MODEL_LABELS


def _render_movie_card(item: dict, accent: str, rank: int) -> str:
    genre_tags = "".join(f'<span class="mc-genre-tag">{g}</span>' for g in item["genres"].split("|") if g)
    score_line = f"score {item['score']:.3f}" if item["score"] is not None else f"rank #{rank}"
    return f"""
    <div class="mc-card" style="border-left: 3px solid {accent};">
        <div style="font-weight:600;">{item['title']}</div>
        <div style="margin-top:0.3rem;">{genre_tags}</div>
        <div class="mc-score" style="margin-top:0.4rem;">{score_line}</div>
    </div>
    """


def render():
    st.markdown('<div class="mc-eyebrow">Screen 02</div>', unsafe_allow_html=True)
    st.markdown("## Recommendations")

    user_id = st.session_state.get("selected_user_id")
    if user_id is None:
        st.warning("No viewer selected yet. Go to the Select Viewer screen first.")
        return

    label = st.session_state.get("selected_label", f"User {user_id}")
    st.write(f"Showing recommendations for **{label}**.")
    st.markdown('<div class="mc-sprocket"></div>', unsafe_allow_html=True)

    registry = load_model_registry()
    available_models = [m for m in MODEL_LABELS if m in registry]

    if not available_models:
        st.warning("No trained models found in data/processed/models/. Run the Phase 1-3 training scripts first.")
        return

    col_a, col_b = st.columns([3, 1])
    with col_a:
        top_n = st.slider("Number of recommendations", min_value=5, max_value=20, value=10)
    with col_b:
        compare_all = st.toggle("Compare all 5 approaches", value=len(available_models) > 1)

    st.markdown('<div class="mc-sprocket"></div>', unsafe_allow_html=True)

    if compare_all:
        cols = st.columns(len(available_models))
        for col, model_name in zip(cols, available_models):
            accent = MODEL_COLORS[model_name]
            with col:
                st.markdown(
                    f'<div class="mc-model-header" style="color:{accent}; border-color:{accent};">'
                    f'{MODEL_LABELS[model_name]}</div>',
                    unsafe_allow_html=True,
                )
                recs = get_recommendations(model_name, user_id, k=top_n)
                if not recs:
                    st.caption("No recommendations available for this user.")
                for rank, item in enumerate(recs, start=1):
                    st.markdown(_render_movie_card(item, accent, rank), unsafe_allow_html=True)
    else:
        model_name = st.selectbox(
            "Approach", options=available_models, format_func=lambda m: MODEL_LABELS[m]
        )
        accent = MODEL_COLORS[model_name]
        recs = get_recommendations(model_name, user_id, k=top_n)
        if not recs:
            st.caption("No recommendations available for this user.")
        for rank, item in enumerate(recs, start=1):
            st.markdown(_render_movie_card(item, accent, rank), unsafe_allow_html=True)
