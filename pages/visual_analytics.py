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
from components.glass_card import glass_card_wrapper_start, glass_card_wrapper_end
from services.visualization_service import VisualizationService


def render() -> None:
    """Render the Visual Analytics workspace."""
    # Check dataset
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
        title="Visual Analytics Canvas",
        subtitle=f"Interactive multi-dimensional visualization suite for {filename}.",
        label="Visual BI Canvas",
    )

    # Detect suitable columns
    detected = VisualizationService.detect_columns(df)
    numeric_cols = detected["numeric"]
    categorical_cols = detected["categorical"]
    datetime_cols = detected["datetime"]

    # Two column layout: Left Filter Drawer, Right Chart Workspace
    col_filters, col_charts = st.columns([1, 3])

    with col_filters:
        st.markdown('<h4 style="margin-top: 0; font-weight: 700; color: #FAFAFA;">Interactive Filters</h4>', unsafe_allow_html=True)
        
        # Wrap filters inside glass card
        glass_card_wrapper_start()
        
        # Choose which columns to activate filters for
        st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--subtext); margin-bottom: 0.5rem;">Select Filters to Apply</p>', unsafe_allow_html=True)
        
        active_numeric = st.multiselect(
            "Numeric variables",
            options=numeric_cols,
            default=numeric_cols[:1] if numeric_cols else [],
            key="act_num"
        )
        
        active_categorical = st.multiselect(
            "Categorical variables",
            options=categorical_cols,
            default=categorical_cols[:1] if categorical_cols else [],
            key="act_cat"
        )
        
        active_dates = st.multiselect(
            "Date variables",
            options=datetime_cols,
            default=datetime_cols[:1] if datetime_cols else [],
            key="act_date"
        )
        
        st.markdown('<div style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1rem;"></div>', unsafe_allow_html=True)
        
        # 1. Build Filter Inputs and Apply in real-time
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
            # To keep lists manageable, default select top 10 if there are many
            default_selection = options[:10] if len(options) > 10 else options
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
                # Ensure start and end are unique
                if min_d == max_d:
                    continue
                date_range = st.date_input(
                    f"{col} Date Range",
                    value=[min_d, max_d],
                    min_value=min_d,
                    max_value=max_d,
                    key=f"val_date_{col}"
                )
                
                # Check for full range selection
                if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                    start_date, end_date = date_range
                    dt_col = pd.to_datetime(filtered_df[col], errors="coerce")
                    filtered_df = filtered_df[(dt_col.dt.date >= start_date) & (dt_col.dt.date <= end_date)]

        # Show record counts
        total_rows = len(df)
        filtered_rows = len(filtered_df)
        st.markdown(
            f"""
            <div style="margin-top: 1rem; padding: 0.75rem; border-radius: 8px; background: rgba(34, 211, 238, 0.04); border: 1px solid rgba(34, 211, 238, 0.12); text-align: center;">
                <span style="font-size: 0.75rem; color: var(--subtext); text-transform: uppercase; letter-spacing: 0.05em;">Rows Filtered</span>
                <p style="margin: 0.25rem 0 0; font-size: 1.25rem; font-weight: 700; color: var(--accent);">{filtered_rows:,} / {total_rows:,}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        glass_card_wrapper_end()

    with col_charts:
        st.markdown('<h4 style="margin-top: 0; font-weight: 700; color: #FAFAFA;">Visualization Canvas</h4>', unsafe_allow_html=True)
        
        # Handle empty filtered dataframe
        if filtered_df.empty:
            st.warning("No data matches current filter settings. Adjust filters to display charts.")
            return

        # Organize charts into beautiful tabs
        tab_corr, tab_dist, tab_relation, tab_prop, tab_hierarchy = st.columns(5)
        
        # Tabs navigation selection using st.tabs for native Streamlit styling but premium container wrapping
        tab_list = st.tabs([
            "Correlation & Heatmaps", 
            "Variable Distributions", 
            "Numeric Relationships", 
            "Pie & Proportion Breakdown", 
            "Hierarchical Treemaps"
        ])
        
        # ── TAB 1: CORRELATION & HEATMAPS ────────────────────────────────────
        with tab_list[0]:
            st.markdown("<h5>Correlation & Multivariates</h5>", unsafe_allow_html=True)
            
            # Correlation matrix
            num_cols = len(filtered_df.select_dtypes(include=[np.number]).columns)
            if num_cols >= 2:
                fig_heat = VisualizationService.create_correlation_heatmap(filtered_df)
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.info("Correlation Matrix requires at least 2 numerical columns.")
                
            # Pair Plot (Scatter matrix)
            st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
            st.markdown("<h5>Pair Plot (Scatter Matrix)</h5>", unsafe_allow_html=True)
            
            numeric_options = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_options) >= 2:
                col_sm1, col_sm2 = st.columns([3, 1])
                with col_sm1:
                    pair_cols = st.multiselect(
                        "Columns for Pair Plot (max 4)",
                        options=numeric_options,
                        default=numeric_options[:3]
                    )
                with col_sm2:
                    pair_color = st.selectbox(
                        "Color code variable",
                        options=["[None]"] + categorical_cols,
                        index=0
                    )
                
                if len(pair_cols) >= 2:
                    color_col = None if pair_color == "[None]" else pair_color
                    fig_pair = VisualizationService.create_pair_plot(filtered_df, pair_cols, color_col)
                    st.plotly_chart(fig_pair, use_container_width=True)
                else:
                    st.info("Select at least 2 columns to plot scatter matrix.")
            else:
                st.info("Pair Plot requires at least 2 numerical columns.")

        # ── TAB 2: VARIABLE DISTRIBUTIONS ────────────────────────────────────
        with tab_list[1]:
            st.markdown("<h5>Continuous Variable Distributions</h5>", unsafe_allow_html=True)
            
            if numeric_cols:
                col_dist1, col_dist2 = st.columns(2)
                with col_dist1:
                    dist_target = st.selectbox(
                        "Target distribution variable",
                        options=numeric_cols,
                        key="dist_tgt"
                    )
                with col_dist2:
                    dist_group = st.selectbox(
                        "Group by categorical variable (optional)",
                        options=["[None]"] + categorical_cols,
                        key="dist_grp"
                    )
                
                group_col = None if dist_group == "[None]" else dist_group
                
                # Render Histogram
                fig_hist = VisualizationService.create_histogram(filtered_df, dist_target)
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # Render Box & Violin Plot side-by-side
                st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
                col_box, col_violin = st.columns(2)
                with col_box:
                    fig_box = VisualizationService.create_box_plot(filtered_df, dist_target, group_col)
                    st.plotly_chart(fig_box, use_container_width=True)
                with col_violin:
                    fig_violin = VisualizationService.create_violin_plot(filtered_df, dist_target, group_col)
                    st.plotly_chart(fig_violin, use_container_width=True)
            else:
                st.info("No numerical features found for distribution plotting.")

        # ── TAB 3: NUMERIC RELATIONSHIPS ─────────────────────────────────────
        with tab_list[2]:
            st.markdown("<h5>Numeric Trend & Relationship analysis</h5>", unsafe_allow_html=True)
            
            if len(numeric_cols) >= 1:
                # Build X axis options: could be Datetime or Numeric or Categorical
                x_options = datetime_cols + numeric_cols + categorical_cols
                
                col_rel1, col_rel2, col_rel3 = st.columns(3)
                with col_rel1:
                    x_col = st.selectbox("X-Axis Variable", options=x_options, key="rel_x")
                with col_rel2:
                    # Filter target to other numeric columns if X is numeric
                    y_options = [c for c in numeric_cols if c != x_col] if x_col in numeric_cols else numeric_cols
                    y_col = st.selectbox("Y-Axis Variable", options=y_options if y_options else numeric_cols, key="rel_y")
                with col_rel3:
                    group_opt = st.selectbox("Color Legend Grouping", options=["[None]"] + categorical_cols, key="rel_grp")
                    
                color_group = None if group_opt == "[None]" else group_opt
                
                if x_col and y_col:
                    fig_scatter = VisualizationService.create_scatter_plot(filtered_df, x_col, y_col, color_group)
                    st.plotly_chart(fig_scatter, use_container_width=True)
                    
                    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
                    col_line, col_area = st.columns(2)
                    with col_line:
                        fig_line = VisualizationService.create_line_chart(filtered_df, x_col, y_col, color_group)
                        st.plotly_chart(fig_line, use_container_width=True)
                    with col_area:
                        fig_area = VisualizationService.create_area_chart(filtered_df, x_col, y_col, color_group)
                        st.plotly_chart(fig_area, use_container_width=True)
            else:
                st.info("Continuous relationships require at least 1 numerical column.")

        # ── TAB 4: PIE & PROPORTION BREAKDOWN ────────────────────────────────
        with tab_list[3]:
            st.markdown("<h5>Pie & Proportion Breakdown</h5>", unsafe_allow_html=True)
            
            if categorical_cols:
                col_prop1, col_prop2 = st.columns(2)
                with col_prop1:
                    prop_cat = st.selectbox("Categorical label column", options=categorical_cols, key="prop_cat")
                with col_prop2:
                    prop_val = st.selectbox("Value column (summed, optional)", options=["[Record Count]"] + numeric_cols, key="prop_val")
                
                values_col = None if prop_val == "[Record Count]" else prop_val
                
                col_pie, col_donut = st.columns(2)
                with col_pie:
                    fig_pie = VisualizationService.create_pie_chart(filtered_df, prop_cat, values_col)
                    st.plotly_chart(fig_pie, use_container_width=True)
                with col_donut:
                    fig_donut = VisualizationService.create_donut_chart(filtered_df, prop_cat, values_col)
                    st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("Proportion charts require at least 1 categorical column.")

        # ── TAB 5: HIERARCHICAL TREEMAPS ─────────────────────────────────────
        with tab_list[4]:
            st.markdown("<h5>Hierarchical Treemap & Sunburst Visualizations</h5>", unsafe_allow_html=True)
            
            if len(categorical_cols) >= 1:
                col_hier1, col_hier2 = st.columns([3, 1])
                with col_hier1:
                    hier_paths = st.multiselect(
                        "Define Hierarchy Path (e.g. Category > Subcategory)",
                        options=categorical_cols,
                        default=categorical_cols[:2] if len(categorical_cols) >= 2 else categorical_cols[:1]
                    )
                with col_hier2:
                    hier_val = st.selectbox(
                        "Hierarchy metric values (optional)",
                        options=["[Record Count]"] + numeric_cols,
                        key="hier_val"
                    )
                
                values_col = None if hier_val == "[Record Count]" else hier_val
                
                if hier_paths:
                    fig_treemap = VisualizationService.create_treemap(filtered_df, hier_paths, values_col)
                    st.plotly_chart(fig_treemap, use_container_width=True)
                    
                    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
                    fig_sunburst = VisualizationService.create_sunburst(filtered_df, hier_paths, values_col)
                    st.plotly_chart(fig_sunburst, use_container_width=True)
                else:
                    st.info("Select at least 1 categorical column for hierarchy paths.")
            else:
                st.info("Hierarchical charts require at least 1 categorical column.")
