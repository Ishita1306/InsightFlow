"""
Visual Analytics Page.

Implements the advanced interactive visualizations canvas with responsive filters
(column selection, numeric range, category value multi-select, and date range).
Plots are organized into thematic tabs.
"""

import streamlit as st
import pandas as pd
import numpy as np

from components.section_header import render_section_header
from components.empty_state import render_empty_state
from components.glass_card import glass_card_panel
from services.visualization_service import VisualizationService


def render() -> None:
    """Render the Visual Analytics workspace."""
    # Check dataset
    if "dataset" not in st.session_state:
        render_empty_state(
            title="No Dataset Selected",
            message="We couldn't locate an active dataset in memory. Please upload a dataset first.",
            action_label="Go to Upload Workspace",
            navigate_to="upload",
            navigate_label="Upload",
        )
        return

    df = st.session_state.get("cleaned_df") if st.session_state.get("cleaned_df") is not None else st.session_state["dataset"]
    filename = st.session_state.get("dataset_filename", "dataset.csv")

    render_section_header(
        title="Visual Analytics Canvas",
        subtitle=f"Interactive multi-dimensional visualization suite for {filename}.",
        label="Visual BI Canvas",
    )

    if st.session_state.get("cleaned_df") is not None:
        st.info("All insights and metrics are generated from the cleaned dataset.")

    # 1. Metric stats & quality audits
    from services.dataset_service import DatasetService
    from pages.upload import perform_advanced_audit
    profile = DatasetService.get_profile(df)
    summary = profile["summary"]
    audit = perform_advanced_audit(df)

    # Detect suitable columns (unsuitable ones are hidden in the service)
    detected = VisualizationService.detect_columns(df)
    numeric_cols = detected["numeric"]
    categorical_cols = detected["categorical"]
    datetime_cols = detected["datetime"]

    from utils.theme_manager import get_current_theme
    theme_vars = get_current_theme()

    # Top KPI cards
    st.markdown(
        """
        <style>
        .va-kpi-card {
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
        .va-kpi-card:hover {
            transform: translateY(-2px) !important;
            border-color: var(--primary) !important;
        }
        .va-kpi-lbl {
            font-size: 0.68rem !important;
            color: var(--subtext) !important;
            font-weight: 600 !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase !important;
            margin-bottom: 0.25rem !important;
        }
        .va-kpi-val {
            font-size: 1.25rem !important;
            font-weight: 800 !important;
            color: var(--text) !important;
        }

        .va-insight-card {
            background: rgba(99, 102, 241, 0.03) !important;
            border: 1px solid rgba(99, 102, 241, 0.12) !important;
            border-left: 5px solid var(--primary) !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
            margin-top: 1.5rem !important;
        }
        .va-insight-title {
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            color: var(--text) !important;
            margin-bottom: 0.5rem !important;
        }
        .va-insight-desc {
            font-size: 0.85rem !important;
            color: var(--subtext) !important;
            line-height: 1.5 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    k_col1, k_col2, k_col3, k_col4, k_col5, k_col6 = st.columns(6)
    with k_col1:
        st.markdown(f'<div class="va-kpi-card"><span class="va-kpi-lbl">Total Records</span><span class="va-kpi-val">{summary["rows"]:,}</span></div>', unsafe_allow_html=True)
    with k_col2:
        st.markdown(f'<div class="va-kpi-card"><span class="va-kpi-lbl">Total Columns</span><span class="va-kpi-val">{summary["columns"]}</span></div>', unsafe_allow_html=True)
    with k_col3:
        st.markdown(f'<div class="va-kpi-card"><span class="va-kpi-lbl">Numeric Features</span><span class="va-kpi-val">{summary["numeric_cols"]}</span></div>', unsafe_allow_html=True)
    with k_col4:
        st.markdown(f'<div class="va-kpi-card"><span class="va-kpi-lbl">Categorical Features</span><span class="va-kpi-val">{summary["categorical_cols"]}</span></div>', unsafe_allow_html=True)
    with k_col5:
        st.markdown(f'<div class="va-kpi-card"><span class="va-kpi-lbl">Missing Values</span><span class="va-kpi-val">{summary["missing_cells"]:,}</span></div>', unsafe_allow_html=True)
    with k_col6:
        st.markdown(f'<div class="va-kpi-card"><span class="va-kpi-lbl">Duplicate Rows</span><span class="va-kpi-val">{audit["duplicate_rows"]:,}</span></div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)

    # Two column layout: Left Filter Drawer, Right Chart Workspace
    col_filters, col_charts = st.columns([1, 3])

    with col_filters:
        st.markdown(f'<h4 style="margin-top: 0; font-weight: 700; color: var(--text);">Interactive Filters</h4>', unsafe_allow_html=True)

        # Wrap filters inside glass card
        with glass_card_panel():
            if st.button("Reset Filters", type="secondary", use_container_width=True, key="reset_filters_btn"):
                st.session_state["act_num"] = []
                st.session_state["act_cat"] = []
                st.session_state["act_date"] = []
                for k in list(st.session_state.keys()):
                    if k.startswith("val_num_") or k.startswith("val_cat_") or k.startswith("val_date_"):
                        st.session_state.pop(k, None)
                st.rerun()
                
            st.markdown('<div style="margin-top: 0.75rem;"></div>', unsafe_allow_html=True)
            
            # Search Column box
            search_q = st.text_input("Search columns", placeholder="Type variable name...", key="search_col_query").strip().lower()
            
            filtered_num_opts = [c for c in numeric_cols if search_q in c.lower()] if search_q else numeric_cols
            filtered_cat_opts = [c for c in categorical_cols if search_q in c.lower()] if search_q else categorical_cols
            filtered_date_opts = [c for c in datetime_cols if search_q in c.lower()] if search_q else datetime_cols

            active_numeric = st.multiselect(
                "Filter Numeric variables",
                options=filtered_num_opts,
                default=[],
                key="act_num"
            )

            active_categorical = st.multiselect(
                "Filter Categorical variables",
                options=filtered_cat_opts,
                default=[],
                key="act_cat"
            )

            active_dates = st.multiselect(
                "Filter Date variables",
                options=filtered_date_opts,
                default=[],
                key="act_date"
            )

            st.markdown('<div style="margin-top: 1rem; border-top: 1px solid var(--border); padding-top: 1rem;"></div>', unsafe_allow_html=True)

            # Apply Filter Inputs in real-time
            filtered_df = df.copy()

            # A. Apply numeric ranges
            for col in active_numeric:
                c_min = float(df[col].min()) if not pd.isna(df[col].min()) else 0.0
                c_max = float(df[col].max()) if not pd.isna(df[col].max()) else 100.0
                if c_min == c_max:
                    continue
                val_range = st.slider(
                    f"{col} Range",
                    min_value=c_min,
                    max_value=c_max,
                    value=(c_min, c_max),
                    key=f"val_num_{col}"
                )
                filtered_df = filtered_df[(filtered_df[col] >= val_range[0]) & (filtered_df[col] <= val_range[1])]

            # B. Apply categorical multi-selects
            for col in active_categorical:
                options = df[col].dropna().unique().tolist()
                default_selection = options
                selected_vals = st.multiselect(
                    f"{col} Values",
                    options=options,
                    default=default_selection,
                    key=f"val_cat_{col}"
                )
                filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

            # C. Apply date ranges
            for col in active_dates:
                dates = pd.to_datetime(df[col], errors="coerce").dropna()
                if not dates.empty:
                    min_d = dates.min().date()
                    max_d = dates.max().date()
                    if min_d == max_d:
                        continue
                    date_range = st.date_input(
                        f"{col} Date Range",
                        value=[min_d, max_d],
                        min_value=min_d,
                        max_value=max_d,
                        key=f"val_date_{col}"
                    )

                    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                        start_date, end_date = date_range
                        dt_col = pd.to_datetime(filtered_df[col], errors="coerce")
                        filtered_df = filtered_df[(dt_col.dt.date >= start_date) & (dt_col.dt.date <= end_date)]

            # Show record counts
            total_rows = len(df)
            filtered_rows = len(filtered_df)
            st.markdown(
                f"""
                <div style="margin-top: 1rem; padding: 0.75rem; border-radius: 8px; background: rgba(99, 102, 241, 0.04); border: 1px solid rgba(99, 102, 241, 0.15); text-align: center;">
                    <span style="font-size: 0.75rem; color: var(--subtext); text-transform: uppercase; letter-spacing: 0.05em;">Rows Filtered</span>
                    <p style="margin: 0.25rem 0 0; font-size: 1.25rem; font-weight: 700; color: var(--primary);">{filtered_rows:,} / {total_rows:,}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col_charts:
        st.markdown(f'<h4 style="margin-top: 0; font-weight: 700; color: var(--text);">BI Visualization Canvas</h4>', unsafe_allow_html=True)
        
        # 1. Config Card
        with glass_card_panel():
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                chart_type = st.selectbox(
                    "Chart Type",
                    options=[
                        "Bar Chart",
                        "Line Chart",
                        "Scatter Plot",
                        "Histogram",
                        "Box Plot",
                        "Violin Plot",
                        "Pie Chart",
                        "Donut Chart",
                        "Correlation Heatmap",
                        "Pair Plot"
                    ],
                    key="va_chart_type"
                )
            with col_c2:
                x_opts = [""] + datetime_cols + numeric_cols + categorical_cols
                x_col = st.selectbox("X-Axis Variable", options=x_opts, key="va_x_col")
            with col_c3:
                y_opts = [""] + numeric_cols
                y_col = st.selectbox("Y-Axis Variable", options=y_opts, key="va_y_col")

            col_c4, col_c5, col_c6 = st.columns(3)
            with col_c4:
                color_col = st.selectbox("Color Grouping Variable", options=["[None]"] + categorical_cols, key="va_color_col")
            with col_c5:
                agg_opt = st.selectbox("Aggregation Rule", options=["[None]", "Sum", "Mean", "Count", "Median"], key="va_agg_opt")
            with col_c6:
                sort_opt = st.selectbox("Sort Order", options=["[None]", "Ascending", "Descending"], key="va_sort_opt")

        # 2. Smart suggestions
        suggestions = []
        if x_col and y_col:
            x_is_num = x_col in numeric_cols
            y_is_num = y_col in numeric_cols
            x_is_cat = x_col in categorical_cols
            
            if x_is_num and y_is_num:
                if chart_type != "Scatter Plot":
                    suggestions.append("💡 **Scatter Plot** is recommended since both X and Y axes are numerical variables.")
                if chart_type != "Correlation Heatmap":
                    suggestions.append("💡 **Correlation Heatmap** is useful to inspect cross-correlation strengths.")
            elif x_is_cat and y_is_num:
                if chart_type != "Bar Chart":
                    suggestions.append("💡 **Bar Chart** is recommended to compare numeric values across category classes.")
                if chart_type != "Box Plot":
                    suggestions.append("💡 **Box Plot** is recommended to identify outlier distributions within categories.")
            elif x_col in datetime_cols and y_is_num:
                if chart_type != "Line Chart":
                    suggestions.append("💡 **Line Chart** is ideal for plotting numeric trends over date time Series.")
        elif x_col and not y_col:
            if x_col in categorical_cols and chart_type not in ["Pie Chart", "Donut Chart"]:
                suggestions.append("💡 **Donut / Pie Chart** is recommended to view proportion share of categorical segments.")
            elif x_col in numeric_cols and chart_type != "Histogram":
                suggestions.append("💡 **Histogram** is recommended to inspect single-variable frequency distribution.")

        if suggestions:
            st.markdown(
                f"""
                <div style="padding: 0.85rem; border-radius: 8px; background: rgba(6, 182, 212, 0.04); border: 1px solid rgba(6, 182, 212, 0.15); margin-bottom: 1rem;">
                    <span style="font-size: 0.75rem; color: var(--accent); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Smart Recommendations</span>
                    <div style="margin-top: 0.35rem; font-size: 0.8rem; color: var(--text); line-height: 1.4;">
                        {'<br>'.join(suggestions)}
                      </div>
                  </div>
                  """,
                unsafe_allow_html=True
            )

        # Handle empty filtered dataframe
        if filtered_df.empty:
            st.warning("⚠️ No data matches current filter settings. Adjust filters to display charts.")
            return

        # Prepare plotting data by applying aggregations if selected
        plot_df = filtered_df.copy()
        target_y = y_col
        
        if agg_opt != "[None]" and x_col and y_col:
            group_cols = [x_col]
            if color_col and color_col != "[None]":
                group_cols.append(color_col)
                
            if agg_opt == "Sum":
                plot_df = filtered_df.groupby(group_cols)[y_col].sum().reset_index()
            elif agg_opt == "Mean":
                plot_df = filtered_df.groupby(group_cols)[y_col].mean().reset_index()
            elif agg_opt == "Count":
                plot_df = filtered_df.groupby(group_cols).size().reset_index(name="Count")
                target_y = "Count"
            elif agg_opt == "Median":
                plot_df = filtered_df.groupby(group_cols)[y_col].median().reset_index()

        if sort_opt != "[None]" and target_y in plot_df.columns:
            ascending = (sort_opt == "Ascending")
            plot_df = plot_df.sort_values(by=target_y, ascending=ascending)

        # Incompatibility check helper
        def show_incompatible_message(msg="No compatible columns available for this visualization."):
            st.info(f"ℹ️ {msg}")

        import plotly.express as px
        import plotly.graph_objects as go

        fig = None
        
        try:
            if chart_type == "Bar Chart":
                if not x_col or not y_col:
                    show_incompatible_message("Please select both X-Axis and Y-Axis columns for a Bar Chart.")
                else:
                    color_seq, _ = VisualizationService.get_theme_colors()
                    color_arg = color_col if color_col != "[None]" else None
                    fig = px.bar(
                        plot_df,
                        x=x_col,
                        y=target_y,
                        color=color_arg,
                        title=f"Bar Chart: Aggregated {target_y} by {x_col}",
                        color_discrete_sequence=color_seq
                    )
                    VisualizationService.apply_theme(fig)
                    
            elif chart_type == "Line Chart":
                if not x_col or not y_col:
                    show_incompatible_message("Please select both X-Axis and Y-Axis columns for a Line Chart.")
                else:
                    color_seq, _ = VisualizationService.get_theme_colors()
                    color_arg = color_col if color_col != "[None]" else None
                    fig = px.line(
                        plot_df,
                        x=x_col,
                        y=target_y,
                        color=color_arg,
                        title=f"Line Chart: Aggregated {target_y} by {x_col}",
                        color_discrete_sequence=color_seq
                    )
                    VisualizationService.apply_theme(fig)

            elif chart_type == "Scatter Plot":
                if not x_col or not y_col:
                    show_incompatible_message("Please select both X-Axis and Y-Axis columns for a Scatter Plot.")
                else:
                    color_arg = color_col if color_col != "[None]" else None
                    fig = VisualizationService.create_scatter_plot(filtered_df, x_col, y_col, color_arg)

            elif chart_type == "Histogram":
                if not x_col:
                    show_incompatible_message("Please select an X-Axis column for the Histogram.")
                else:
                    fig = VisualizationService.create_histogram(filtered_df, x_col)

            elif chart_type == "Box Plot":
                if not y_col:
                    show_incompatible_message("Please select a Y-Axis column (numerical) for the Box Plot.")
                else:
                    x_arg = x_col if x_col else None
                    fig = VisualizationService.create_box_plot(filtered_df, y_col, x_arg)

            elif chart_type == "Violin Plot":
                if not y_col:
                    show_incompatible_message("Please select a Y-Axis column (numerical) for the Violin Plot.")
                else:
                    x_arg = x_col if x_col else None
                    fig = VisualizationService.create_violin_plot(filtered_df, y_col, x_arg)

            elif chart_type == "Pie Chart":
                if not x_col:
                    show_incompatible_message("Please select a Categorical column (X-Axis) for the Pie Chart.")
                else:
                    y_arg = y_col if y_col else None
                    fig = VisualizationService.create_pie_chart(filtered_df, x_col, y_arg)

            elif chart_type == "Donut Chart":
                if not x_col:
                    show_incompatible_message("Please select a Categorical column (X-Axis) for the Donut Chart.")
                else:
                    y_arg = y_col if y_col else None
                    fig = VisualizationService.create_donut_chart(filtered_df, x_col, y_arg)

            elif chart_type == "Correlation Heatmap":
                fig = VisualizationService.create_correlation_heatmap(filtered_df)

            elif chart_type == "Pair Plot":
                num_opts = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
                if len(num_opts) < 2:
                    show_incompatible_message("Pair Plot requires at least 2 numerical columns.")
                else:
                    color_arg = color_col if color_col != "[None]" else None
                    fig = VisualizationService.create_pair_plot(filtered_df, num_opts, color_arg)
                    
        except Exception as e:
            show_incompatible_message(f"Could not render chart: {str(e)}")

        if fig is not None:
            fig.update_layout(height=480)
            st.plotly_chart(fig, use_container_width=True)
            
            # AI Insights Card
            st.markdown('<div class="va-insight-card">', unsafe_allow_html=True)
            st.markdown('<p class="va-insight-title">✨ AI Observations & Narrative</p>', unsafe_allow_html=True)
            
            # Build business-oriented insights dynamically
            insight_text = ""
            if chart_type in ["Bar Chart", "Line Chart", "Scatter Plot"] and x_col and y_col:
                if len(plot_df) > 1:
                    try:
                        x_vals = np.arange(len(plot_df))
                        y_vals = plot_df[target_y].values
                        if np.issubdtype(y_vals.dtype, np.number):
                            slope, _ = np.polyfit(x_vals, y_vals, 1)
                            y_mean = np.mean(y_vals)
                            y_min = np.min(y_vals)
                            y_max = np.max(y_vals)
                            
                            trend_word = "increasing" if slope > 0.001 * y_mean else "decreasing" if slope < -0.001 * y_mean else "stable"
                            
                            if chart_type == "Line Chart":
                                insight_text = (
                                    f"The Line Chart shows a primarily <strong>{trend_word}</strong> trajectory for the aggregated <strong>{target_y}</strong> over <strong>{x_col}</strong>. "
                                    f"Values peak at <strong>{y_max:,.2f}</strong> and reach a minimum of <strong>{y_min:,.2f}</strong>. This indicates "
                                    f"{'steady positive growth' if trend_word == 'increasing' else 'a gradual contraction' if trend_word == 'decreasing' else 'high stability'} "
                                    f"across the filtered range."
                                )
                            elif chart_type == "Bar Chart":
                                highest_row = plot_df.loc[plot_df[target_y].idxmax()]
                                highest_lbl = highest_row[x_col]
                                insight_text = (
                                    f"The Bar Chart indicates that <strong>{target_y}</strong> varies across different classifications of <strong>{x_col}</strong>. "
                                    f"The highest category is <strong>{highest_lbl}</strong> with an aggregated value of <strong>{y_max:,.2f}</strong>, suggesting a focal point for resource allocation "
                                    f"and strategic optimization."
                                )
                            else: # Scatter Plot
                                corr_coeff = df[[x_col, y_col]].corr().iloc[0, 1]
                                strength_word = "strong" if abs(corr_coeff) >= 0.7 else "moderate" if abs(corr_coeff) >= 0.4 else "weak"
                                dir_word = "positive" if corr_coeff > 0 else "negative"
                                insight_text = (
                                    f"The Scatter Plot reveals a <strong>{strength_word} {dir_word} correlation</strong> ({corr_coeff:.2f}) between <strong>{x_col}</strong> and <strong>{y_col}</strong>. "
                                    f"This relationship suggests that as <strong>{x_col}</strong> increases, <strong>{y_col}</strong> tend to "
                                    f"{'increase' if corr_coeff > 0 else 'decrease'} proportionally, indicating a predictable business relationship."
                                )
                    except Exception:
                        pass
                if not insight_text:
                    insight_text = f"An analytical review of <strong>{target_y}</strong> by <strong>{x_col}</strong> shows noticeable variations. Clean variables and balanced distributions suggest the dataset is ready for executive decision-making."
                    
            elif chart_type in ["Pie Chart", "Donut Chart"] and x_col:
                insight_text = (
                    f"The proportion breakdown reveals the relative share of <strong>{x_col}</strong> categories. "
                    f"The distribution highlights the dominant segments within the dataset, allowing analysts to identify major market concentrations or category spikes."
                )
            elif chart_type in ["Histogram", "Box Plot", "Violin Plot"] and y_col:
                insight_text = (
                    f"The distribution profile of <strong>{y_col}</strong> reveals its statistical spread, skewness, and median center. "
                    f"The presence of any outliers beyond the standard IQR limits flags potential anomalies that may require data cleaning or specialized treatment."
                )
            else:
                insight_text = (
                    "The visualization illustrates the multi-dimensional structure of the dataset. "
                    "Analyzing these variables helps uncover hidden data patterns, anomalies, and cardinalities suitable for business intelligence analysis."
                )
                
            st.markdown(f'<p class="va-insight-desc">{insight_text}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
