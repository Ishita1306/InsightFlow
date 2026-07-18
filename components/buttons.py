"""
Reusable button components for Kosvio.
"""

from typing import Callable, Optional
import streamlit as st


def primary_button(
    label: str,
    key: str,
    on_click: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
    width: str = "content",
    disabled: bool = False,
) -> bool:
    """Render a styled primary button."""
    st.markdown('<span class="button-marker" data-type="primary"></span>', unsafe_allow_html=True)
    return st.button(
        label,
        key=key,
        type="primary",
        on_click=on_click,
        args=args,
        kwargs=kwargs,
        width=width,
        disabled=disabled,
    )


def secondary_button(
    label: str,
    key: str,
    on_click: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
    width: str = "content",
    disabled: bool = False,
) -> bool:
    """Render a styled secondary button."""
    st.markdown('<span class="button-marker" data-type="secondary"></span>', unsafe_allow_html=True)
    return st.button(
        label,
        key=key,
        type="secondary",
        on_click=on_click,
        args=args,
        kwargs=kwargs,
        width=width,
        disabled=disabled,
    )


def danger_button(
    label: str,
    key: str,
    on_click: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
    width: str = "content",
    disabled: bool = False,
) -> bool:
    """Render a styled danger button."""
    st.markdown('<span class="button-marker" data-type="danger"></span>', unsafe_allow_html=True)
    return st.button(
        label,
        key=key,
        type="secondary",
        on_click=on_click,
        args=args,
        kwargs=kwargs,
        width=width,
        disabled=disabled,
    )
