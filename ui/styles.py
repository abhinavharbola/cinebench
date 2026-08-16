"""
Design tokens and custom CSS for the Streamlit UI. Cinema/film-reel
aesthetic grounded in the subject (MovieLens): warm paper white, deep
brass gold, burgundy, a sprocket-rail divider as the signature element,
and a fixed per-model color identity used consistently across every screen.

Light theme, not the more common cream+terracotta pairing: warm paper
background (not stark white), true white cards for elevation, and
deepened/saturated accent colors (brass instead of bright gold, forest
green instead of pastel) so everything stays legible against a light
background rather than washing out.

Token scale: colors, spacing, and radii are named and reused everywhere
below rather than hardcoded per rule, so the theme can be retuned in one
place -- this file -- without hunting through every screen's markdown.
"""

COLORS = {
    "bg_primary": "#F7F5F0",
    "bg_surface": "#FFFFFF",
    "bg_surface_raised": "#F1EDE3",
    "accent_marquee": "#9C5A1E",
    "accent_marquee_soft": "#C98A3E",
    "accent_velvet": "#6E2A2A",
    "accent_ink": "#22303F",
    "text_primary": "#1C1A16",
    "text_muted": "#69635A",
    "text_faint": "#95907F",
    "border_subtle": "#E4DECF",
    "border_strong": "#D6CDB8",
    "positive": "#2F7A4F",
    "warning": "#A66A1E",
}

RADIUS = {"sm": "6px", "md": "10px", "lg": "16px"}
SHADOW = {
    "card": "0 1px 2px rgba(28, 26, 22, 0.05)",
    "card_hover": "0 4px 14px rgba(28, 26, 22, 0.09)",
    "raised": "0 2px 8px rgba(28, 26, 22, 0.06)",
}

# Fixed per-model identity, used consistently across all three screens so a
# user learns to recognize "brass = two-tower" the same way they'd recognize
# a labeled film reel. Deepened versions of the dark theme's hues, so each
# stays legible against a light background instead of washing out.
MODEL_COLORS = {
    "popularity": "#6E685F",
    "item_item_cf": "#2F5F8A",
    "als": "#3F7A52",
    "two_tower": "#B8752A",
    "sasrec": "#8A4A73",
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
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
}}

.block-container {{
    max-width: 1180px;
    padding-top: 2.2rem;
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
    font-size: 1.5rem;
    font-weight: 700;
    color: {COLORS['text_primary']};
    padding: 1.2rem 0 0.15rem 0;
    letter-spacing: -0.01em;
}}

.mc-wordmark span {{
    color: {COLORS['accent_marquee']};
}}

.mc-sidebar-tagline {{
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: {COLORS['text_muted']};
    line-height: 1.5;
    padding-bottom: 1.1rem;
    border-bottom: 1px solid {COLORS['border_subtle']};
    margin-bottom: 1rem;
}}

.mc-sidebar-footer {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.66rem;
    color: {COLORS['text_faint']};
    line-height: 1.7;
}}

.mc-stack-chip {{
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: {COLORS['text_muted']};
    background-color: {COLORS['bg_surface_raised']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: 4px;
    padding: 0.12rem 0.4rem;
    margin: 0.15rem 0.25rem 0.15rem 0;
}}

.mc-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {COLORS['accent_marquee']};
    font-weight: 500;
}}

.mc-page-title {{
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 2rem;
    color: {COLORS['text_primary']};
    margin: 0.25rem 0 0.4rem 0;
    letter-spacing: -0.015em;
}}

.mc-page-subtitle {{
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: {COLORS['text_muted']};
    max-width: 640px;
    line-height: 1.5;
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
    border-radius: {RADIUS['md']};
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.9rem;
    box-shadow: {SHADOW['card']};
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
}}

.mc-card:hover {{
    border-color: {COLORS['accent_marquee']}77;
    box-shadow: {SHADOW['card_hover']};
}}

