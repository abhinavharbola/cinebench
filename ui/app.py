"""
Main Streamlit entrypoint. Three screens per project spec: viewer
selection, recommendations comparison, model performance dashboard. All
three read only cached local artifacts -- no live external calls, no
recomputation, no auth, no write-back.

Lives in a top-level ui/ package (not under src/), so the run command is
`streamlit run ui/app.py` from the repo root.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from ui.screens import dashboard, persona_selector, recommendations
from ui.styles import inject_custom_css

st.set_page_config(page_title="MovieLens Recommender", layout="wide")
st.markdown(inject_custom_css(), unsafe_allow_html=True)

if "selected_user_id" not in st.session_state:
    st.session_state["selected_user_id"] = None

with st.sidebar:
    st.markdown('<div class="mc-wordmark">Reel<span>Bench</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mc-eyebrow" style="padding-bottom:1rem;">Two-stage recommender benchmark</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="mc-sprocket"></div>', unsafe_allow_html=True)

    screen = st.radio(
        "Navigate",
        options=["Select Viewer", "Recommendations", "Model Performance"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="mc-sprocket"></div>', unsafe_allow_html=True)
    if st.session_state["selected_user_id"] is not None:
        st.caption(f"Current viewer: {st.session_state.get('selected_label')}")

if screen == "Select Viewer":
    persona_selector.render()
elif screen == "Recommendations":
    recommendations.render()
else:
    dashboard.render()
