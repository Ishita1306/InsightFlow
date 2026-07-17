"""
Top navigation bar component for CLARIO AI.

Provides theme toggle, avatar, notification icon, current page title,
active dataset status, search input, and deploy button.
"""

import time
import streamlit as st
from components.sidebar_nav import get_page_label


def render_top_nav() -> None:
    """Render a professional top navigation bar matching enterprise dashboard standards."""
    current_page = st.session_state.get("current_page", "landing")
    page_label = get_page_label(current_page) or "Home"
    if current_page == "landing":
        page_label = "Home"

    # Fetch active dataset details
    has_dataset = "dataset" in st.session_state
    dataset_name = st.session_state.get("dataset_filename", "No Dataset Active")

    # Layout using columns: Left, Center, Right
    col_left, col_center, col_right = st.columns([4, 4, 3])

    with col_left:
        # Title of current workspace (indented slightly to clear the hamburger button)
        st.markdown(
            f"""
            <div class="top-nav-left" style="padding-left: 2.75rem;">
                <span class="top-nav-title">{page_label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_center:
        # Dataset Status Badge (compact outline)
        if has_dataset:
            st.markdown(
                f"""
                <div class="top-nav-status active" title="Active Dataset: {dataset_name}">
                    <span class="status-dot"></span>
                    <span class="status-text">{dataset_name}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="top-nav-status inactive">
                    <span class="status-dot"></span>
                    <span class="status-text">No Active Dataset</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_right:
        # Action controls aligned right using sub-columns (Theme toggle, Notifications, Avatar)
        sub_cols = st.columns([6, 1, 1, 1], gap="small")

        with sub_cols[1]:
            # Theme Switcher Icon Toggle
            current_theme = st.session_state.get("theme", "dark")
            st.markdown(
                f'<span class="top-nav-marker" data-type="theme-toggle" data-theme="{current_theme}"></span>',
                unsafe_allow_html=True,
            )
            if st.button("", key="top_nav_theme", use_container_width=True):
                st.session_state["theme"] = "light" if current_theme == "dark" else "dark"
                st.rerun()

        with sub_cols[2]:
            # Notifications Icon
            st.markdown('<span class="top-nav-marker" data-type="notifications"></span>', unsafe_allow_html=True)
            if st.button("", key="top_nav_notifications", use_container_width=True):
                st.toast("No new alerts. All systems operational.")

        with sub_cols[3]:
            # User Profile Avatar Icon (navigates to settings page)
            st.markdown('<span class="top-nav-marker" data-type="avatar"></span>', unsafe_allow_html=True)
            if st.button("", key="top_nav_avatar", use_container_width=True):
                st.session_state["current_page"] = "settings"
                st.rerun()
