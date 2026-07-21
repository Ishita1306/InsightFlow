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
from components.glass_card import glass_card_panel
from services.analytics import AnalyticsService as DatasetService


def render() -> None:
    """Render the dashboard workspace page."""
    # Check if dataset is in memory
    if "dataset" not in st.session_state:
        render_empty_state(
            title="No Dataset Selected",
            message="We couldn't locate an active dataset in memory. Please upload a dataset first.",
            action_label="Go to Upload Workspace",
            navigate_to="upload",
            navigate_label="Upload",
        )
        return

    df = st.session_state["dataset"]
    filename = st.session_state.get("dataset_filename", "dataset.csv")

    render_section_header(
        title="Dashboard Workspace",
        subtitle=f"Enterprise KPIs and search explorer for {filename}",
        label="Analytics Center",
    )

    if st.session_state.get("cleaned_df") is not None:
        st.info("All insights and metrics are generated from the cleaned dataset.")

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

    # Redesign spacing using Streamlit columns split-pane layout
    col_kpi, col_status = st.columns([5, 2])

    with col_kpi:
        # 1. Dataset Overview
        st.markdown('<p style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-top: 0; margin-bottom: 0.5rem;">Dataset Overview</p>', unsafe_allow_html=True)
        overview_kpis = [k for k in kpi_cards if k["key"] in ["rows", "columns"]]
        render_kpi_grid(overview_kpis, session_key=f"anim_overview_{filename}")
        
        # 2. Business Metrics
        st.markdown('<p style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-top: 1rem; margin-bottom: 0.5rem;">Business Metrics</p>', unsafe_allow_html=True)
        business_kpis = [k for k in kpi_cards if k["key"] in ["numeric", "categorical"]]
        render_kpi_grid(business_kpis, session_key=f"anim_business_{filename}")
        
        # 3. Data Health
        st.markdown('<p style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-top: 1rem; margin-bottom: 0.5rem;">Data Health</p>', unsafe_allow_html=True)
        health_kpis = [k for k in kpi_cards if k["key"] in ["missing", "duplicates"]]
        render_kpi_grid(health_kpis, session_key=f"anim_health_{filename}")
        
        # 4. System Statistics
        st.markdown('<p style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-top: 1rem; margin-bottom: 0.5rem;">System Statistics</p>', unsafe_allow_html=True)
        system_kpis = [k for k in kpi_cards if k["key"] in ["memory", "dates"]]
        render_kpi_grid(system_kpis, session_key=f"anim_system_{filename}")

    with col_status:
        # 1. Dataset Health Score Card
        from pages.upload import calculate_health_score
        health = calculate_health_score(df)
        if health >= 80:
            status_color = "#10B981"
            status_label = "Optimal"
        elif health >= 50:
            status_color = "#F59E0B"
            status_label = "Warnings"
        else:
            status_color = "#EF4444"
            status_label = "Critical"

        with glass_card_panel():
            st.markdown(
                f"""
                <div style="text-align: center; margin-bottom: 0.5rem;">
                    <p style="margin: 0; font-size: 0.82rem; color: var(--subtext);">Dataset Health</p>
                    <h3 style="margin: 0.25rem 0; font-size: 2.25rem; font-weight: 700; color: {status_color};">{health:.1f}</h3>
                    <span style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; color: #fff; background: {status_color}; padding: 0.15rem 0.5rem; border-radius: 99px;">{status_label}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 2. Quick Actions Card
        with glass_card_panel():
            st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--text); margin-top: 0; margin-bottom: 0.75rem;">Quick Actions</p>', unsafe_allow_html=True)
            if st.button("Clean Dataset", width="stretch", key="dash_btn_clean"):
                st.session_state["current_page"] = "upload"
                st.rerun()
            if st.button("Visual Analytics", width="stretch", key="dash_btn_visual"):
                st.session_state["current_page"] = "visual_analytics"
                st.rerun()
            if st.button("Insight AI", width="stretch", key="dash_btn_ai"):
                st.session_state["current_page"] = "ai_insights"
                st.rerun()

        # 3. Recent Activity Log
        if "activity_log" not in st.session_state:
            st.session_state["activity_log"] = [
                {"time": "10:14 AM", "event": "Session workspace loaded."},
                {"time": "10:15 AM", "event": f"File '{filename}' analyzed."},
            ]

        with glass_card_panel():
            st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--text); margin-top: 0; margin-bottom: 0.75rem;">Recent Activity</p>', unsafe_allow_html=True)
            for item in st.session_state["activity_log"][:3]:
                st.markdown(
                    f"""
                    <div style="font-size: 0.78rem; line-height: 1.4; margin-bottom: 0.5rem; border-left: 2px solid var(--border); padding-left: 0.5rem;">
                        <span style="color: var(--subtext); font-weight: 500;">{item['time']}</span> - <span style="color: var(--text);">{item['event']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown('<div style="margin-top: 2rem; border-top: 1px solid var(--border);"></div>', unsafe_allow_html=True)

    # Render paginated dataset explorer
    render_dataset_explorer(df)
