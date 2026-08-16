"""Screen 1: user/persona selector."""

import streamlit as st

from ui.components import genre_icon, render_empty_state, render_page_header
from ui.data_access import load_all_user_ids, load_personas


def render():
    render_page_header(
        "Screen 01",
        "Choose a viewer",
        "Pick a curated persona below, or browse recommendations for any real MovieLens user ID.",
    )

    personas = load_personas()

    if personas:
        st.markdown('<div class="mc-eyebrow" style="margin-bottom:0.7rem;">Curated personas</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(personas), 4))
        for i, persona in enumerate(personas):
            top_genres = persona.get("top_genres", [])
            icon = genre_icon(top_genres[0]) if top_genres else "\U0001F3AC"
            with cols[i % len(cols)]:
                st.markdown(
                    f"""
                    <div class="mc-persona-card">
                        <div class="mc-persona-icon">{icon}</div>
                        <div class="mc-persona-name">{persona['name']}</div>
                        <div class="mc-persona-desc">{persona['description']}</div>
                        <div class="mc-persona-tags">
                            {''.join(f'<span class="mc-genre-tag">{g}</span>' for g in top_genres)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("View recommendations", key=f"persona_{i}", use_container_width=True):
                    st.session_state["selected_user_id"] = persona["user_id"]
                    st.session_state["selected_label"] = persona["name"]
    else:
        render_empty_state(
            "No curated personas cached yet.",
            action_hint="Run: python scripts/curate_personas.py &mdash; or browse by user ID below.",
        )

    st.markdown('<div class="mc-sprocket"></div>', unsafe_allow_html=True)
    st.markdown('<div class="mc-eyebrow" style="margin-bottom:0.7rem;">Browse by user ID</div>', unsafe_allow_html=True)

    user_ids = load_all_user_ids()
    if user_ids:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            selected = st.selectbox(
                "MovieLens user ID", options=user_ids, key="user_id_select",
                help=f"{len(user_ids):,} users available in the cached training split.",
            )
        with col_b:
            st.write("")
            st.write("")
            if st.button("View recommendations for this user", use_container_width=True):
                st.session_state["selected_user_id"] = selected
                st.session_state["selected_label"] = f"User {selected}"
    else:
        render_empty_state(
            "No processed training data found.",
            action_hint="Run: python -m src.data.ingest &nbsp;then&nbsp; python scripts/run_phase1.py",
        )

    if st.session_state.get("selected_user_id") is not None:
        st.success(f"Selected: {st.session_state.get('selected_label')}. Open the Recommendations screen from the sidebar.")