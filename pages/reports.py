"""
Report Studio Page.

Allows users to compile and preview high-fidelity executive reports.
Includes Executive Summaries, KPIs, Data Quality audits, Forecast projections,
and AI recommendations. Exports are provided for PDF, Excel, and PowerPoint.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from components.section_header import render_section_header
from components.empty_state import render_empty_state
from components.glass_card import glass_card_panel
from services.reporting import (
    compile_excel_report,
    compile_pdf_document,
    compile_powerpoint_briefing,
    compile_docx_report,
    compile_html_report,
)


def render() -> None:
    """Render the Report Studio Workspace."""
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
        title="Report Studio Workspace",
        subtitle=f"Compile, review, and export executive intelligence briefings for {filename}.",
        label="Executive Briefing Studio",
    )

    if st.session_state.get("cleaned_df") is not None:
        st.info("All insights and metrics are generated from the cleaned dataset.")

    from services.analytics import AnalyticsService as DatasetService
    from pages.upload import perform_advanced_audit, calculate_health_score
    profile = DatasetService.get_profile(df)
    summary = profile["summary"]
    audit = perform_advanced_audit(df)
    health = calculate_health_score(df)
    
    # Retrieve active forecast data if present
    active_fore = st.session_state.get("active_forecast", {})
    forecast_df = active_fore.get("df")

    # Inject CSS custom styling for premium enterprise BI look
    st.markdown(
        """
        <style>
        .kpi-card {
            background: var(--card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 16px !important;
            padding: 1.25rem !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            min-height: 120px !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        }
        .kpi-card:hover {
            transform: translateY(-4px) !important;
            border-color: var(--primary) !important;
            box-shadow: 0 0 20px rgba(108, 99, 255, 0.2) !important;
        }
        .kpi-card-icon {
            font-size: 1.6rem !important;
            margin-bottom: 0.35rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .kpi-card-val {
            font-size: 1.45rem !important;
            font-weight: 800 !important;
            color: var(--text) !important;
            line-height: 1.2 !important;
        }
        .kpi-card-lbl {
            font-size: 0.72rem !important;
            color: var(--subtext) !important;
            font-weight: 600 !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase !important;
            margin-top: 0.25rem !important;
        }

        /* Circular progress indicator */
        .health-score-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 1.5rem !important;
            min-height: 250px !important;
        }
        .circular-progress {
            position: relative !important;
            width: 130px !important;
            height: 130px !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .circular-progress::before {
            content: "" !important;
            position: absolute !important;
            width: 108px !important;
            height: 108px !important;
            border-radius: 50% !important;
            background: var(--card) !important;
        }
        .circular-progress-val {
            position: relative !important;
            font-size: 1.75rem !important;
            font-weight: 800 !important;
            color: var(--text) !important;
            z-index: 1 !important;
        }

        /* Recommendation card styling */
        .rec-card {
            background: rgba(108, 99, 255, 0.03) !important;
            border: 1px solid rgba(108, 99, 255, 0.12) !important;
            border-left: 5px solid var(--primary) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            margin-bottom: 0.75rem !important;
            display: flex !important;
            gap: 0.75rem !important;
            align-items: flex-start !important;
        }
        .rec-card.accent {
            background: rgba(6, 182, 212, 0.03) !important;
            border: 1px solid rgba(6, 182, 212, 0.12) !important;
            border-left: 5px solid var(--accent) !important;
        }
        .rec-card-icon {
            font-size: 1.35rem !important;
            margin-top: 0.1rem !important;
            flex-shrink: 0 !important;
        }
        .rec-card-title {
            font-size: 0.9rem !important;
            font-weight: 700 !important;
            color: var(--text) !important;
            margin: 0 0 0.25rem 0 !important;
        }
        .rec-card-desc {
            font-size: 0.8rem !important;
            color: var(--subtext) !important;
            line-height: 1.4 !important;
            margin: 0 !important;
        }

        /* Cleaning summary card styling */
        .summary-card {
            background: var(--card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.75rem !important;
        }
        .summary-card-icon {
            width: 40px !important;
            height: 40px !important;
            border-radius: 8px !important;
            background: rgba(255,255,255,0.02) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 1.15rem !important;
            border: 1px solid var(--border) !important;
            flex-shrink: 0 !important;
        }
        .summary-card-info {
            display: flex !important;
            flex-direction: column !important;
        }
        .summary-card-lbl {
            font-size: 0.75rem !important;
            color: var(--subtext) !important;
            font-weight: 500 !important;
        }
        .summary-card-val {
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: var(--text) !important;
            margin-top: 0.1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 1. Row 1: Executive Summary & Data Quality Score (circular progress)
    col_summary, col_health = st.columns([2.2, 1])

    with col_summary:
        with st.container(border=True):
            st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--subtext); margin: 0 0 0.5rem 0; text-transform: uppercase; letter-spacing: 0.05em;">Executive Summary</p>', unsafe_allow_html=True)
            st.markdown(
                f"<div style='font-size: 0.95rem; line-height: 1.6; color: var(--text); margin-bottom: 1.5rem;'>"
                f"This executive briefing documents the statistical profile and data quality audit of the dataset <strong>{filename}</strong>. "
                f"The ingestion pipeline has successfully validated the structure, classifications, and formatting parameters of the dataset. "
                f"The overall data quality health score is rated at <strong>{health:.1f}/100</strong>, indicating the readiness of the data for advanced analytics and modeling."
                f"</div>",
                unsafe_allow_html=True
            )

            st.markdown('<p style="font-size: 0.8rem; font-weight: 600; color: var(--subtext); margin: 0 0 0.5rem 0; text-transform: uppercase; letter-spacing: 0.05em;">Export Actions</p>', unsafe_allow_html=True)
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            with col_btn1:
                pdf_bytes = compile_pdf_document(filename, summary, audit, health, forecast_df)
                st.download_button(
                    "📄 Export to PDF",
                    data=pdf_bytes,
                    file_name=f"kosvio_report_{filename.split('.')[0]}.html",
                    mime="text/html",
                    width="stretch",
                    key="btn_exp_pdf",
                    help="Downloads a print-optimized document which auto-triggers the print/PDF save dialog."
                )
            with col_btn2:
                docx_bytes = compile_docx_report(filename, summary, audit, health, forecast_df)
                st.download_button(
                    "📝 Export to Word",
                    data=docx_bytes,
                    file_name=f"kosvio_briefing_{filename.split('.')[0]}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    width="stretch",
                    key="btn_exp_docx"
                )
            with col_btn3:
                html_bytes = compile_html_report(filename, summary, audit, health, forecast_df)
                st.download_button(
                    "🌐 Export to HTML",
                    data=html_bytes,
                    file_name=f"kosvio_briefing_{filename.split('.')[0]}.html",
                    mime="text/html",
                    width="stretch",
                    key="btn_exp_html"
                )
            with col_btn4:
                excel_bytes = compile_excel_report(df, summary, audit)
                st.download_button(
                    "📊 Export to Excel",
                    data=excel_bytes,
                    file_name=f"kosvio_briefing_{filename.split('.')[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch",
                    key="btn_exp_xlsx"
                )

    with col_health:
        health_color = "var(--primary)"
        if health < 50:
            health_color = "#EF4444"
        elif health < 80:
            health_color = "#F59E0B"
        else:
            health_color = "var(--accent)"

        conic_grad = f"conic-gradient({health_color} {health}%, rgba(255,255,255,0.05) 0)"

        st.markdown(
            f"""
            <div class="glass-card health-score-container">
                <p style="font-size: 0.85rem; font-weight: 600; color: var(--subtext); margin: 0 0 1rem 0; text-transform: uppercase; letter-spacing: 0.05em; text-align: center;">Data Quality Score</p>
                <div style="display: flex; justify-content: center; width: 100%;">
                    <div class="circular-progress" style="background: {conic_grad};">
                        <div class="circular-progress-val">{health:.1f}%</div>
                    </div>
                </div>
                <p style="font-size: 0.78rem; color: var(--subtext); margin-top: 1.25rem; text-align: center; line-height: 1.4;">Overall health rating of active dataset variables and formats</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Row 2: Dataset Statistics (KPI cards)
    st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 1.5rem; margin-bottom: 0.75rem;">Dataset Statistics</p>', unsafe_allow_html=True)
    col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5, col_kpi6 = st.columns(6)

    with col_kpi1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-icon">📊</div>
                <div class="kpi-card-val">{summary['rows']:,}</div>
                <div class="kpi-card-lbl">Total Rows</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_kpi2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-icon">📋</div>
                <div class="kpi-card-val">{summary['columns']}</div>
                <div class="kpi-card-lbl">Total Columns</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_kpi3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-icon">🔍</div>
                <div class="kpi-card-val">{audit['missing_cells']:,}</div>
                <div class="kpi-card-lbl">Missing Values</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_kpi4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-icon">👥</div>
                <div class="kpi-card-val">{audit['duplicate_rows']:,}</div>
                <div class="kpi-card-lbl">Duplicate Rows</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_kpi5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-icon">💖</div>
                <div class="kpi-card-val">{health:.1f}%</div>
                <div class="kpi-card-lbl">Health Score</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_kpi6:
        mem_kb = summary['memory_bytes'] / 1024
        if mem_kb > 1024:
            mem_str = f"{mem_kb / 1024:.1f} MB"
        else:
            mem_str = f"{mem_kb:.1f} KB"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-icon">💾</div>
                <div class="kpi-card-val">{mem_str}</div>
                <div class="kpi-card-lbl">Memory Size</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 3. Row 3: Small charts (Data Completeness, Variable Types Breakdown, Top Column Cardinality)
    st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 1.5rem; margin-bottom: 0.75rem;">Dataset Distributions & Quality</p>', unsafe_allow_html=True)
    col_chart1, col_chart2, col_chart3 = st.columns(3)

    with col_chart1:
        with st.container(border=True):
            total_cells = df.size
            missing_cells = audit["missing_cells"]
            complete_cells = total_cells - missing_cells

            fig_missing = go.Figure(data=[go.Pie(
                labels=["Complete", "Missing"],
                values=[complete_cells, missing_cells],
                hole=0.5,
                marker=dict(colors=["var(--accent)", "rgba(239, 68, 68, 0.4)"], line=dict(color="var(--bg)", width=1.5)),
                textinfo="percent",
                showlegend=True
            )])
            fig_missing.update_layout(
                title=dict(text="Data Completeness", font=dict(size=12, color="var(--text)"), x=0.5, xanchor="center"),
                height=180,
                margin=dict(l=10, r=10, t=30, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            from pages.overview import apply_plotly_theme
            apply_plotly_theme(fig_missing)
            st.plotly_chart(fig_missing, width="stretch", key="fig_comp")

    with col_chart2:
        with st.container(border=True):
            type_counts = df.dtypes.value_counts()
            friendly_types = []
            for t in type_counts.index:
                t_str = str(t)
                if t_str.startswith("int") or t_str.startswith("float") or t_str.startswith("UInt"):
                    friendly_types.append("Numeric")
                elif t_str.startswith("date"):
                    friendly_types.append("DateTime")
                elif t_str == "category" or t_str == "bool":
                    friendly_types.append("Categorical")
                else:
                    friendly_types.append("Object/Text")

            type_data = pd.DataFrame({"Type": friendly_types, "Count": type_counts.values})
            type_grouped = type_data.groupby("Type").sum().reset_index()

            fig_types = go.Figure(data=[go.Bar(
                x=type_grouped["Type"],
                y=type_grouped["Count"],
                marker_color="var(--primary)",
                marker_line=dict(color="var(--bg)", width=1)
            )])
            fig_types.update_layout(
                title=dict(text="Variable Types Breakdown", font=dict(size=12, color="var(--text)"), x=0.5, xanchor="center"),
                height=180,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            apply_plotly_theme(fig_types)
            st.plotly_chart(fig_types, width="stretch", key="fig_types")

    with col_chart3:
        with st.container(border=True):
            cols = df.columns
            cardinalities = [df[col].nunique() for col in cols]
            card_df = pd.DataFrame({"Column": cols, "Unique Values": cardinalities})
            card_df = card_df.sort_values(by="Unique Values", ascending=False).head(5)

            fig_dist = go.Figure(data=[go.Bar(
                y=card_df["Column"],
                x=card_df["Unique Values"],
                orientation="h",
                marker_color="var(--accent)",
                marker_line=dict(color="var(--bg)", width=1)
            )])
            fig_dist.update_layout(
                title=dict(text="Top Column Cardinality", font=dict(size=12, color="var(--text)"), x=0.5, xanchor="center"),
                height=180,
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis=dict(title="Unique Values"),
                yaxis=dict(autorange="reversed")
            )
            apply_plotly_theme(fig_dist)
            st.plotly_chart(fig_dist, width="stretch", key="fig_card")

    # 4. Row 4: Data Cleaning Summary & AI Business Recommendations
    col_clean, col_rec = st.columns([1, 1.3])

    with col_clean:
        with st.container(border=True):
            st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--subtext); margin: 0 0 1rem 0; text-transform: uppercase; letter-spacing: 0.05em;">Cleaning Summary</p>', unsafe_allow_html=True)

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown(
                    f"""
                    <div class="summary-card">
                        <div class="summary-card-icon">👥</div>
                        <div class="summary-card-info">
                            <span class="summary-card-lbl">Duplicate Records</span>
                            <span class="summary-card-val">{audit['duplicate_rows']:,} Rows</span>
                        </div>
                    </div>
                    <div class="summary-card" style="margin-top: 1rem;">
                        <div class="summary-card-icon">📈</div>
                        <div class="summary-card-info">
                            <span class="summary-card-lbl">Outliers (IQR)</span>
                            <span class="summary-card-val">{audit['outliers_count']:,} Values</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_s2:
                st.markdown(
                    f"""
                    <div class="summary-card">
                        <div class="summary-card-icon">🔒</div>
                        <div class="summary-card-info">
                            <span class="summary-card-lbl">Constant Columns</span>
                            <span class="summary-card-val">{len(audit['constant_cols'])} Columns</span>
                        </div>
                    </div>
                    <div class="summary-card" style="margin-top: 1rem;">
                        <div class="summary-card-icon">⚙️</div>
                        <div class="summary-card-info">
                            <span class="summary-card-lbl">Type Anomalies</span>
                            <span class="summary-card-val">{len(audit['incorrect_cols'])} Columns</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with col_rec:
        with st.container(border=True):
            st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--subtext); margin: 0 0 1rem 0; text-transform: uppercase; letter-spacing: 0.05em;">AI Insights & Business Recommendations</p>', unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="rec-card">
                    <div class="rec-card-icon">💡</div>
                    <div>
                        <h5 class="rec-card-title">Recommendation 1: In-Session Data Imputation</h5>
                        <p class="rec-card-desc">We identified {audit['missing_cells']:,} missing cells. It is strategically advised to impute numerical columns using median statistics and text/categorical columns using mode statistics to avoid statistical bias.</p>
                    </div>
                </div>
                <div class="rec-card accent">
                    <div class="rec-card-icon">⚡</div>
                    <div>
                        <h5 class="rec-card-title">Recommendation 2: Remove Redundant Data Rows</h5>
                        <p class="rec-card-desc">There are {audit['duplicate_rows']:,} duplicate rows. To ensure optimal performance and prevent machine learning model over-fitting, deduplicate these records before running analytics.</p>
                    </div>
                </div>
                <div class="rec-card">
                    <div class="rec-card-icon">🌐</div>
                    <div>
                        <h5 class="rec-card-title">Recommendation 3: Align Inferred Columns & Timelines</h5>
                        <p class="rec-card-desc">{len(audit['incorrect_cols'])} columns are using mismatched datatypes. Aligning categories and parsing date columns will activate forecasting and time-series projection charts.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    render()
