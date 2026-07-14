"""
Dashboard Workspace Page.

Displays the KPI dashboard with synchronized animated counters and embeds
the Dataset Explorer to search, sort, and filter the dataset in detail.
"""

import streamlit as st
import pandas as pd

from components.section_header import render_section_header
from components.empty_state import render_empty_state
from components.animated_counter import render_kpi_grid
from components.dataset_explorer import render_dataset_explorer
from services.dataset_service import DatasetService


def render() -> None:
    """Render the dashboard workspace page."""
    # Check if dataset is in memory
    if "dataset" not in st.session_state:
        clicked = render_empty_state(
            title="No Dataset Selected",
            message="We couldn't locate an active dataset in memory. Please upload a dataset first.",
            action_label="Go to Upload Workspace",
        )
        if clicked:
            st.session_state["current_page"] = "upload"
            st.rerun()
        return

    df = st.session_state["dataset"]
    filename = st.session_state.get("dataset_filename", "dataset.csv")

    render_section_header(
        title="Dashboard Workspace",
        subtitle=f"Enterprise KPIs and search explorer for {filename}",
        label="Analytics Center",
    )

    # Fetch profile and metrics summary
    profile = DatasetService.get_profile(df)
    summary = profile["summary"]

    # Build the 8 KPI data cards for the synchronized animation
    kpi_cards = [
        {
            "key": "rows",
            "value": float(summary["rows"]),
            "label": "Total Rows",
            "detail": "Data samples processed",
            "icon_svg": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/></svg>',
            "is_float": False
        },
        {
            "key": "columns",
            "value": float(summary["columns"]),
            "label": "Total Columns",
            "detail": "Measured variables",
            "icon_svg": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="21" y1="12" x2="3" y2="12"/><line x1="12" y1="3" x2="12" y2="21"/></svg>',
            "is_float": False
        },
        {
            "key": "missing",
            "value": float(summary["missing_cells"]),
            "label": "Missing Values",
            "detail": f"{summary['missing_pct']:.1f}% of total data",
            "trend": f"{summary['missing_pct']:.1f}%",
            "trend_positive": (summary["missing_cells"] == 0),
            "icon_svg": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
            "is_float": False
        },
        {
            "key": "duplicates",
            "value": float(summary["duplicate_rows"]),
            "label": "Duplicate Rows",
            "detail": "Redundant data records",
            "trend": str(summary["duplicate_rows"]),
            "trend_positive": (summary["duplicate_rows"] == 0),
            "icon_svg": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
            "is_float": False
        },
        {
            "key": "memory",
            "value": float(profile["memory_usage_mb"]),
            "label": "Memory Footprint",
            "detail": "System active RAM",
            "icon_svg": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l-7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.73z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
            "is_float": True,
            "unit": "MB"
        },
        {
            "key": "numeric",
            "value": float(summary["numeric_cols"]),
            "label": "Numeric Columns",
            "detail": "Continuous variables",
            "icon_svg": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
            "is_float": False
        },
        {
            "key": "categorical",
            "value": float(summary["categorical_cols"]),
            "label": "Categorical Columns",
            "detail": "Discrete labels/tags",
            "icon_svg": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8l-4 8h8l-4-8z"/></svg>',
            "is_float": False
        },
        {
            "key": "dates",
            "value": float(summary["datetime_cols"]),
            "label": "Date Columns",
            "detail": "Temporal variables",
            "icon_svg": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
            "is_float": False
        }
    ]

    # Render synchronized KPI cards
    render_kpi_grid(kpi_cards, session_key=f"anim_dashboard_{filename}")

    st.markdown('<div style="margin-top: 2rem; border-top: 1px solid var(--border);"></div>', unsafe_allow_html=True)

    # Render paginated dataset explorer
    render_dataset_explorer(df)
