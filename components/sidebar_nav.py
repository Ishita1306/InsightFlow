"""
Premium sidebar navigation for InsightFlow.

Renders compact pill buttons with Uiverse-inspired glow animations and
single-click routing backed by session_state["current_page"].
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

# pyrefly: ignore [missing-import]
import streamlit as st


@dataclass(frozen=True)
class NavItem:
    """Single sidebar navigation entry."""

    key: str
    title: str
    description: str
    icon_paths: str


@dataclass(frozen=True)
class NavSection:
    """Grouped navigation section."""

    label: str
    items: tuple[NavItem, ...]


NAV_SECTIONS: tuple[NavSection, ...] = (
    NavSection(
        label="Workspace",
        items=(
            NavItem(
                key="landing",
                title="Home Page",
                description="Platform overview",
                icon_paths='M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-9.5z',
            ),
            NavItem(
                key="dashboard",
                title="Dashboard",
                description="KPIs and live metrics",
                icon_paths=(
                    'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z'
                ),
            ),
        ),
    ),
    NavSection(
        label="Data",
        items=(
            NavItem(
                key="upload",
                title="Upload",
                description="Import CSV datasets",
                icon_paths="M12 16V4M12 4l-4 4M12 4l4 4M4 20h16",
            ),
            NavItem(
                key="overview",
                title="Overview",
                description="Profiling and summaries",
                icon_paths=(
                    'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M8 13h8M8 17h5'
                ),
            ),
            NavItem(
                key="visual_analytics",
                title="Visual Analytics",
                description="Charts and trends",
                icon_paths="M3 3v18h18M7 16l4-6 4 3 5-8",
            ),
        ),
    ),
    NavSection(
        label="Intelligence",
        items=(
            NavItem(
                key="ai_insights",
                title="Insight AI",
                description="Smart recommendations",
                icon_paths=(
                    'M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.4V12h4a2 2 0 0 1 2 2v1h-2v5H8v-5H6v-1a2 2 0 0 1 2-2h4V9.4A4 4 0 0 1 12 2z'
                ),
            ),
            NavItem(
                key="forecasting",
                title="Forecasting",
                description="Predictive models",
                icon_paths="M22 12h-4l-3 9L9 3l-3 9H2",
            ),
            NavItem(
                key="reports",
                title="Report Studio",
                description="Executive exports",
                icon_paths=(
                    'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M9 15l2 2 4-4'
                ),
            ),
        ),
    ),
    NavSection(
        label="System",
        items=(
            NavItem(
                key="settings",
                title="Settings",
                description="Platform preferences",
                icon_paths=(
                    'M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9c.26.604.852.997 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z'
                ),
            ),
        ),
    ),
)

PAGE_LABELS: dict[str, str] = {
    item.key: item.title
    for section in NAV_SECTIONS
    for item in section.items
}
PAGE_LABELS["document_analysis"] = "Doc Analysis"


def get_page_label(page_key: str) -> Optional[str]:
    """Return the sidebar label for a page key, if defined."""
    return PAGE_LABELS.get(page_key)


def _svg_mask_uri(paths: str) -> str:
    """Encode icon paths as an SVG data URI for CSS masking."""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="black" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        f"<path d=\"{paths}\"/></svg>"
    )
    return f"url(\"data:image/svg+xml,{quote(svg)}\")"


@st.cache_data
def _build_nav_icon_styles() -> str:
    """Generate per-item icon mask rules for sidebar pill buttons."""
    rules: list[str] = []
    for section in NAV_SECTIONS:
        for item in section.items:
            mask = _svg_mask_uri(item.icon_paths)
            selector = (
                '[data-testid="stSidebar"] '
                f'[data-testid="element-container"]:has(.nav-pill-seed[data-nav="{item.key}"]) '
                '+ [data-testid="element-container"] button::before'
            )
            rules.append(
                f"{selector} {{ -webkit-mask-image: {mask}; mask-image: {mask}; }}"
            )
            
    # Append signout custom style rule
    signout_mask = _svg_mask_uri("M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9")
    signout_selector = (
        '[data-testid="stSidebar"] '
        '[data-testid="element-container"]:has(.nav-pill-seed[data-nav="signout"]) '
        '+ [data-testid="element-container"] button::before'
    )
    rules.append(f"{signout_selector} {{ -webkit-mask-image: {signout_mask}; mask-image: {signout_mask}; }}")
    
    return "\n".join(rules)


def render_sidebar_branding() -> None:
    """Render the sidebar logo and product tagline."""
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-mark">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M3 3v18h18"/>
                    <path d="M7 16l4-6 4 3 5-8"/>
                </svg>
            </div>
            <div class="sidebar-brand-copy">
                <p class="sidebar-brand-name">Kosvio</p>
                <p class="sidebar-brand-tagline">Every dataset has a story.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_nav_pill(item: NavItem, *, is_active: bool) -> None:
    """Render one pill navigation button."""
    active_flag = "true" if is_active else "false"
    st.sidebar.markdown(
        f'<span class="nav-pill-seed" data-nav="{item.key}" data-active="{active_flag}"></span>',
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        item.title,
        key=f"sidebar_nav_{item.key}",
        width="stretch",
        type="secondary",
        help=item.description,
    ):
        if not is_active:
            st.session_state["current_page"] = item.key
            st.rerun()


def render_sidebar_navigation(current_page: str) -> None:
    """
    Render the full sidebar navigation menu.

    Each item is a single Streamlit button styled as a premium animated pill.
    """
    st.sidebar.markdown(
        f"<style>{_build_nav_icon_styles()}</style>",
        unsafe_allow_html=True,
    )

    for section_index, section in enumerate(NAV_SECTIONS):
        st.sidebar.markdown(
            f'<div class="sidebar-nav-section-label">{section.label}</div>',
            unsafe_allow_html=True,
        )

        for item in section.items:
            _render_nav_pill(item, is_active=current_page == item.key)

        if section_index < len(NAV_SECTIONS) - 1:
            st.sidebar.markdown('<div class="sidebar-nav-spacer"></div>', unsafe_allow_html=True)

    # Render a clean divider and Sign Out button at the bottom
    st.sidebar.markdown('<div class="sidebar-nav-spacer" style="margin-top: auto; border-top: 1px solid var(--border); padding-top: 1rem;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<span class="nav-pill-seed" data-nav="signout" data-active="false"></span>', unsafe_allow_html=True)
    if st.sidebar.button("Sign Out", key="sidebar_signout", width="stretch"):
        from utils.workspace_manager import clear_workspace
        clear_workspace()
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.session_state["current_page"] = "landing"
        st.rerun()

