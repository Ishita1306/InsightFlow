"""
Dataset Explorer Component.

Provides a premium grid-based dataset explorer with search, sorting, pagination,
column visibility toggles, and formatted CSV export for filtered datasets.
"""

import math
import io
import pandas as pd
import numpy as np
import streamlit as st

from components.table_container import render_table_container
from components.glass_card import glass_card_panel


def render_dataset_explorer(df: pd.DataFrame) -> None:
    """
    Render the premium dataset explorer interface.
    
    Args:
        df (pd.DataFrame): Dataset to explore.
    """
    st.markdown('<h3 style="margin-top: 1.5rem; margin-bottom: 1.5rem; font-weight: 700;">Dataset Explorer</h3>', unsafe_allow_html=True)
    
    # Session state key initialization
    if "exp_page" not in st.session_state:
        st.session_state["exp_page"] = 0
        
    # Search and Control Panel inside glass card
    with glass_card_panel():
        col_search, col_sort_by, col_sort_order = st.columns([2, 1, 1])

        with col_search:
            search_query = st.text_input(
                "Search keywords",
                value="",
                placeholder="Search all columns...",
                help="Filters rows matching the search term (case-insensitive)."
            )
        with col_sort_by:
            sort_col = st.selectbox(
                "Sort by column",
                options=["[None]"] + df.columns.tolist(),
                index=0
            )
        with col_sort_order:
            sort_order = st.radio(
                "Sort direction",
                options=["Ascending", "Descending"],
                horizontal=True,
                disabled=(sort_col == "[None]")
            )

        col_vis, col_page_size = st.columns([3, 1])
        with col_vis:
            visible_cols = st.multiselect(
                "Columns to display",
                options=df.columns.tolist(),
                default=df.columns.tolist(),
                help="Select columns to show or hide in the grid view."
            )
        with col_page_size:
            page_size = st.selectbox(
                "Rows per page",
                options=[10, 25, 50, 100],
                index=0
            )
    
    # 1. Apply Search Filter (Case-insensitive across all columns)
    df_filtered = df
    if search_query:
        # Convert search query to lowercase and do substring matches
        # Handle different data types by converting columns to string first
        queries = search_query.lower().split()
        for q in queries:
            mask = np.column_stack([
                df_filtered[col].astype(str).str.lower().str.contains(q, na=False) 
                for col in df_filtered.columns
            ])
            df_filtered = df_filtered[mask.any(axis=1)]
            
    # Reset page index if filters/queries change to avoid index-out-of-bounds
    # We construct a hash/tuple of filter state to detect updates
    filter_state = (search_query, sort_col, sort_order, len(visible_cols), page_size)
    if "last_filter_state" not in st.session_state or st.session_state["last_filter_state"] != filter_state:
        st.session_state["exp_page"] = 0
        st.session_state["last_filter_state"] = filter_state
        
    # 2. Apply Sorting
    if sort_col != "[None]" and sort_col in df_filtered.columns:
        df_filtered = df_filtered.sort_values(
            by=sort_col, 
            ascending=(sort_order == "Ascending")
        )
        
    # 3. Apply Column Visibility
    if not visible_cols:
        st.warning("Please select at least one column to display.")
        return
        
    df_visible = df_filtered[visible_cols]
    
    # 4. Pagination math
    total_records = len(df_visible)
    total_pages = max(1, math.ceil(total_records / page_size))
    
    # Bind page boundary
    current_page = st.session_state["exp_page"]
    if current_page >= total_pages:
        current_page = total_pages - 1
    current_page = max(0, current_page)
    st.session_state["exp_page"] = current_page
    
    start_row = current_page * page_size
    end_row = min(start_row + page_size, total_records)
    
    # Slice rows for display
    page_df = df_visible.iloc[start_row:end_row]
    
    # Display table container
    if total_records > 0:
        render_table_container(page_df, max_height_px=450, index=False)
        
        # Pagination controls
        col_nav_prev, col_nav_info, col_nav_next = st.columns([1, 2, 1])
        with col_nav_prev:
            if st.button("Previous Page", disabled=(current_page == 0), width="stretch"):
                st.session_state["exp_page"] -= 1
                st.rerun()
        with col_nav_info:
            import textwrap
            st.markdown(
                textwrap.dedent(
                    f"""
                    <div style="text-align: center; color: var(--subtext); font-size: 0.88rem; padding-top: 0.4rem;">
                        Page <strong>{current_page + 1}</strong> of <strong>{total_pages}</strong> 
                        <span style="margin-left: 10px; color: rgba(255,255,255,0.35);">|</span> 
                        Showing {start_row + 1}-{end_row} of {total_records:,} rows
                    </div>
                    """
                ).strip(),
                unsafe_allow_html=True
            )
        with col_nav_next:
            if st.button("Next Page", disabled=(current_page >= total_pages - 1), width="stretch"):
                st.session_state["exp_page"] += 1
                st.rerun()
                
        # Export Actions Row
        st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
        csv_buffer = io.BytesIO()
        df_filtered.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label=f"Download Filtered Dataset ({total_records:,} rows)",
            data=csv_data,
            file_name="kosvio_filtered_dataset.csv",
            mime="text/csv",
            width="stretch",
            type="primary"
        )
    else:
        st.info("No rows match the specified search keywords.")
