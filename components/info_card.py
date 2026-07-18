"""
Reusable info card notice component for Kosvio.
"""

from typing import Optional
import streamlit as st


def render_info_card(title: str, text: str, card_type: str = "info") -> None:
    """Render a premium enterprise-styled information banner card."""
    border_color = "var(--border)"
    bg_color = "var(--glass)"
    text_color = "var(--text)"
    icon_svg = ""

    if card_type == "success":
        border_color = "rgba(34, 197, 94, 0.2)"
        bg_color = "rgba(34, 197, 94, 0.05)"
        icon_svg = (
            '<svg viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px;">'
            '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
            '<polyline points="22 4 12 14.01 9 11.01"/></svg>'
        )
    elif card_type == "warning":
        border_color = "rgba(245, 158, 11, 0.2)"
        bg_color = "rgba(245, 158, 11, 0.05)"
        icon_svg = (
            '<svg viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px;">'
            '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
            '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
        )
    elif card_type in ["danger", "error"]:
        border_color = "rgba(239, 68, 68, 0.2)"
        bg_color = "rgba(239, 68, 68, 0.05)"
        icon_svg = (
            '<svg viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px;">'
            '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/>'
            '<line x1="9" y1="9" x2="15" y2="15"/></svg>'
        )
    else:  # info
        border_color = "rgba(91, 108, 255, 0.2)"
        bg_color = "rgba(91, 108, 255, 0.05)"
        icon_svg = (
            '<svg viewBox="0 0 24 24" fill="none" stroke="#5B6CFF" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px;">'
            '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/>'
            '<line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
        )

    st.markdown(
        f"""
        <div style="display: flex; gap: 0.75rem; padding: 0.85rem 1.15rem; border-radius: 8px; 
                    border: 1px solid {border_color}; background-color: {bg_color}; margin-bottom: 1rem;">
            <div style="flex-shrink: 0; display: flex; align-items: center;">{icon_svg}</div>
            <div style="flex-grow: 1;">
                <p style="margin: 0; font-size: 0.88rem; font-weight: 600; color: {text_color};">{title}</p>
                <p style="margin: 0.15rem 0 0; font-size: 0.8rem; line-height: 1.4; color: var(--subtext);">{text}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
