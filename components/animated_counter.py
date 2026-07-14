"""
Animated KPI Grid Component.

Renders a 2x4 grid of high-fidelity KPI metric cards with synchronized
animated counters for initial page load, and static HTML for sub-second re-renders.
"""

import time
from typing import List, Dict, Any, Optional
import streamlit as st


def format_kpi_value(val: float, is_float: bool, unit: str) -> str:
    """Format KPI value with commas, decimals, and optional unit suffixes."""
    if is_float:
        formatted = f"{val:,.2f}"
    else:
        formatted = f"{int(val):,}"
    
    if unit:
        return f"{formatted} {unit}"
    return formatted


def render_kpi_grid(kpis: List[Dict[str, Any]], session_key: str = "animated_kpi_dashboard") -> None:
    """
    Render a grid of KPI cards with synchronized counter animations on first load.
    
    Args:
        kpis (List[Dict[str, Any]]): List of dicts representing each KPI. Each dict has:
            - 'key': str (unique key)
            - 'value': float (target numeric value)
            - 'label': str (KPI label)
            - 'detail': Optional[str] (subtext details)
            - 'icon_svg': Optional[str] (custom SVG markup)
            - 'trend': Optional[str] (trend string, e.g. "+15%")
            - 'trend_positive': bool (color trend green if True, red if False)
            - 'is_float': bool (whether value should be formatted as float)
            - 'unit': str (suffix unit e.g. "MB")
        session_key (str): Key to track animation state in session_state.
    """
    # Grid parameters
    cols_per_row = 4
    num_kpis = len(kpis)
    
    # Check if animation has already run for this dataset session
    should_animate = not st.session_state.get(session_key, False)
    
    # We will build rows of columns using Streamlit columns
    rows = []
    placeholders = []
    
    for i in range(0, num_kpis, cols_per_row):
        chunk = kpis[i : i + cols_per_row]
        cols = st.columns(len(chunk))
        rows.append((chunk, cols))
        
        # Create empty placeholders in each column
        for col in cols:
            placeholders.append(col.empty())
            
    # Function to build card HTML
    def get_card_html(kpi: Dict[str, Any], current_val: float) -> str:
        val_str = format_kpi_value(current_val, kpi.get("is_float", False), kpi.get("unit", ""))
        
        # Svg Icon resolve
        default_icon = '<svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h10M4 17h14"/></svg>'
        resolved_icon = kpi.get("icon_svg") if kpi.get("icon_svg") else default_icon
        
        # Trend element
        trend_html = ""
        if kpi.get("trend"):
            trend_color = "#4ade80" if kpi.get("trend_positive", True) else "#f87171"
            trend_html = f'<span class="kpi-trend" style="color: {trend_color};">{kpi["trend"]}</span>'
            
        detail_html = f'<p class="kpi-detail">{kpi["detail"]}</p>' if kpi.get("detail") else ""
        
        return f"""
        <div class="kpi-card glass-card" style="margin-bottom: 1rem; min-height: 165px; display: flex; flex-direction: column; justify-content: space-between;">
            <div class="kpi-top" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                <div class="kpi-icon-wrap icon-box" style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: 8px; background: rgba(34, 211, 238, 0.08); border: 1px solid rgba(34, 211, 238, 0.12);">
                    {resolved_icon}
                </div>
                {trend_html}
            </div>
            <div>
                <p class="kpi-value" style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #FAFAFA; letter-spacing: -0.03em;">{val_str}</p>
                <p class="kpi-label" style="margin: 0.25rem 0 0.5rem; font-size: 0.85rem; font-weight: 600; color: #FAFAFA;">{kpi["label"]}</p>
                {detail_html}
            </div>
        </div>
        """

    # If animating, loop progress in parallel
    if should_animate:
        animation_steps = 12
        animation_duration = 0.6  # total duration in seconds
        sleep_step = animation_duration / animation_steps
        
        for step in range(animation_steps + 1):
            progress = step / animation_steps
            # For each KPI, compute its intermediate value and update the placeholder
            for idx, kpi in enumerate(kpis):
                current_val = progress * kpi["value"]
                card_html = get_card_html(kpi, current_val)
                placeholders[idx].markdown(card_html, unsafe_allow_html=True)
            time.sleep(sleep_step)
            
        # Set session state to avoid re-animating
        st.session_state[session_key] = True
    else:
        # Render static HTML immediately
        for idx, kpi in enumerate(kpis):
            card_html = get_card_html(kpi, kpi["value"])
            placeholders[idx].markdown(card_html, unsafe_allow_html=True)