.mc-rank-badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background-color: {COLORS['bg_surface_raised']};
    color: {COLORS['text_muted']};
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    margin-right: 0.55rem;
    flex-shrink: 0;
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
    border-radius: {RADIUS['md']};
    padding: 1.1rem 1.2rem;
    height: 100%;
    box-shadow: {SHADOW['card']};
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}}

.mc-persona-card:hover {{
    box-shadow: {SHADOW['card_hover']};
    transform: translateY(-1px);
}}

.mc-persona-icon {{
    font-size: 1.5rem;
    line-height: 1;
    margin-bottom: 0.5rem;
}}

.mc-persona-name {{
    font-family: 'Fraunces', serif;
    font-size: 1.08rem;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

.mc-persona-desc {{
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: {COLORS['text_muted']};
    margin-top: 0.3rem;
    line-height: 1.45;
}}

/* KPI summary cards -- dashboard headline numbers */
.mc-kpi-card {{
    background-color: {COLORS['bg_surface']};
    border: 1px solid {COLORS['border_subtle']};
    border-top: 3px solid {COLORS['accent_marquee']};
    border-radius: {RADIUS['sm']};
    padding: 0.85rem 1rem 0.95rem 1rem;
    box-shadow: {SHADOW['card']};
    height: 100%;
}}

.mc-kpi-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.66rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {COLORS['text_muted']};
    margin-bottom: 0.3rem;
}}

.mc-kpi-value {{
    font-family: 'Fraunces', serif;
    font-size: 1.5rem;
    font-weight: 600;
    line-height: 1.15;
}}

.mc-kpi-caption {{
    font-family: 'Inter', sans-serif;
    font-size: 0.76rem;
    color: {COLORS['text_faint']};
    margin-top: 0.25rem;
}}

/* Empty / placeholder states, used wherever an artifact hasn't been built yet */
.mc-empty-state {{
    background-color: {COLORS['bg_surface']};
    border: 1px dashed {COLORS['border_strong']};
    border-radius: {RADIUS['md']};
    padding: 2.4rem 1.5rem;
    text-align: center;
}}

.mc-empty-icon {{
    font-size: 2rem;
    margin-bottom: 0.6rem;
}}

.mc-empty-message {{
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: {COLORS['text_primary']};
    font-weight: 500;
}}

.mc-empty-hint {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    color: {COLORS['text_muted']};
    margin-top: 0.5rem;
}}

.stButton > button {{
    background-color: {COLORS['bg_surface_raised']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: {RADIUS['sm']};
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    transition: border-color 0.15s ease, color 0.15s ease;
}}

.stButton > button:hover {{
    border-color: {COLORS['accent_marquee']};
    color: {COLORS['accent_marquee']};
}}

.stButton > button:focus-visible {{
    outline: 2px solid {COLORS['accent_marquee_soft']};
    outline-offset: 1px;
}}

div[data-testid="stMetricValue"] {{
    font-family: 'IBM Plex Mono', monospace;
    color: {COLORS['accent_marquee']};
}}

hr {{
    border-color: {COLORS['border_subtle']};
}}

/* Streamlit's default header bar is bright and clashes with the theme --
this is a standalone demo app, not embedded, so blend it in and hide the
toolbar controls. */
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

/* Sidebar nav radio defaults to Streamlit's red accent for the selected
dot -- recolor to match the rest of the token system. The visible dot is
actually two layered divs: an outer "ring" div with the red background,
and a smaller empty leaf div centered inside it. Both need recoloring, or
the red ring shows through around the edges. Auto-generated Streamlit
class names aren't stable across versions, so both are targeted
structurally instead of by class. */
label[data-testid="stRadioOption"][data-selected="true"] div:has(> div:not(:has(*))) {{
    background-color: {COLORS['accent_marquee']} !important;
}}

label[data-testid="stRadioOption"][data-selected="true"] div:not(:has(*)) {{
    background-color: {COLORS['accent_marquee']} !important;
    border-color: {COLORS['accent_marquee']} !important;
}}

label[data-testid="stRadioOption"][data-selected="true"] svg circle {{
    fill: {COLORS['accent_marquee']} !important;
    stroke: {COLORS['accent_marquee']} !important;
}}
</style>
"""
