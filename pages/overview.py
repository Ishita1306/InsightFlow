"""
Dataset Overview Page.

Renders interactive Plotly charts, feature summaries, and profiles
of numerical, categorical, and date variables matching the luxury dark design system.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from components.section_header import render_section_header
from components.empty_state import render_empty_state
from components.metric_card import render_metric_card
from components.table_container import render_table_container
from services.dataset_service import DatasetService
from pages.upload import perform_advanced_audit, calculate_health_score


def apply_plotly_theme(fig: go.Figure) -> None:
    """Apply the active theme properties to a Plotly figure."""
    from utils.theme_manager import get_current_theme
    theme_vars = get_current_theme()
    paper_bg = "rgba(0,0,0,0)"
    font_col = theme_vars['text']
    legend_col = theme_vars['subtext']
    grid_col = theme_vars['border']
    zero_col = theme_vars['border']
    axis_col = theme_vars['subtext']

    fig.update_layout(
        paper_bgcolor=paper_bg,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font_family="Inter, -apple-system, sans-serif",
        font_color=font_col,
        title_font_color=font_col,
        legend_font_color=legend_col,
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(
            gridcolor=grid_col,
            zerolinecolor=zero_col,
            color=axis_col,
            tickfont=dict(size=10),
            title=dict(font=dict(color=axis_col, size=11)),
        ),
        yaxis=dict(
            gridcolor=grid_col,
            zerolinecolor=zero_col,
            color=axis_col,
            tickfont=dict(size=10),
            title=dict(font=dict(color=axis_col, size=11)),
        ),
    )


def render() -> None:
    """Render the overview workspace."""
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
        title="Dataset Overview",
        subtitle=f"Statistical variables and metrics breakdown for {filename}.",
        label="Dataset Profiler",
    )

    # 1. Metric stats & quality audits
    profile = DatasetService.get_profile(df)
    summary = profile["summary"]
    audit = perform_advanced_audit(df)
    health = calculate_health_score(df)
    
    from utils.theme_manager import get_current_theme
    theme_vars = get_current_theme()

    # Dynamic summary panel text and AI observations calculations
    total_rows = summary['rows']
    total_cols = summary['columns']
    missing_cells = audit['missing_cells']
    dup_cnt = audit['duplicate_rows']
    missing_pct = audit['missing_pct']
    
    # Determine quality level description
    if health >= 85:
        quality_desc = "excellent"
    elif health >= 70:
        quality_desc = "good with minor issues"
    elif health >= 50:
        quality_desc = "fair with notable anomalies"
    else:
        quality_desc = "poor with significant issues"
        
    missing_desc = "no missing values" if missing_cells == 0 else f"{missing_cells:,} missing cells ({missing_pct:.1f}%)"
    dup_desc = "no duplicate rows" if dup_cnt == 0 else f"{dup_cnt:,} duplicate record" + ("s" if dup_cnt > 1 else "")
    
    summary_text = (
        f"This dataset contains <strong>{total_rows:,}</strong> records across <strong>{total_cols}</strong> variables. "
        f"Data quality is <strong>{quality_desc}</strong>, featuring {missing_desc} and {dup_desc}. "
        f"The dataset is <strong>{'highly suitable' if health >= 75 else 'partially suitable' if health >= 50 else 'unsuitable'}</strong> "
        f"for business intelligence and predictive modeling."
    )

    # 1. Correlations
    strong_corrs = []
    numeric_df = df.loc[:, ~df.isna().all()].select_dtypes(include=[np.number])
    if len(numeric_df.columns) > 1:
        corr_matrix = numeric_df.corr().abs()
        upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        for col in upper_tri.columns:
            for row in upper_tri.index:
                val = upper_tri.loc[row, col]
                if pd.notna(val) and val >= 0.6:
                    sign = "positive" if numeric_df.corr().loc[row, col] > 0 else "negative"
                    strong_corrs.append(f"Strong {sign} correlation between <strong>{row}</strong> and <strong>{col}</strong> ({numeric_df.corr().loc[row, col]:.2f})")

    # 2. High Cardinality
    high_card = [f"High cardinality in <strong>{col}</strong> ({df[col].nunique()} unique values)" for col in df.columns if df[col].dtype == "object" and 20 < df[col].nunique() < len(df)]

    # 3. Outliers
    outliers_cols = [f"Potential outliers in <strong>{col}</strong> ({cnt} values detected)" for col, cnt in audit.get("outlier_cols", {}).items() if cnt > 0]

    # 4. Missing values per column
    missing_cols = [f"Missing values in <strong>{col}</strong> ({df[col].isnull().sum()} cells)" for col in df.columns if df[col].isnull().sum() > 0]

    # 5. Quality warnings
    quality_warnings = []
    if audit.get("constant_cols"):
        quality_warnings.append(f"Constant column detected: <strong>{', '.join(audit['constant_cols'])}</strong> (no information variance)")
    if audit.get("invalid_date_cols"):
        invalid_cols = [col for col, cnt in audit["invalid_date_cols"].items() if cnt > 0]
        if invalid_cols:
            quality_warnings.append(f"Invalid date formats in column: <strong>{', '.join(invalid_cols)}</strong>")

    # Inject custom styling for premium enterprise BI look
    st.markdown(
        """
        <style>
        .profile-kpi-card {
            background: var(--card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            padding: 0.85rem !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            min-height: 80px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease !important;
        }
        .profile-kpi-card:hover {
            transform: translateY(-2px) !important;
            border-color: var(--primary) !important;
        }
        .profile-kpi-lbl {
            font-size: 0.68rem !important;
            color: var(--subtext) !important;
            font-weight: 600 !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase !important;
            margin-bottom: 0.25rem !important;
        }
        .profile-kpi-val {
            font-size: 1.25rem !important;
            font-weight: 800 !important;
            color: var(--text) !important;
        }
        
        .quality-card {
            background: var(--card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            padding: 0.75rem !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.75rem !important;
            min-height: 55px !important;
            transition: all 0.2s ease !important;
        }
        .quality-card:hover {
            border-color: var(--primary) !important;
        }
        .quality-indicator {
            width: 10px !important;
            height: 10px !important;
            border-radius: 50% !important;
            flex-shrink: 0 !important;
        }
        .quality-indicator.green {
            background: #10B981 !important;
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.4) !important;
        }
        .quality-indicator.yellow {
            background: #F59E0B !important;
            box-shadow: 0 0 8px rgba(245, 158, 11, 0.4) !important;
        }
        .quality-indicator.red {
            background: #EF4444 !important;
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.4) !important;
        }
        .quality-card-info {
            display: flex !important;
            flex-direction: column !important;
        }
        .quality-lbl {
            font-size: 0.72rem !important;
            color: var(--subtext) !important;
            font-weight: 500 !important;
        }
        .quality-val {
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            color: var(--text) !important;
            margin-top: 0.05rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 2. Summary KPI Cards
    st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 1rem; margin-bottom: 0.75rem;">Dataset Profile Indicators</p>', unsafe_allow_html=True)
    kpi_row1_c1, kpi_row1_c2, kpi_row1_c3, kpi_row1_c4 = st.columns(4)
    kpi_row2_c1, kpi_row2_c2, kpi_row2_c3, kpi_row2_c4 = st.columns(4)

    with kpi_row1_c1:
        st.markdown(f'<div class="profile-kpi-card"><span class="profile-kpi-lbl">Total Rows</span><span class="profile-kpi-val">{summary["rows"]:,}</span></div>', unsafe_allow_html=True)
    with kpi_row1_c2:
        st.markdown(f'<div class="profile-kpi-card"><span class="profile-kpi-lbl">Total Columns</span><span class="profile-kpi-val">{summary["columns"]}</span></div>', unsafe_allow_html=True)
    with kpi_row1_c3:
        st.markdown(f'<div class="profile-kpi-card"><span class="profile-kpi-lbl">Numeric Columns</span><span class="profile-kpi-val">{summary["numeric_cols"]}</span></div>', unsafe_allow_html=True)
    with kpi_row1_c4:
        st.markdown(f'<div class="profile-kpi-card"><span class="profile-kpi-lbl">Categorical Columns</span><span class="profile-kpi-val">{summary["categorical_cols"]}</span></div>', unsafe_allow_html=True)

    with kpi_row2_c1:
        st.markdown(f'<div class="profile-kpi-card"><span class="profile-kpi-lbl">Date Columns</span><span class="profile-kpi-val">{summary["datetime_cols"]}</span></div>', unsafe_allow_html=True)
    with kpi_row2_c2:
        st.markdown(f'<div class="profile-kpi-card"><span class="profile-kpi-lbl">Missing Cells</span><span class="profile-kpi-val">{summary["missing_cells"]:,}</span></div>', unsafe_allow_html=True)
    with kpi_row2_c3:
        st.markdown(f'<div class="profile-kpi-card"><span class="profile-kpi-lbl">Duplicate Rows</span><span class="profile-kpi-val">{audit["duplicate_rows"]:,}</span></div>', unsafe_allow_html=True)
    with kpi_row2_c4:
        mem_kb = summary['memory_bytes'] / 1024
        mem_str = f"{mem_kb / 1024:.1f} MB" if mem_kb > 1024 else f"{mem_kb:.1f} KB"
        st.markdown(f'<div class="profile-kpi-card"><span class="profile-kpi-lbl">Memory Size</span><span class="profile-kpi-val">{mem_str}</span></div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)

    # 3. Dynamic Summary Panel & Data Quality Grid
    col_summary_panel, col_quality_grid = st.columns([1.5, 1])

    with col_summary_panel:
        with st.container(border=True):
            st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--subtext); margin: 0 0 0.5rem 0; text-transform: uppercase; letter-spacing: 0.05em;">Dataset Summary</p>', unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 0.9rem; line-height: 1.5; color: var(--text); margin-bottom: 1.25rem;'>{summary_text}</div>", unsafe_allow_html=True)
            
            st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--subtext); margin: 0 0 0.5rem 0; text-transform: uppercase; letter-spacing: 0.05em;">AI Observations</p>', unsafe_allow_html=True)
            
            obs_html = ""
            # Correlations
            for corr_msg in strong_corrs[:2]:
                obs_html += f"<div style='font-size: 0.82rem; margin-bottom: 0.4rem; color: var(--text);'>🔹 {corr_msg}</div>"
            # High Cardinality
            for card_msg in high_card[:2]:
                obs_html += f"<div style='font-size: 0.82rem; margin-bottom: 0.4rem; color: var(--text);'>🔸 {card_msg}</div>"
            # Outliers
            for out_msg in outliers_cols[:2]:
                obs_html += f"<div style='font-size: 0.82rem; margin-bottom: 0.4rem; color: var(--text);'>⚠️ {out_msg}</div>"
            # Missing
            for mis_msg in missing_cols[:2]:
                obs_html += f"<div style='font-size: 0.82rem; margin-bottom: 0.4rem; color: var(--text);'>🔍 {mis_msg}</div>"
            # General warnings
            for wrn_msg in quality_warnings:
                obs_html += f"<div style='font-size: 0.82rem; margin-bottom: 0.4rem; color: var(--text);'>🚫 {wrn_msg}</div>"
                
            if not obs_html:
                obs_html = "<div style='font-size: 0.82rem; color: var(--subtext); font-style: italic;'>No critical data issues or anomalous correlations detected. The dataset structure appears clean.</div>"
                
            st.markdown(f"<div style='display: flex; flex-direction: column;'>{obs_html}</div>", unsafe_allow_html=True)

    with col_quality_grid:
        with st.container(border=True):
            st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--subtext); margin: 0 0 0.75rem 0; text-transform: uppercase; letter-spacing: 0.05em; text-align: center;">Data Quality Standing</p>', unsafe_allow_html=True)
            
            q_col1, q_col2 = st.columns(2)
            
            with q_col1:
                mis_status = "green" if missing_cells == 0 else "yellow" if missing_pct < 10 else "red"
                st.markdown(f"""
                    <div class="quality-card">
                        <div class="quality-indicator {mis_status}"></div>
                        <div class="quality-card-info">
                            <span class="quality-lbl">Missing cells</span>
                            <span class="quality-val">{missing_pct:.1f}%</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with q_col2:
                dup_status = "green" if dup_cnt == 0 else "yellow"
                st.markdown(f"""
                    <div class="quality-card">
                        <div class="quality-indicator {dup_status}"></div>
                        <div class="quality-card-info">
                            <span class="quality-lbl">Duplicate rows</span>
                            <span class="quality-val">{dup_cnt:,} Rows</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown('<div style="margin-top: 0.75rem;"></div>', unsafe_allow_html=True)
            q_col3, q_col4 = st.columns(2)
            
            with q_col3:
                out_status = "green" if len(outliers_cols) == 0 else "yellow"
                st.markdown(f"""
                    <div class="quality-card">
                        <div class="quality-indicator {out_status}"></div>
                        <div class="quality-card-info">
                            <span class="quality-lbl">Outliers (IQR)</span>
                            <span class="quality-val">{audit.get('outliers_count', 0):,} Values</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with q_col4:
                type_status = "green" if len(audit.get('incorrect_cols', [])) == 0 else "yellow"
                st.markdown(f"""
                    <div class="quality-card">
                        <div class="quality-indicator {type_status}"></div>
                        <div class="quality-card-info">
                            <span class="quality-lbl">Type Anomalies</span>
                            <span class="quality-val">{len(audit.get('incorrect_cols', []))} Columns</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown('<div style="margin-top: 0.75rem;"></div>', unsafe_allow_html=True)
            q_col5, q_col6 = st.columns(2)
            
            with q_col5:
                const_status = "green" if len(audit.get('constant_cols', [])) == 0 else "yellow"
                st.markdown(f"""
                    <div class="quality-card">
                        <div class="quality-indicator {const_status}"></div>
                        <div class="quality-card-info">
                            <span class="quality-lbl">Constant columns</span>
                            <span class="quality-val">{len(audit.get('constant_cols', []))} Cols</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with q_col6:
                hlth_status = "green" if health >= 80 else "yellow" if health >= 50 else "red"
                st.markdown(f"""
                    <div class="quality-card">
                        <div class="quality-indicator {hlth_status}"></div>
                        <div class="quality-card-info">
                            <span class="quality-lbl">Overall Health</span>
                            <span class="quality-val">{health:.1f}%</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)

    # 4. Interactive Visualizations Section
    st.markdown('<h3 style="margin-top: 2rem; font-weight: 700;">Interactive Explorations</h3>', unsafe_allow_html=True)
    
    chart_row1_c1, chart_row1_c2 = st.columns(2)
    
    # 1. Donut Chart - Columns Data Types
    with chart_row1_c1:
        with st.container(border=True):
            data_types_counts = {
                "Numeric": summary["numeric_cols"],
                "Categorical": summary["categorical_cols"],
                "Date/Time": summary["datetime_cols"],
            }
            labels = [k for k, v in data_types_counts.items() if v > 0]
            values = [v for k, v in data_types_counts.items() if v > 0]

            if values:
                fig_types = px.pie(
                    names=labels,
                    values=values,
                    hole=0.6,
                    title="Data Types Distribution",
                    color_discrete_sequence=[theme_vars['primary'], theme_vars['accent'], theme_vars['subtext']],
                )
                apply_plotly_theme(fig_types)
                fig_types.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_types, use_container_width=True, key="donut_types")
            else:
                st.info("No columns available to plot data types.")
                
    # 2. Horizontal Bar Chart - Missing Values per Column
    with chart_row1_c2:
        with st.container(border=True):
            missing_df = profile["missing"]
            if not missing_df.empty:
                missing_df_reset = missing_df.reset_index().rename(
                    columns={"index": "Column", "Missing Count": "Missing Count"}
                )
                # Keep only columns with > 0 missing count, sort them descending
                missing_df_reset = missing_df_reset[missing_df_reset["Missing Count"] > 0]
                missing_df_reset = missing_df_reset.sort_values(by="Missing Count", ascending=False)
                
                if not missing_df_reset.empty:
                    fig_missing = px.bar(
                        missing_df_reset,
                        x="Missing Count",
                        y="Column",
                        orientation="h",
                        title="Missing Values Count per Column",
                        color_discrete_sequence=[theme_vars['primary']],
                    )
                    apply_plotly_theme(fig_missing)
                    fig_missing.update_layout(height=340, yaxis=dict(autorange="reversed"), margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig_missing, use_container_width=True, key="bar_missing")
                else:
                    # Render complete message
                    fig_complete = go.Figure(
                        go.Indicator(
                            mode="number+gauge",
                            value=100,
                            number={"suffix": "%", "font": {"color": "#10B981"}},
                            title={"text": "Data Completeness Rate", "font": {"color": theme_vars['text']}},
                            gauge={
                                "axis": {"range": [0, 100], "tickcolor": theme_vars['text']},
                                "bar": {"color": "#10B981"},
                                "bgcolor": "rgba(0,0,0,0.02)" if st.session_state.get("theme") == "light" else "rgba(255,255,255,0.02)",
                                "steps": [{"range": [0, 100], "color": "rgba(99,102,241,0.04)"}],
                            },
                        )
                    )
                    apply_plotly_theme(fig_complete)
                    fig_complete.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig_complete, use_container_width=True, key="indicator_complete")
            else:
                st.info("No missing values profile data found.")

    # 3. Numeric Variable Histogram & Box Plot Row
    st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 1.5rem; margin-bottom: 0.5rem;">Numerical Variables Inspection</p>', unsafe_allow_html=True)
    numeric_cols = df.loc[:, ~df.isna().all()].select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        selected_num = st.selectbox(
            "Select Variable for Distribution & Outlier plots", numeric_cols, key="sel_num_var"
        )
        chart_row2_c1, chart_row2_c2 = st.columns(2)
        
        with chart_row2_c1:
            with st.container(border=True):
                fig_dist = px.histogram(
                    df,
                    x=selected_num,
                    title=f"Distribution Profile: {selected_num}",
                    color_discrete_sequence=[theme_vars['primary']],
                )
                apply_plotly_theme(fig_dist)
                fig_dist.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_dist, use_container_width=True, key="hist_num")
                
        with chart_row2_c2:
            with st.container(border=True):
                fig_box = px.box(
                    df,
                    y=selected_num,
                    title=f"Outlier Box Plot: {selected_num}",
                    color_discrete_sequence=[theme_vars['accent']],
                )
                apply_plotly_theme(fig_box)
                fig_box.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_box, use_container_width=True, key="box_num")
    else:
        st.info("No numerical features found for distributions.")

    # 4. Categorical frequency Selector & Correlation Matrix
    st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 1.5rem; margin-bottom: 0.5rem;">Relationship & Cardinality Audits</p>', unsafe_allow_html=True)
    chart_row3_c1, chart_row3_c2 = st.columns(2)
    
    with chart_row3_c1:
        with st.container(border=True):
            categorical_cols = df.loc[:, ~df.isna().all()].select_dtypes(
                include=["object", "category", "bool"]
            ).columns.tolist()
            if categorical_cols:
                selected_cat = st.selectbox(
                    "Select Categorical Variable for Frequencies", categorical_cols, key="sel_cat_var"
                )
                counts = df[selected_cat].value_counts().reset_index()
                counts.columns = [selected_cat, "Frequency"]
                counts_top = counts.head(15)

                fig_freq = px.bar(
                    counts_top,
                    x="Frequency",
                    y=selected_cat,
                    orientation="h",
                    title=f"Top Categories: {selected_cat}",
                    color_discrete_sequence=[theme_vars['accent']],
                )
                apply_plotly_theme(fig_freq)
                fig_freq.update_layout(yaxis=dict(autorange="reversed"), height=340, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_freq, use_container_width=True, key="bar_freq")
            else:
                st.info("No categorical features found for frequencies.")
                
    with chart_row3_c2:
        with st.container(border=True):
            numeric_df = df.loc[:, ~df.isna().all()].select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 1:
                corr = numeric_df.corr()

                fig_heat = px.imshow(
                    corr,
                    x=corr.columns,
                    y=corr.columns,
                    color_continuous_scale=[
                        [0.0, theme_vars['primary']],
                        [0.5, theme_vars['bg']],
                        [1.0, theme_vars['accent']],
                    ],
                    aspect="auto",
                    title="Pearson Correlation Matrix Heatmap",
                )
                apply_plotly_theme(fig_heat)
                fig_heat.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_heat, use_container_width=True, key="heatmap_corr")
            elif len(numeric_df.columns) == 1:
                st.info("Correlation matrix requires at least two numerical columns. Only one numerical column detected.")
            else:
                st.info("No numerical columns found. Correlation analysis skipped.")

    # 5. Descriptive Summary Table
    if not profile["statistics"].empty:
        st.markdown('<h4 style="margin-top: 2rem; font-weight: 700; color: var(--text);">Descriptive Statistics</h4>', unsafe_allow_html=True)
        render_table_container(profile["statistics"], max_height_px=380, index=True)


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    try:
        with open("styles/theme.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    render()
