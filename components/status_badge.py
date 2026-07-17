"""
Reusable status badge component for CLARIO AI.
"""

import streamlit as st


def render_status_badge(label: str, status_type: str = "success") -> None:
    """Render a compact styled status badge pill."""
    bg_color = "rgba(34, 197, 94, 0.1)"
    text_color = "#22C55E"

    if status_type == "warning":
        bg_color = "rgba(245, 158, 11, 0.1)"
        text_color = "#F59E0B"
    elif status_type in ["danger", "error"]:
        bg_color = "rgba(239, 68, 68, 0.1)"
        text_color = "#EF4444"
    elif status_type == "info":
        bg_color = "rgba(91, 108, 255, 0.1)"
        text_color = "#5B6CFF"

    st.markdown(
        f"""
        <span style="display: inline-flex; align-items: center; justify-content: center; 
                     padding: 0.18rem 0.55rem; font-size: 0.72rem; font-weight: 600; 
                     border-radius: 99px; background-color: {bg_color}; color: {text_color}; 
                     white-space: nowrap;">
            {label}
        </span>
        """,
        unsafe_allow_html=True,
    )
