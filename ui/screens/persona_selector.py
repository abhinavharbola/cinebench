"""Screen 1: user/persona selector."""

import streamlit as st

from ui.data_access import load_all_user_ids, load_personas


def render():
    st.markdown('<div class="mc-eyebrow">Screen 01</div>', unsafe_allow_html=True)
    st.markdown("## Choose a viewer")
    st.write("Pick a curated persona, or browse by a real MovieLens user ID.")
    st.markdown('<div class="mc-sprocket"></div>', unsafe_allow_html=True)

    personas = load_personas()

    if personas:
        st.markdown('<div class="mc-eyebrow" style="margin-bottom:0.6rem;">Curated personas</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(personas), 4))
        for i, persona in enumerate(personas):
            with cols[i % len(cols)]:
                st.markdown(
                    f"""
                    <div class="mc-persona-card">
                        <div class="mc-persona-name">{persona['name']}</div>
                        <div class="mc-persona-desc">{persona['description']}</div>
                        <div style="margin-top:0.6rem;">
                            {''.join(f'<span class="mc-genre-tag">{g}</span>' for g in persona.get('top_genres', []))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("View recommendations", key=f"persona_{i}", use_container_width=True):
                    st.session_state["selected_user_id"] = persona["user_id"]
                    st.session_state["selected_label"] = persona["name"]
    else:
        st.info("No curated personas cached yet. Run scripts/curate_personas.py, or browse by user ID below.")

    st.markdown('<div class="mc-sprocket"></div>', unsafe_allow_html=True)
    st.markdown('<div class="mc-eyebrow" style="margin-bottom:0.6rem;">Browse by user ID</div>', unsafe_allow_html=True)

    user_ids = load_all_user_ids()
    if user_ids:
        selected = st.selectbox("MovieLens user ID", options=user_ids, key="user_id_select")
        if st.button("View recommendations for this user"):
            st.session_state["selected_user_id"] = selected
            st.session_state["selected_label"] = f"User {selected}"
    else:
        st.warning("No processed training data found. Run src/data/ingest.py and scripts/run_phase1.py first.")

    if st.session_state.get("selected_user_id") is not None:
        st.success(f"Selected: {st.session_state.get('selected_label')}. Open the Recommendations screen from the sidebar.")
