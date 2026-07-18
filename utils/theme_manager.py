"""
Theme manager utility for InsightFlow.
"""

import streamlit as st

THEMES = {
    "dark": {
        "bg": "#0B0F19",
        "surface": "#111827",
        "card": "#1F2937",
        "primary": "#6366F1",
        "secondary": "#4F46E5",
        "accent": "#06B6D4",
        "text": "#FFFFFF",
        "subtext": "#C8CBD7",
        "border": "rgba(255, 255, 255, 0.08)",
        "glass": "rgba(17, 24, 39, 0.55)",
    }
}


def get_current_theme():
    """Retrieve active theme variables (always dark)."""
    return THEMES["dark"]


def inject_theme_css():
    """Inject dark theme CSS variables and premium UI overrides."""
    st.session_state["theme"] = "dark"
    theme_vars = THEMES["dark"]
    
    theme_css = f"""
    <style>
    :root {{
        --bg: {theme_vars['bg']} !important;
        --surface: {theme_vars['surface']} !important;
        --card: {theme_vars['card']} !important;
        --primary: {theme_vars['primary']} !important;
        --secondary: {theme_vars['secondary']} !important;
        --accent: {theme_vars['accent']} !important;
        --text: {theme_vars['text']} !important;
        --subtext: {theme_vars['subtext']} !important;
        --border: {theme_vars['border']} !important;
        --glass: {theme_vars['glass']} !important;
    }}
    
    /* Native App Layout */
    .stApp {{
        background-color: {theme_vars['bg']} !important;
    }}
    
    /* Headers & Text colors */
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: {theme_vars['text']} !important;
    }}
    
    /* Selectboxes, Dropdowns, Inputs styling */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] {{
        background-color: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: {theme_vars['text']} !important;
        transition: all 0.25s ease-in-out !important;
    }}
    
    div[data-baseweb="select"] > div:hover, div[data-baseweb="input"]:hover {{
        border-color: rgba(99, 102, 241, 0.4) !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
    }}
    
    div[data-baseweb="select"] > div:focus-within, div[data-baseweb="input"]:focus-within {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
    }}
    
    div[data-baseweb="select"] span, div[data-baseweb="input"] input {{
        color: {theme_vars['text']} !important;
    }}
    
    /* Popover/Dropdown listbox */
    div[role="listbox"] {{
        background-color: {theme_vars['card']} !important;
        border: 1px solid {theme_vars['border']} !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
    }}
    
    div[role="option"] {{
        color: {theme_vars['text']} !important;
    }}
    div[role="option"]:hover, div[role="option"][aria-selected="true"] {{
        background-color: {theme_vars['surface']} !important;
        color: {theme_vars['primary']} !important;
    }}
    
    /* Tabs styling */
    button[data-baseweb="tab"] {{
        color: {theme_vars['subtext']} !important;
        font-weight: 500 !important;
        background: transparent !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: color 0.18s ease-in-out !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {theme_vars['primary']} !important;
        border-bottom: 2px solid {theme_vars['primary']} !important;
    }}
    
    /* Checkboxes & Radios */
    span[data-baseweb="checkbox"] > div {{
        border-color: {theme_vars['border']} !important;
        border-radius: 6px !important;
        background-color: transparent !important;
    }}
    span[data-baseweb="checkbox"][data-checked="true"] > div {{
        background-color: {theme_vars['primary']} !important;
        border-color: {theme_vars['primary']} !important;
    }}
    
    /* Focus outline on checkbox */
    span[data-baseweb="checkbox"]:focus-within > div {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
    }}
    
    /* Sidebar styling overrides */
    [data-testid="stSidebar"] {{
        background-color: {theme_vars['surface']} !important;
        border-right: 1px solid {theme_vars['border']} !important;
    }}
    
    /* Upload drag and drop box */
    div[data-testid="stFileUploaderDropzone"] {{
        background-color: {theme_vars['surface']} !important;
        border: 1px dashed {theme_vars['primary']} !important;
        border-radius: 18px !important;
    }}
    
    /* Success, Info, Warning, Error alerts styling */
    div[data-testid="stAlert"] {{
        background-color: {theme_vars['card']} !important;
        border: 1px solid {theme_vars['border']} !important;
        border-radius: 18px !important;
    }}
    """
    
    theme_css += "\n</style>"
    st.markdown(theme_css, unsafe_allow_html=True)
