"""
Theme manager utility for InsightFlow.
"""

import streamlit as st

THEMES = {
    "dark": {
        "bg": "#0B1020",
        "surface": "#0E1326",
        "card": "#12182B",
        "primary": "#6C63FF",
        "secondary": "#4F8CFF",
        "accent": "#6C63FF",
        "text": "#F8FAFC",
        "subtext": "#94A3B8",
        "border": "rgba(255, 255, 255, 0.08)",
        "glass": "rgba(18, 24, 43, 0.85)",
    },
    "light": {
        "bg": "#F6F8FC",
        "surface": "#EFF3F8",
        "card": "#FFFFFF",
        "primary": "#5B5CEB",
        "secondary": "#5B5CEB",
        "accent": "#5B5CEB",
        "text": "#1E293B",
        "subtext": "#64748B",
        "border": "#E2E8F0",
        "glass": "rgba(255, 255, 255, 0.9)",
    }
}


def get_current_theme():
    """Retrieve active theme variables from session state."""
    theme_name = st.session_state.get("theme", "dark")
    return THEMES.get(theme_name, THEMES["dark"])


def inject_theme_css():
    """Inject theme-specific CSS variables to override theme.css variables."""
    theme_name = st.session_state.get("theme", "dark")
    theme_vars = THEMES.get(theme_name, THEMES["dark"])
    
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
        background-color: {theme_vars['surface']} !important;
        border: 1px solid {theme_vars['border']} !important;
        border-radius: 12px !important;
        color: {theme_vars['text']} !important;
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
    }}
    span[data-baseweb="checkbox"][data-checked="true"] > div {{
        background-color: {theme_vars['primary']} !important;
        border-color: {theme_vars['primary']} !important;
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
    
    # Apply flat, gradient-free styles for light theme
    if theme_name == "light":
        theme_css += """
        .stApp {
            background: #F6F8FC !important;
        }
        .hero-section {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
        }
        .hero-glow, .dash-glow-ring {
            display: none !important;
        }
        .glass-card {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
        }
        .glass-card:hover {
            transform: translateY(-4px) !important;
            border-color: #5B5CEB !important;
            box-shadow: 0 8px 30px rgba(91, 92, 235, 0.15) !important;
        }
        """
        
    theme_css += "\n</style>"
    st.markdown(theme_css, unsafe_allow_html=True)
