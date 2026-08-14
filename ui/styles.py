"""
Design tokens and custom CSS for the Streamlit UI. Cinema/film-reel
aesthetic grounded in the subject (MovieLens): warm charcoal, marquee gold,
velvet red, a sprocket-rail divider as the signature element, and a fixed
per-model color identity used consistently across every screen.
"""

COLORS = {
    "bg_primary": "#101014",
    "bg_surface": "#17181D",
    "bg_surface_raised": "#1E2027",
    "accent_marquee": "#E8A33D",
    "accent_velvet": "#8C3B3B",
    "text_primary": "#F2EFE6",
    "text_muted": "#8B8D98",
    "border_subtle": "#26282F",
    "positive": "#6FCF97",
}

# Fixed per-model identity, used consistently across all three screens so a
# user learns to recognize "gold = two-tower" the same way they'd recognize
# a labeled film reel.
MODEL_COLORS = {
    "popularity": "#8B8D98",
    "item_item_cf": "#5B8DBF",
    "als": "#6FA37A",
    "two_tower": "#E8A33D",
    "sasrec": "#B5679A",
}

MODEL_LABELS = {
    "popularity": "Popularity",
    "item_item_cf": "Item-Item CF",
    "als": "ALS / BPR",
    "two_tower": "Two-Tower",
    "sasrec": "SASRec",
}


def inject_custom_css() -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
}}

section[data-testid="stSidebar"] {{
    background-color: {COLORS['bg_surface']};
    border-right: 1px solid {COLORS['border_subtle']};
}}

h1, h2, h3 {{
    font-family: 'Fraunces', serif;
    font-weight: 600;
    color: {COLORS['text_primary']};
    letter-spacing: -0.01em;
}}

.mc-wordmark {{
    font-family: 'Fraunces', serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: {COLORS['text_primary']};
    padding: 1.2rem 0 0.4rem 0;
}}

.mc-wordmark span {{
    color: {COLORS['accent_marquee']};
}}

.mc-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {COLORS['text_muted']};
}}

/* Signature element: sprocket-rail divider, a row of film-perforation dots */
.mc-sprocket {{
    height: 14px;
    margin: 1.4rem 0;
    background-image: radial-gradient({COLORS['border_subtle']} 35%, transparent 36%);
    background-size: 18px 14px;
    background-repeat: repeat-x;
    opacity: 0.9;
}}

.mc-card {{
    background-color: {COLORS['bg_surface']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: 6px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.9rem;
}}

.mc-card:hover {{
    border-color: {COLORS['accent_marquee']}55;
}}

.mc-score {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: {COLORS['accent_marquee']};
}}

.mc-genre-tag {{
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: {COLORS['text_muted']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: 4px;
    padding: 0.1rem 0.45rem;
    margin: 0.15rem 0.25rem 0 0;
}}

.mc-model-header {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding-bottom: 0.5rem;
    margin-bottom: 0.6rem;
    border-bottom: 2px solid;
}}

.mc-persona-card {{
    background-color: {COLORS['bg_surface']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: 6px;
    padding: 1rem 1.1rem;
    height: 100%;
}}

.mc-persona-name {{
    font-family: 'Fraunces', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

.mc-persona-desc {{
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: {COLORS['text_muted']};
    margin-top: 0.3rem;
}}

.stButton > button {{
    background-color: {COLORS['bg_surface_raised']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}}

.stButton > button:hover {{
    border-color: {COLORS['accent_marquee']};
    color: {COLORS['accent_marquee']};
}}

div[data-testid="stMetricValue"] {{
    font-family: 'IBM Plex Mono', monospace;
    color: {COLORS['accent_marquee']};
}}

hr {{
    border-color: {COLORS['border_subtle']};
}}

/* Streamlit's default header bar is bright and clashes with the dark
theme -- this is a standalone demo app, not embedded, so blend it in and
hide the toolbar controls. */
header[data-testid="stHeader"] {{
    background-color: {COLORS['bg_primary']} !important;
}}

[data-testid="stToolbar"] {{
    visibility: hidden;
}}

/* Select/multiselect internals vary between Streamlit versions (BaseWeb vs
react-aria), so target the stable data-testid wrapper rather than
version-specific internal classes. */
div[data-testid="stSelectbox"] input,
div[data-testid="stMultiSelect"] input,
div[data-testid="stSelectbox"] [role="group"],
div[data-testid="stMultiSelect"] [role="group"],
div[data-testid="stSelectbox"] button,
div[data-testid="stMultiSelect"] button {{
    background-color: {COLORS['bg_surface_raised']} !important;
    border-color: {COLORS['border_subtle']} !important;
    color: {COLORS['text_primary']} !important;
}}

div[data-baseweb="popover"],
ul[role="listbox"] {{
    background-color: {COLORS['bg_surface_raised']} !important;
}}

li[role="option"] {{
    color: {COLORS['text_primary']} !important;
}}

span[data-baseweb="tag"] {{
    background-color: {COLORS['accent_velvet']} !important;
}}

/* Slider and toggle default to Streamlit's red accent -- recolor to the
marquee gold so every interactive control matches the token system. */
div[data-testid="stSlider"] div[role="slider"] {{
    background-color: {COLORS['accent_marquee']} !important;
    border-color: {COLORS['accent_marquee']} !important;
}}

div[data-testid="stSlider"] > div > div > div > div {{
    background-color: {COLORS['accent_marquee']} !important;
}}

/* st.toggle renders as an input[role=switch] with the visible track as a
sibling div -- target via the label's data-selected state for the "on" color. */
label:has(input[role="switch"]:checked) > div:nth-of-type(1) {{
    background-color: {COLORS['accent_marquee']} !important;
}}
</style>
"""
