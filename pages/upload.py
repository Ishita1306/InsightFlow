"""
Dataset upload page workspace.

Provides interactive controls to upload CSV and Excel (XLSX) datasets, profiles
them, and displays KPI cards and summaries matching the premium dark theme.
"""

import io
import streamlit as st
import pandas as pd
import numpy as np

from components.section_header import render_section_header
from components.empty_state import render_empty_state
from components.metric_card import render_metric_card
from components.table_container import render_table_container
from components.glass_card import glass_card_panel
from services.dataset_service import DatasetService


def format_memory_size(bytes_size: int) -> str:
    """Format size in bytes to a human-readable string."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"


def calculate_health_score(df: pd.DataFrame) -> float:
    """Calculate a normalized dataset health score from 0 to 100."""
    if df.empty:
        return 0.0
    
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0.0
    
    duplicate_rows = df.duplicated().sum()
    dup_pct = (duplicate_rows / len(df) * 100) if len(df) > 0 else 0.0
    
    empty_cols = [col for col in df.columns if df[col].isna().all()]
    empty_pct = (len(empty_cols) / len(df.columns) * 100) if len(df.columns) > 0 else 0.0
    
    inferred_types = DatasetService.auto_detect_datatypes(df)
    incorrect_count = 0
    for col in df.columns:
        curr_type = str(df[col].dtype)
        inf_type = inferred_types.get(col)
        
        is_incorrect = False
        if inf_type == "datetime64[ns]" and not curr_type.startswith("datetime"):
            is_incorrect = True
        elif inf_type == "category" and curr_type not in ["category", "bool"]:
            is_incorrect = True
        elif inf_type == "int64" and not (curr_type.startswith("int") or curr_type.startswith("UInt")):
            is_incorrect = True
        elif inf_type == "float64" and not curr_type.startswith("float"):
            is_incorrect = True
            
        if is_incorrect:
            incorrect_count += 1
            
    dtype_pct = (incorrect_count / len(df.columns) * 100) if len(df.columns) > 0 else 0.0
    
    score = 100.0
    score -= missing_pct * 0.5  # up to 50 pts penalty
    score -= dup_pct * 0.3      # up to 30 pts penalty
    score -= empty_pct * 0.4    # up to 40 pts penalty
    score -= dtype_pct * 0.2    # up to 20 pts penalty
    
    return max(0.0, min(100.0, score))


def render() -> None:
    """Render the upload workspace."""
    render_section_header(
        title="Upload Dataset",
        subtitle="Import your CSV or Excel spreadsheets to profile, clean, and analyze your business data.",
        label="Data Workspace",
    )

    # Initialize recent uploads storage
    if "recent_uploads" not in st.session_state:
        st.session_state["recent_uploads"] = []

    # Two column layout before file is uploaded, single column after
    has_dataset = "dataset" in st.session_state
    
    if not has_dataset:
        upload_col, history_col = st.columns([5, 3])
    else:
        upload_col = st.container()
        history_col = None

    with upload_col:
        # File uploader workspace styled inside a card
        with st.container(border=True):
            uploaded_file = st.file_uploader(
                "Choose a data file",
                type=["csv", "xlsx", "xls"],
                help="Supported formats: CSV, Excel (.xlsx, .xls). File size limits up to 200MB.",
                label_visibility="collapsed",
            )

    if history_col:
        with history_col:
            st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 0;">Recent Uploads</p>', unsafe_allow_html=True)
            if st.session_state["recent_uploads"]:
                for index, item in enumerate(st.session_state["recent_uploads"]):
                    st.markdown(
                        f"""
                        <div class="glass-card" style="padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <p style="margin: 0; font-size: 0.85rem; font-weight: 500; color: var(--text);">{item['filename']}</p>
                                <p style="margin: 0; font-size: 0.75rem; color: var(--subtext);">{item['rows']:,} rows &bull; {item['cols']} cols</p>
                            </div>
                            <span style="font-size: 0.72rem; color: var(--subtext);">{item['time']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<p style="font-size: 0.8rem; color: var(--subtext); font-style: italic;">No recent uploads in this session.</p>', unsafe_allow_html=True)

    # Process upload if file is provided
    if uploaded_file is not None:
        if (
            "dataset" not in st.session_state 
            or st.session_state.get("dataset_filename") != uploaded_file.name
            or st.session_state.get("uploaded_file_id") != id(uploaded_file)
        ):
            try:
                # 1. Validation: check empty file
                if uploaded_file.size == 0:
                    raise ValueError("The uploaded file is empty (0 bytes).")
                
                # 2. Premium simulated progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                stages = [
                    (20, "Reading raw file bytes..."),
                    (50, "Parsing tabular structure..."),
                    (75, "Validating column headers..."),
                    (95, "Running data profiling audits..."),
                    (100, "Finalizing Kosvio session state...")
                ]
                
                for pct, msg in stages:
                    import time
                    status_text.markdown(f'<span style="font-size: 0.85rem; color: var(--subtext);">{msg}</span>', unsafe_allow_html=True)
                    time.sleep(0.08)
                    progress_bar.progress(pct)
                
                progress_bar.empty()
                status_text.empty()

                # Read file buffer and save DataFrame to state
                df = DatasetService.load_and_validate(
                    uploaded_file, uploaded_file.name
                )
                
                # 3. Validation: check empty rows/cols
                if df.empty:
                    raise ValueError("The parsed dataset contains no rows of data.")
                if len(df.columns) == 0:
                    raise ValueError("No columns could be detected in this dataset.")

                st.session_state["dataset"] = df
                st.session_state["original_df"] = df.copy()
                st.session_state["dataset_filename"] = uploaded_file.name
                st.session_state["uploaded_file_id"] = id(uploaded_file)
                st.session_state.pop("cleaned_df", None)
                st.session_state.pop("cleaning_summary", None)
                st.session_state.pop("just_cleaned", None)
                
                # Append to recent uploads history
                import datetime
                recent_entry = {
                    "filename": uploaded_file.name,
                    "rows": len(df),
                    "cols": len(df.columns),
                    "time": datetime.datetime.now().strftime("%I:%M %p")
                }
                if uploaded_file.name not in [u["filename"] for u in st.session_state["recent_uploads"]]:
                    st.session_state["recent_uploads"].append(recent_entry)
                
                st.rerun()
            except Exception as e:
                # Reset state on failure to ensure clean error state
                st.session_state.pop("dataset", None)
                st.session_state.pop("dataset_filename", None)
                st.session_state.pop("uploaded_file_id", None)
                st.markdown(
                    f"""
                    <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                        <h4 style="margin: 0 0 0.25rem; color: #EF4444; font-size: 0.95rem; font-weight: 600;">Invalid Dataset File</h4>
                        <p style="margin: 0; color: var(--subtext); font-size: 0.82rem;">{str(e)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Retrieve dataset from session state
    if "dataset" in st.session_state:
        df = st.session_state["dataset"]
        if "original_df" not in st.session_state:
            st.session_state["original_df"] = df.copy()
        filename = st.session_state.get("dataset_filename", "dataset.csv")

        # Get profile stats
        profile = DatasetService.get_profile(df)
        summary = profile["summary"]

        # Premium Animated Success Banner
        st.markdown(
            f"""
            <style>
            @keyframes slideIn {{
                from {{ transform: translateY(-8px); opacity: 0; }}
                to {{ transform: translateY(0); opacity: 1; }}
            }}
            .success-banner {{
                animation: slideIn 0.2s ease-out forwards;
                background: rgba(16, 185, 129, 0.08) !important;
                border: 1px solid rgba(16, 185, 129, 0.2) !important;
                border-radius: 8px;
                padding: 0.85rem 1rem;
                margin-top: 1rem;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }}
            </style>
            <div class="success-banner">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: #10B981; display: flex; align-items: center; justify-content: center;">
                    <svg viewBox="0 0 24 24" style="width: 14px; height: 14px; stroke: #fff; stroke-width: 3; fill: none;"><polyline points="20 6 9 17 4 12"/></svg>
                </div>
                <div>
                    <h4 style="margin: 0; color: #10B981; font-weight: 600; font-size: 0.9rem;">Dataset Successfully Loaded</h4>
                    <p style="margin: 0; color: var(--subtext); font-size: 0.78rem;">Profiled and indexed for active workspace models.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Metrics section (6 columns grid)
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            render_metric_card(
                value=f"{summary['rows']:,}",
                label="Rows",
                detail="Total data samples",
                icon_svg='<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/></svg>',
            )
        with col2:
            render_metric_card(
                value=str(summary["columns"]),
                label="Columns",
                detail="Total variables",
                icon_svg='<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="21" y1="12" x2="3" y2="12"/><line x1="12" y1="3" x2="12" y2="21"/></svg>',
            )
        with col3:
            # Color trend positive/negative based on missing values presence
            missing_val = summary["missing_cells"]
            missing_pct = summary["missing_pct"]
            render_metric_card(
                value=f"{missing_val:,}",
                label="Missing",
                detail=f"{missing_pct:.1f}% of total dataset",
                trend=f"{missing_pct:.1f}%",
                trend_positive=(missing_val == 0),
                icon_svg='<svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
            )
        with col4:
            dups = summary["duplicate_rows"]
            render_metric_card(
                value=f"{dups:,}",
                label="Duplicates",
                detail="Redundant rows",
                trend=str(dups),
                trend_positive=(dups == 0),
                icon_svg='<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
            )
        with col5:
            # Format dataset size (in-memory footprint)
            formatted_mem = format_memory_size(summary["memory_bytes"])
            render_metric_card(
                value=formatted_mem,
                label="Dataset Size",
                detail="Raw dataset footprint",
                icon_svg='<svg viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l-7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.73z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
            )
        with col6:
            # Memory usage formatted
            mem_mb = profile["memory_usage_mb"]
            render_metric_card(
                value=f"{mem_mb:.2f} MB",
                label="Memory Usage",
                detail="System active RAM",
                icon_svg='<svg viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>',
            )

        # Data Quality Report
def perform_advanced_audit(df: pd.DataFrame) -> dict:
    """Run comprehensive audits on dataset abnormalities."""
    if df.empty:
        return {
            "missing_cells": 0, "missing_pct": 0.0, "duplicate_rows": 0,
            "empty_cols": [], "incorrect_cols": [], "outliers_count": 0,
            "outlier_cols": {}, "constant_cols": [], "high_card_cols": [], "invalid_date_cols": {}
        }
    
    # 1. Missing Values
    missing_cells = int(df.isnull().sum().sum())
    missing_pct = (missing_cells / df.size * 100) if df.size > 0 else 0.0
    
    # 2. Duplicate Rows
    duplicate_rows = int(df.duplicated().sum())
    
    # 3. Empty Columns
    empty_cols = [col for col in df.columns if df[col].isna().all()]
    
    # 4. Incorrect Datatypes
    inferred_types = DatasetService.auto_detect_datatypes(df)
    incorrect_cols = []
    for col in df.columns:
        curr_type = str(df[col].dtype)
        inf_type = inferred_types.get(col)
        is_incorrect = False
        if inf_type == "datetime64[ns]" and not curr_type.startswith("datetime"):
            is_incorrect = True
        elif inf_type == "category" and curr_type not in ["category", "bool"]:
            is_incorrect = True
        elif inf_type == "int64" and not (curr_type.startswith("int") or curr_type.startswith("UInt")):
            is_incorrect = True
        elif inf_type == "float64" and not curr_type.startswith("float"):
            is_incorrect = True
        if is_incorrect:
            incorrect_cols.append((col, curr_type, inf_type))
            
    # 5. Outliers (using IQR method)
    outliers_count = 0
    outlier_cols = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        # Ignore completely null numeric columns
        if df[col].notna().sum() > 3:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                mask = (df[col] < lower) | (df[col] > upper)
                cnt = int(mask.sum())
                if cnt > 0:
                    outlier_cols[col] = cnt
                    outliers_count += cnt
                    
    # 6. Constant Columns
    constant_cols = [col for col in df.columns if df[col].nunique() == 1 and df[col].notna().any()]
    
    # 7. High Cardinality (unique ratio > 90% for categorical)
    high_card_cols = []
    n_rows = len(df)
    for col in df.select_dtypes(include=["object", "category"]).columns:
        col_lower = col.lower()
        # Avoid flagging date columns as high cardinality
        is_date_col = any(kw in col_lower for kw in ["date", "time", "year", "created", "updated", "joining", "order", "timestamp"])
        if is_date_col:
            continue
            
        if n_rows > 10:
            uniq_cnt = df[col].nunique()
            if uniq_cnt / n_rows > 0.9:
                high_card_cols.append(col)
                
    # 8. Invalid Dates (where field name suggests a date but has failed parses)
    invalid_date_cols = {}
    for col in df.select_dtypes(include=["object"]).columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in ["date", "time", "year", "created", "updated", "joining", "order", "timestamp"]):
            # Ignore completely empty columns
            if df[col].notna().any():
                # Count coerced failures
                parsed = pd.to_datetime(df[col], errors="coerce")
                orig_nulls = int(df[col].isnull().sum())
                parsed_nulls = int(parsed.isnull().sum())
                invalid_cnt = parsed_nulls - orig_nulls
                if invalid_cnt > 0:
                    invalid_date_cols[col] = invalid_cnt
                    
    return {
        "missing_cells": missing_cells,
        "missing_pct": missing_pct,
        "duplicate_rows": duplicate_rows,
        "empty_cols": empty_cols,
        "incorrect_cols": incorrect_cols,
        "outliers_count": outliers_count,
        "outlier_cols": outlier_cols,
        "constant_cols": constant_cols,
        "high_card_cols": high_card_cols,
        "invalid_date_cols": invalid_date_cols,
    }


def calculate_health_score(df: pd.DataFrame) -> float:
    """Calculate a normalized dataset health score from 0 to 100 based on advanced audits."""
    if df.empty:
        return 0.0
    audit = perform_advanced_audit(df)
    
    score = 100.0
    score -= min(25.0, audit["missing_pct"] * 0.5)
    
    dup_pct = (audit["duplicate_rows"] / len(df) * 100) if len(df) > 0 else 0.0
    score -= min(15.0, dup_pct * 0.3)
    
    empty_pct = (len(audit["empty_cols"]) / len(df.columns) * 100) if len(df.columns) > 0 else 0.0
    score -= min(15.0, empty_pct * 0.4)
    
    dtype_pct = (len(audit["incorrect_cols"]) / len(df.columns) * 100) if len(df.columns) > 0 else 0.0
    score -= min(15.0, dtype_pct * 0.3)
    
    outlier_pct = (audit["outliers_count"] / df.size * 100) if df.size > 0 else 0.0
    score -= min(10.0, outlier_pct * 0.5)
    
    const_pct = (len(audit["constant_cols"]) / len(df.columns) * 100) if len(df.columns) > 0 else 0.0
    score -= min(10.0, const_pct * 1.0)
    
    card_pct = (len(audit["high_card_cols"]) / len(df.columns) * 100) if len(df.columns) > 0 else 0.0
    score -= min(5.0, card_pct * 0.5)
    
    invalid_dates_count = sum(audit["invalid_date_cols"].values())
    invalid_date_pct = (invalid_dates_count / len(df) * 100) if len(df) > 0 else 0.0
    score -= min(5.0, invalid_date_pct * 0.5)
    
    return max(0.0, min(100.0, score))


def render() -> None:
    """Render the upload workspace."""
    render_section_header(
        title="Upload Dataset",
        subtitle="Import your CSV or Excel spreadsheets to profile, clean, and analyze your business data.",
        label="Data Workspace",
    )

    # Privacy Notice
    st.markdown(
        """
        <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 8px; padding: 0.85rem 1rem; margin-bottom: 1.5rem;">
            <p style="margin: 0; font-size: 0.82rem; color: var(--text); line-height: 1.5;">
                🔒 <strong>Privacy Notice</strong>: Your uploaded datasets are processed only during your current session. 
                Kosvio does not permanently store, share, or transmit your files. 
                All uploaded data is removed when your session ends or you clear the workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Initialize recent uploads storage
    if "recent_uploads" not in st.session_state:
        st.session_state["recent_uploads"] = []

    # Two column layout before file is uploaded, single column after
    has_dataset = "dataset" in st.session_state
    
    if not has_dataset:
        upload_col, history_col = st.columns([5, 3])
    else:
        upload_col = st.container()
        history_col = None

    with upload_col:
        # File uploader workspace styled inside a card
        with st.container(border=True):
            uploaded_file = st.file_uploader(
                "Choose a data file",
                type=["csv", "xlsx", "xls"],
                help="Supported formats: CSV, Excel (.xlsx, .xls). File size limits up to 200MB.",
                label_visibility="collapsed",
            )

    if history_col:
        with history_col:
            st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 0;">Recent Uploads</p>', unsafe_allow_html=True)
            if st.session_state["recent_uploads"]:
                for index, item in enumerate(st.session_state["recent_uploads"]):
                    st.markdown(
                        f"""
                        <div class="glass-card" style="padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <p style="margin: 0; font-size: 0.85rem; font-weight: 500; color: var(--text);">{item['filename']}</p>
                                <p style="margin: 0; font-size: 0.75rem; color: var(--subtext);">{item['rows']:,} rows &bull; {item['cols']} cols</p>
                            </div>
                            <span style="font-size: 0.72rem; color: var(--subtext);">{item['time']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<p style="font-size: 0.8rem; color: var(--subtext); font-style: italic;">No recent uploads in this session.</p>', unsafe_allow_html=True)

    # Process upload if file is provided
    if uploaded_file is not None:
        file_key = (uploaded_file.name, uploaded_file.size)
        if st.session_state.get("last_processed_file") != file_key:
            try:
                # 1. Premium simulated progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                stages = [
                    (20, "Reading raw file bytes..."),
                    (50, "Saving local file copy..."),
                    (75, "Parsing tabular structure..."),
                    (95, "Running data profiling audits..."),
                    (100, "Finalizing Kosvio session state...")
                ]
                
                for pct, msg in stages:
                    import time
                    status_text.markdown(f'<span style="font-size: 0.85rem; color: var(--subtext);">{msg}</span>', unsafe_allow_html=True)
                    time.sleep(0.08)
                    progress_bar.progress(pct)
                
                progress_bar.empty()
                status_text.empty()

                # Call the new UploadService to validate, save and parse the file
                from services.upload_service import UploadService
                df, saved_path = UploadService.process_upload(uploaded_file)
                
                st.session_state["dataset"] = df
                st.session_state["original_df"] = df.copy()
                st.session_state["dataset_filename"] = uploaded_file.name
                st.session_state["last_processed_file"] = file_key
                st.session_state.pop("cleaned_df", None)
                st.session_state.pop("cleaning_summary", None)
                st.session_state.pop("just_cleaned", None)
                st.session_state.pop("dataset_health_score", None)
                
                # Append to recent uploads history
                import datetime
                recent_entry = {
                    "filename": uploaded_file.name,
                    "rows": len(df),
                    "cols": len(df.columns),
                    "time": datetime.datetime.now().strftime("%I:%M %p")
                }
                if uploaded_file.name not in [u["filename"] for u in st.session_state["recent_uploads"]]:
                    st.session_state["recent_uploads"].append(recent_entry)
                
                st.rerun()
            except Exception as e:
                # Reset state on failure to ensure clean error state
                st.session_state.pop("dataset", None)
                st.session_state.pop("dataset_filename", None)
                st.session_state["last_processed_file"] = None
                st.markdown(
                    f"""
                    <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                        <h4 style="margin: 0 0 0.25rem; color: #EF4444; font-size: 0.95rem; font-weight: 600;">Invalid Dataset File</h4>
                        <p style="margin: 0; color: var(--subtext); font-size: 0.82rem;">{str(e)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.session_state["last_processed_file"] = None

    # Retrieve dataset from session state
    if "dataset" in st.session_state:
        df = st.session_state["dataset"]
        orig_df = st.session_state.get("original_df", df)
        filename = st.session_state.get("dataset_filename", "dataset.csv")

        # Active Dataset Row with Clear Workspace button
        col_title, col_clear = st.columns([4, 1.2])
        with col_title:
            st.markdown(f'<h3 style="font-weight: 700; color: var(--text); margin-top: 0.5rem; margin-bottom: 1.5rem;">Active Dataset: <span style="color: var(--primary);">{filename}</span></h3>', unsafe_allow_html=True)
        with col_clear:
            if st.button("Clear Workspace", key="upload_clear_workspace", type="secondary", width="stretch"):
                from utils.workspace_manager import clear_workspace
                clear_workspace()
                st.rerun()

        # Get profile stats
        profile = DatasetService.get_profile(df)
        summary = profile["summary"]

        # Premium Animated Success Banner
        st.markdown(
            f"""
            <style>
            @keyframes slideIn {{
                from {{ transform: translateY(-8px); opacity: 0; }}
                to {{ transform: translateY(0); opacity: 1; }}
            }}
            .success-banner {{
                animation: slideIn 0.2s ease-out forwards;
                background: rgba(16, 185, 129, 0.08) !important;
                border: 1px solid rgba(16, 185, 129, 0.2) !important;
                border-radius: 8px;
                padding: 0.85rem 1rem;
                margin-top: 1rem;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }}
            </style>
            <div class="success-banner">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: #10B981; display: flex; align-items: center; justify-content: center;">
                    <svg viewBox="0 0 24 24" style="width: 14px; height: 14px; stroke: #fff; stroke-width: 3; fill: none;"><polyline points="20 6 9 17 4 12"/></svg>
                </div>
                <div>
                    <h4 style="margin: 0; color: #10B981; font-weight: 600; font-size: 0.9rem;">Dataset Successfully Loaded</h4>
                    <p style="margin: 0; color: var(--subtext); font-size: 0.78rem;">Profiled and indexed for active workspace models.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Metrics section (6 columns grid)
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            render_metric_card(
                value=f"{summary['rows']:,}",
                label="Rows",
                detail="Total data samples",
                icon_svg='<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/></svg>',
            )
        with col2:
            render_metric_card(
                value=str(summary["columns"]),
                label="Columns",
                detail="Total variables",
                icon_svg='<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="21" y1="12" x2="3" y2="12"/><line x1="12" y1="3" x2="12" y2="21"/></svg>',
            )
        with col3:
            missing_val = summary["missing_cells"]
            missing_pct = summary["missing_pct"]
            render_metric_card(
                value=f"{missing_val:,}",
                label="Missing",
                detail=f"{missing_pct:.1f}% of total dataset",
                trend=f"{missing_pct:.1f}%",
                trend_positive=(missing_val == 0),
                icon_svg='<svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
            )
        with col4:
            dups = summary["duplicate_rows"]
            render_metric_card(
                value=f"{dups:,}",
                label="Duplicates",
                detail="Redundant rows",
                trend=str(dups),
                trend_positive=(dups == 0),
                icon_svg='<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
            )
        with col5:
            formatted_mem = format_memory_size(summary["memory_bytes"])
            render_metric_card(
                value=formatted_mem,
                label="Dataset Size",
                detail="Raw dataset footprint",
                icon_svg='<svg viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l-7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.73z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
            )
        with col6:
            mem_mb = profile["memory_usage_mb"]
            render_metric_card(
                value=f"{mem_mb:.2f} MB",
                label="Memory Usage",
                detail="System active RAM",
                icon_svg='<svg viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>',
            )

        # Perform advanced data quality audits
        audit = perform_advanced_audit(orig_df)
        before_score = calculate_health_score(orig_df)
        
        if before_score >= 80:
            score_color = "#10B981"  # Emerald
        elif before_score >= 50:
            score_color = "#F59E0B"  # Amber
        else:
            score_color = "#EF4444"  # Red
            
        st.markdown(
            f'<div style="display: flex; align-items: center; justify-content: space-between; margin-top: 2rem; margin-bottom: 0.5rem;">'
            f'<h3 style="margin: 0; font-weight: 700; color: var(--text);">Data Quality Report</h3>'
            f'<h4 style="margin: 0; font-weight: 700; color: var(--text);">Health Score: <span style="color: {score_color};">{before_score:.1f}/100</span></h4>'
            f'</div>',
            unsafe_allow_html=True
        )

        with glass_card_panel():
            # Row 1 of Data Quality Metrics
            q_col1, q_col2, q_col3, q_col4 = st.columns(4)
            with q_col1:
                st.markdown(f'<p style="font-size: 0.85rem; color: var(--subtext); margin-bottom: 0;">Missing Values</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size: 1.5rem; font-weight: 700; color: var(--text); margin-top: 0;">{audit["missing_cells"]:,} ({audit["missing_pct"]:.1f}%)</p>', unsafe_allow_html=True)
            with q_col2:
                st.markdown(f'<p style="font-size: 0.85rem; color: var(--subtext); margin-bottom: 0;">Duplicate Rows</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size: 1.5rem; font-weight: 700; color: var(--text); margin-top: 0;">{audit["duplicate_rows"]:,}</p>', unsafe_allow_html=True)
            with q_col3:
                st.markdown(f'<p style="font-size: 0.85rem; color: var(--subtext); margin-bottom: 0;">Incorrect Datatypes</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size: 1.5rem; font-weight: 700; color: var(--text); margin-top: 0;">{len(audit["incorrect_cols"])}</p>', unsafe_allow_html=True)
            with q_col4:
                st.markdown(f'<p style="font-size: 0.85rem; color: var(--subtext); margin-bottom: 0;">Empty Columns</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size: 1.5rem; font-weight: 700; color: var(--text); margin-top: 0;">{len(audit["empty_cols"])}</p>', unsafe_allow_html=True)

            st.markdown('<div style="margin-top: 1rem; border-top: 1px solid var(--border); padding-top: 1rem;"></div>', unsafe_allow_html=True)

            # Row 2 of Advanced Data Quality Metrics
            q_col5, q_col6, q_col7, q_col8 = st.columns(4)
            with q_col5:
                st.markdown(f'<p style="font-size: 0.85rem; color: var(--subtext); margin-bottom: 0;">Outliers Detected</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size: 1.5rem; font-weight: 700; color: var(--text); margin-top: 0;">{audit["outliers_count"]:,}</p>', unsafe_allow_html=True)
            with q_col6:
                st.markdown(f'<p style="font-size: 0.85rem; color: var(--subtext); margin-bottom: 0;">Constant Columns</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size: 1.5rem; font-weight: 700; color: var(--text); margin-top: 0;">{len(audit["constant_cols"])}</p>', unsafe_allow_html=True)
            with q_col7:
                st.markdown(f'<p style="font-size: 0.85rem; color: var(--subtext); margin-bottom: 0;">High-Cardinality Columns</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size: 1.5rem; font-weight: 700; color: var(--text); margin-top: 0;">{len(audit["high_card_cols"])}</p>', unsafe_allow_html=True)
            with q_col8:
                invalid_dates_count = sum(audit["invalid_date_cols"].values())
                st.markdown(f'<p style="font-size: 0.85rem; color: var(--subtext); margin-bottom: 0;">Invalid Date Formats</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size: 1.5rem; font-weight: 700; color: var(--text); margin-top: 0;">{invalid_dates_count}</p>', unsafe_allow_html=True)
            
            # Recommendations section
            st.markdown('<div style="margin-top: 1rem; border-top: 1px solid var(--border); padding-top: 1rem;"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 1rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem;">Quality Recommendations</p>', unsafe_allow_html=True)
            
            recommendations = []
            if audit["missing_cells"] > 0:
                recommendations.append(f"**Resolve Missing Values**: The dataset has {audit['missing_cells']:,} missing cells. Consider filling numeric fields with Median and categorical fields with Mode.")
            if audit["duplicate_rows"] > 0:
                recommendations.append(f"**Deduplicate Records**: Found {audit['duplicate_rows']:,} duplicate rows. Deduplicating prevents analytical skew.")
            if audit["empty_cols"]:
                recommendations.append(f"**Drop Empty Columns**: Dropping empty columns (`{', '.join(audit['empty_cols'])}`) cleans the data dictionary.")
            if audit["incorrect_cols"]:
                details = [f"`{col}` ({curr} ➔ {inf})" for col, curr, inf in audit["incorrect_cols"][:5]]
                recommendations.append(f"**Convert Column Datatypes**: Restructure {len(audit['incorrect_cols'])} misaligned columns: {', '.join(details)}.")
            if audit["outliers_count"] > 0:
                recommendations.append(f"**Clip Numerical Outliers**: Audited {audit['outliers_count']:,} values lying outside IQR bounds across {len(audit['outlier_cols'])} columns.")
            if audit["constant_cols"]:
                recommendations.append(f"**Drop Constant Columns**: Drop columns `{', '.join(audit['constant_cols'])}` containing a single repeated value.")
            if audit["high_card_cols"]:
                recommendations.append(f"**Drop High-Cardinality**: Exclude text-heavy fields (`{', '.join(audit['high_card_cols'])}`) with high unique ratios from statistical analysis.")
            if invalid_dates_count > 0:
                recommendations.append(f"**Fix Date Fields**: Convert invalid string records to NaT formats in {len(audit['invalid_date_cols'])} date fields.")
            
            if not recommendations:
                st.markdown('<p style="font-size: 0.85rem; color: #10B981; margin: 0;">✓ Outstanding data quality! The dataset is ready for dashboard visualizations and model computations.</p>', unsafe_allow_html=True)
            else:
                for rec in recommendations:
                    st.markdown(f'<p style="font-size: 0.85rem; color: var(--text); margin-bottom: 0.25rem;">• {rec}</p>', unsafe_allow_html=True)

        # Cleaning Actions section
        st.markdown('<h3 style="margin-top: 2rem; font-weight: 700; color: var(--text);">Cleaning Actions</h3>', unsafe_allow_html=True)
        with glass_card_panel():
            st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 0; margin-bottom: 1rem;">Select Operations to Apply</p>', unsafe_allow_html=True)
            
            # Necessity Checks for standard operations
            dups_needed = audit["duplicate_rows"] > 0
            
            numeric_cols_list = orig_df.select_dtypes(include=[np.number]).columns.tolist()
            num_missing_needed = any(orig_df[col].isnull().any() for col in numeric_cols_list) if numeric_cols_list else False
            
            cat_cols_list = orig_df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
            cat_missing_needed = any(orig_df[col].isnull().any() for col in cat_cols_list) if cat_cols_list else False
            
            empty_needed = len(audit["empty_cols"]) > 0
            dtypes_needed = len(audit["incorrect_cols"]) > 0
            
            has_trim = False
            for col in orig_df.columns:
                if orig_df[col].dtype == "object":
                    sample = orig_df[col].dropna()
                    if not sample.empty:
                        if any(isinstance(x, str) and (x.strip() != x) for x in sample):
                            has_trim = True
                            break
            trim_needed = has_trim
            
            # Advanced operations necessity checks
            outliers_needed = audit["outliers_count"] > 0
            constant_needed = len(audit["constant_cols"]) > 0
            high_card_needed = len(audit["high_card_cols"]) > 0
            invalid_dates_needed = sum(audit["invalid_date_cols"].values()) > 0

            # 1. Duplicate Rows
            col_chk1, col_status1 = st.columns([3, 2])
            with col_chk1:
                clean_dups = st.checkbox("Remove duplicate rows", value=dups_needed, disabled=not dups_needed, key="clean_dups")
            with col_status1:
                if dups_needed:
                    st.markdown(f'<span style="color: var(--primary); font-weight: 600; font-size: 0.85rem;">✦ Recommended ({audit["duplicate_rows"]} duplicates)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color: var(--subtext); font-size: 0.85rem;">✓ Not Needed (No duplicate rows detected)</span>', unsafe_allow_html=True)
                    
            # 2. Numeric Median
            col_chk2, col_status2 = st.columns([3, 2])
            with col_chk2:
                clean_num = st.checkbox("Fill missing numeric values with Median", value=num_missing_needed, disabled=not num_missing_needed, key="clean_num")
            with col_status2:
                if num_missing_needed:
                    st.markdown('<span style="color: var(--primary); font-weight: 600; font-size: 0.85rem;">✦ Recommended (Missing numeric values)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color: var(--subtext); font-size: 0.85rem;">✓ Not Needed (No missing numeric values)</span>', unsafe_allow_html=True)
                    
            # 3. Categorical Mode
            col_chk3, col_status3 = st.columns([3, 2])
            with col_chk3:
                clean_cat = st.checkbox("Fill missing categorical values with Mode", value=cat_missing_needed, disabled=not cat_missing_needed, key="clean_cat")
            with col_status3:
                if cat_missing_needed:
                    st.markdown('<span style="color: var(--primary); font-weight: 600; font-size: 0.85rem;">✦ Recommended (Missing categorical values)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color: var(--subtext); font-size: 0.85rem;">✓ Not Needed (No missing categorical values)</span>', unsafe_allow_html=True)
                    
            # 4. Empty Columns Row
            col_chk4, col_status4 = st.columns([3, 2])
            with col_chk4:
                clean_empty_cols = st.checkbox("Remove completely empty columns", value=empty_needed, disabled=not empty_needed, key="clean_empty_cols")
            with col_status4:
                if empty_needed:
                    st.markdown(f'<span style="color: var(--primary); font-weight: 600; font-size: 0.85rem;">✦ Recommended ({len(audit["empty_cols"])} empty columns)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color: var(--subtext); font-size: 0.85rem;">✓ Not Needed (No empty columns detected)</span>', unsafe_allow_html=True)
                    
            # 5. Datatype Conversion Row
            col_chk5, col_status5 = st.columns([3, 2])
            with col_chk5:
                clean_dtypes = st.checkbox("Automatically convert data types", value=dtypes_needed, disabled=not dtypes_needed, key="clean_dtypes")
            with col_status5:
                if dtypes_needed:
                    st.markdown(f'<span style="color: var(--primary); font-weight: 600; font-size: 0.85rem;">✦ Recommended ({len(audit["incorrect_cols"])} mismatching columns)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color: var(--subtext); font-size: 0.85rem;">✓ Not Needed (All datatypes are optimal)</span>', unsafe_allow_html=True)
                    
            # 6. Trim whitespace Row
            col_chk6, col_status6 = st.columns([3, 2])
            with col_chk6:
                clean_trim = st.checkbox("Trim leading/trailing spaces from text columns", value=trim_needed, disabled=not trim_needed, key="clean_trim")
            with col_status6:
                if trim_needed:
                    st.markdown('<span style="color: var(--primary); font-weight: 600; font-size: 0.85rem;">✦ Recommended (Trailing spaces detected)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color: var(--subtext); font-size: 0.85rem;">✓ Not Needed (No trailing spaces detected)</span>', unsafe_allow_html=True)
                    
            # 7. Clip Outliers Row
            col_chk7, col_status7 = st.columns([3, 2])
            with col_chk7:
                clean_outliers = st.checkbox("Handle/Clip numeric outliers (IQR)", value=outliers_needed, disabled=not outliers_needed, key="clean_outliers")
            with col_status7:
                if outliers_needed:
                    st.markdown(f'<span style="color: var(--primary); font-weight: 600; font-size: 0.85rem;">✦ Recommended ({audit["outliers_count"]} outlier values)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color: var(--subtext); font-size: 0.85rem;">✓ Not Needed (No outlier cells detected)</span>', unsafe_allow_html=True)
                    
            # 8. Drop Constant Columns Row
            col_chk8, col_status8 = st.columns([3, 2])
            with col_chk8:
                clean_constant = st.checkbox("Remove constant columns", value=constant_needed, disabled=not constant_needed, key="clean_constant")
            with col_status8:
                if constant_needed:
                    st.markdown(f'<span style="color: var(--primary); font-weight: 600; font-size: 0.85rem;">✦ Recommended ({len(audit["constant_cols"])} constant columns)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color: var(--subtext); font-size: 0.85rem;">✓ Not Needed (No constant columns detected)</span>', unsafe_allow_html=True)
                    
            # 9. Drop High-Cardinality Columns Row
            col_chk9, col_status9 = st.columns([3, 2])
            with col_chk9:
                clean_high_card = st.checkbox("Remove high-cardinality text columns", value=high_card_needed, disabled=not high_card_needed, key="clean_high_card")
            with col_status9:
                if high_card_needed:
                    st.markdown(f'<span style="color: var(--primary); font-weight: 600; font-size: 0.85rem;">✦ Recommended ({len(audit["high_card_cols"])} text columns)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color: var(--subtext); font-size: 0.85rem;">✓ Not Needed (No high-cardinality columns)</span>', unsafe_allow_html=True)
                    
            # 10. Fix Invalid Dates Row
            col_chk10, col_status10 = st.columns([3, 2])
            with col_chk10:
                clean_invalid_dates = st.checkbox("Coerce invalid date values to NaT", value=invalid_dates_needed, disabled=not invalid_dates_needed, key="clean_invalid_dates")
            with col_status10:
                if invalid_dates_needed:
                    st.markdown(f'<span style="color: var(--primary); font-weight: 600; font-size: 0.85rem;">✦ Recommended ({invalid_dates_count} invalid cells)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color: var(--subtext); font-size: 0.85rem;">✓ Not Needed (No invalid date structures)</span>', unsafe_allow_html=True)

            # Cleaning Operations Preview
            st.markdown('<div style="margin-top: 1.5rem; border-top: 1px solid var(--border); padding-top: 1rem;"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 1rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem;">Cleaning Operations Preview</p>', unsafe_allow_html=True)
            
            preview_items = []
            if clean_dups:
                preview_items.append(f"Deduplicate: Drop {audit['duplicate_rows']} duplicate rows.")
            if clean_num:
                preview_items.append("Impute numeric missing cells with Median values.")
            if clean_cat:
                preview_items.append("Impute categorical missing cells with Mode values.")
            if clean_empty_cols:
                preview_items.append(f"Schema: Drop empty columns (`{', '.join(audit['empty_cols'])}`).")
            if clean_dtypes:
                preview_items.append(f"Format: Standardize alignments for {len(audit['incorrect_cols'])} columns.")
            if clean_trim:
                preview_items.append("Trim: Strip trailing whitespace from text variables.")
            if clean_outliers:
                preview_items.append(f"Outliers: Clip numerical cells inside IQR range in `{', '.join(audit['outlier_cols'].keys())}`.")
            if clean_constant:
                preview_items.append(f"Drop single-value columns: `{', '.join(audit['constant_cols'])}`.")
            if clean_high_card:
                preview_items.append(f"Drop high-cardinality text: `{', '.join(audit['high_card_cols'])}`.")
            if clean_invalid_dates:
                preview_items.append(f"Dates: Parse invalid dates as NaT in `{', '.join(audit['invalid_date_cols'].keys())}`.")
            
            if preview_items:
                for item in preview_items:
                    st.markdown(f'<p style="font-size: 0.82rem; color: var(--subtext); margin-bottom: 0.25rem;">&nbsp;&nbsp;&bull; {item}</p>', unsafe_allow_html=True)
            else:
                st.info("No cleaning operations selected.")

            st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
            
            if st.button("Clean Dataset", type="primary", width="stretch"):
                work_df = orig_df.copy()
                detailed_changes = []
                
                # 1. Remove duplicate rows
                rows_removed = 0
                if clean_dups:
                    from analytics.cleaning import remove_duplicates
                    dups_before = int(work_df.duplicated().sum())
                    work_df = remove_duplicates(work_df)
                    rows_removed += dups_before
                    detailed_changes.append(f"**Duplicate rows**: Removed {dups_before} duplicate rows.")
                else:
                    detailed_changes.append("**Duplicate rows**: No duplicates removed.")
                    
                # 2. Fill missing values
                filled_count = 0
                if clean_num:
                    from analytics.cleaning import fill_missing
                    num_cols = work_df.select_dtypes(include=[np.number]).columns
                    for col in num_cols:
                        if col in work_df.columns:
                            nulls_count = int(work_df[col].isnull().sum())
                            if nulls_count > 0:
                                work_df = fill_missing(work_df, column=col, strategy="median")
                                filled_count += nulls_count
                    detailed_changes.append(f"**Missing numerical values**: Imputed {filled_count} cell values with Median.")
                else:
                    detailed_changes.append("**Missing numerical values**: No missing numeric values filled.")
                    
                if clean_cat:
                    from analytics.cleaning import fill_missing
                    cat_cols = work_df.select_dtypes(include=["object", "category", "bool"]).columns
                    for col in cat_cols:
                        if col in work_df.columns:
                            nulls_count = int(work_df[col].isnull().sum())
                            if nulls_count > 0:
                                work_df = fill_missing(work_df, column=col, strategy="mode")
                                filled_count += nulls_count
                    detailed_changes.append(f"**Missing categorical values**: Imputed missing cells with Mode.")
                else:
                    detailed_changes.append("**Missing categorical values**: No missing categorical values filled.")

                empty_cols_to_remove = []
                if clean_empty_cols:
                    # Do not drop date-related columns
                    empty_cols_to_remove = [
                        col for col in work_df.columns
                        if work_df[col].isna().all() and not any(kw in col.lower() for kw in ["date", "time", "year", "created", "updated", "joining", "order", "timestamp"])
                    ]
                    work_df = work_df.drop(columns=[col for col in empty_cols_to_remove if col in work_df.columns])
                    detailed_changes.append(f"**Empty columns**: Dropped {len(empty_cols_to_remove)} columns (`{', '.join(empty_cols_to_remove)}`).")
                else:
                    detailed_changes.append("**Empty columns**: No empty columns dropped.")
                    
                # 3. Convert datatypes
                converted_cols = []
                if clean_dtypes:
                    from analytics.cleaning import convert_datatypes, auto_detect_datatypes
                    inferred_types = auto_detect_datatypes(work_df)
                    for col in work_df.columns:
                        if col in work_df.columns:
                            curr_type = str(work_df[col].dtype)
                            inf_type = inferred_types.get(col)
                            
                            is_incorrect = False
                            target_type = None
                            if inf_type == "datetime64[ns]" and not curr_type.startswith("datetime"):
                                is_incorrect = True
                                target_type = "datetime"
                            elif inf_type == "category" and curr_type not in ["category", "bool"]:
                                is_incorrect = True
                                target_type = "category"
                            elif inf_type == "int64" and not (curr_type.startswith("int") or curr_type.startswith("UInt")):
                                is_incorrect = True
                                target_type = "int64"
                            elif inf_type == "float64" and not curr_type.startswith("float"):
                                is_incorrect = True
                                target_type = "float64"
                                
                            if is_incorrect and target_type:
                                work_df = convert_datatypes(work_df, column=col, datatype=target_type)
                                converted_cols.append(f"`{col}` ➔ `{inf_type}`")
                                
                    detailed_changes.append(f"**Datatype conversions**: Converted {len(converted_cols)} columns ({', '.join(converted_cols)}).")
                else:
                    detailed_changes.append("**Datatype conversions**: No datatypes converted.")
                    
                if clean_trim:
                    trimmed_cols_count = 0
                    for col in work_df.columns:
                        if col in work_df.columns:
                            if work_df[col].dtype == "object":
                                work_df[col] = work_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
                                trimmed_cols_count += 1
                            elif isinstance(work_df[col].dtype, pd.CategoricalDtype):
                                try:
                                    work_df[col] = work_df[col].cat.rename_categories(lambda x: x.strip() if isinstance(x, str) else x)
                                    trimmed_cols_count += 1
                                except Exception:
                                    pass
                    detailed_changes.append(f"**Whitespace trimming**: Trimmed spaces across {trimmed_cols_count} text columns.")
                else:
                    detailed_changes.append("**Whitespace trimming**: No whitespace trimmed.")

                # 4. Validate and clean date columns
                invalid_dates_fixed = 0
                if clean_invalid_dates:
                    for col in audit["invalid_date_cols"]:
                        if col in work_df.columns:
                            orig_n = int(work_df[col].isnull().sum())
                            work_df[col] = pd.to_datetime(work_df[col], errors="coerce")
                            new_n = int(work_df[col].isnull().sum())
                            invalid_dates_fixed += (new_n - orig_n)
                    detailed_changes.append(f"**Invalid dates**: Coerced {invalid_dates_fixed} values to NaT.")
                else:
                    detailed_changes.append("**Invalid dates**: No invalid dates coerced.")
                    
                # 5. Handle outliers
                outliers_clipped = 0
                if clean_outliers:
                    for col in audit["outlier_cols"]:
                        if col in work_df.columns:
                            q1 = work_df[col].quantile(0.25)
                            q3 = work_df[col].quantile(0.75)
                            iqr = q3 - q1
                            if iqr > 0:
                                lower = q1 - 1.5 * iqr
                                upper = q3 + 1.5 * iqr
                                clip_mask = (work_df[col] < lower) | (work_df[col] > upper)
                                outliers_clipped += int(clip_mask.sum())
                                work_df[col] = work_df[col].clip(lower, upper)
                    detailed_changes.append(f"**Outliers**: Capped {outliers_clipped} outliers to IQR bounds.")
                else:
                    detailed_changes.append("**Outliers**: No outliers clipped.")
                    
                # 6. Remove constant columns
                if clean_constant:
                    constant_to_drop = [
                        col for col in audit["constant_cols"]
                        if col in work_df.columns and not any(kw in col.lower() for kw in ["date", "time", "year", "created", "updated", "joining", "order", "timestamp"])
                    ]
                    if constant_to_drop:
                        work_df = work_df.drop(columns=constant_to_drop)
                    detailed_changes.append(f"**Constant columns**: Dropped {len(constant_to_drop)} single-value columns.")
                else:
                    detailed_changes.append("**Constant columns**: No constant columns dropped.")
                    
                # 7. Remove high-cardinality columns (if enabled)
                if clean_high_card:
                    high_card_to_drop = [
                        col for col in audit["high_card_cols"]
                        if col in work_df.columns and not any(kw in col.lower() for kw in ["date", "time", "year", "created", "updated", "joining", "order", "timestamp"])
                    ]
                    # Only remove true identifier columns like Name, Email, Phone, Address, Customer_ID, ID
                    high_card_to_drop = [
                        col for col in high_card_to_drop
                        if any(id_kw in col.lower() for id_kw in ["name", "email", "phone", "address", "id", "identifier", "customer", "employee"])
                    ]
                    if high_card_to_drop:
                        work_df = work_df.drop(columns=high_card_to_drop)
                    detailed_changes.append(f"**High-cardinality**: Dropped {len(high_card_to_drop)} columns.")
                else:
                    detailed_changes.append("**High-cardinality**: No high-cardinality columns dropped.")

                # Save results to session state
                st.session_state["cleaned_df"] = work_df
                st.session_state["dataset"] = work_df
                summary_report = {
                    "rows_removed": rows_removed,
                    "missing_fixed": filled_count,
                    "dtypes_converted": len(converted_cols),
                    "outliers_handled": outliers_clipped,
                    "empty_removed": len(empty_cols_to_remove),
                    "detailed_changes": detailed_changes,
                    "score_before": before_score,
                    "score_after": calculate_health_score(work_df)
                }
                
                st.session_state["cleaning_summary"] = summary_report
                st.session_state["just_cleaned"] = True
                st.rerun()

        # Display Cleaning Summary
        if st.session_state.get("just_cleaned", False) and "cleaning_summary" in st.session_state:
            summary_report = st.session_state["cleaning_summary"]
            score_b = summary_report["score_before"]
            score_a = summary_report["score_after"]
            
            st.markdown('<h3 style="margin-top: 1.5rem; font-weight: 700; color: var(--text);">Data Quality Audit & Cleaning Report</h3>', unsafe_allow_html=True)
            
            with glass_card_panel():
                col_sc1, col_sc2 = st.columns(2)
                with col_sc1:
                    st.metric("Before Health Score", f"{score_b:.1f}/100")
                with col_sc2:
                    delta = score_a - score_b
                    st.metric("After Health Score", f"{score_a:.1f}/100", f"+{delta:.1f}" if delta > 0 else f"{delta:.1f}")
                
                st.markdown('<div style="margin-top: 1rem; border-top: 1px solid var(--border); padding-top: 1rem;"></div>', unsafe_allow_html=True)
                st.markdown('<p style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 0.75rem;">Quality Improvements Summary</p>', unsafe_allow_html=True)
                
                sum_col1, sum_col2, sum_col3, sum_col4, sum_col5 = st.columns(5)
                with sum_col1:
                    st.markdown('<p style="font-size: 0.8rem; color: var(--subtext); margin-bottom: 0;">Rows Affected</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="font-size: 1.35rem; font-weight: 700; color: var(--text); margin-top: 0;">{summary_report["rows_removed"]:,}</p>', unsafe_allow_html=True)
                with sum_col2:
                    st.markdown('<p style="font-size: 0.8rem; color: var(--subtext); margin-bottom: 0;">Duplicates Removed</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="font-size: 1.35rem; font-weight: 700; color: var(--text); margin-top: 0;">{summary_report["rows_removed"]:,}</p>', unsafe_allow_html=True)
                with sum_col3:
                    st.markdown('<p style="font-size: 0.8rem; color: var(--subtext); margin-bottom: 0;">Missing Repaired</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="font-size: 1.35rem; font-weight: 700; color: var(--text); margin-top: 0;">{summary_report["missing_fixed"]:,}</p>', unsafe_allow_html=True)
                with sum_col4:
                    st.markdown('<p style="font-size: 0.8rem; color: var(--subtext); margin-bottom: 0;">Outliers Treated</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="font-size: 1.35rem; font-weight: 700; color: var(--text); margin-top: 0;">{summary_report["outliers_handled"]:,}</p>', unsafe_allow_html=True)
                with sum_col5:
                    st.markdown('<p style="font-size: 0.8rem; color: var(--subtext); margin-bottom: 0;">Datatype Optimizations</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="font-size: 1.35rem; font-weight: 700; color: var(--text); margin-top: 0;">{summary_report["dtypes_converted"]}</p>', unsafe_allow_html=True)
                
                st.markdown('<div style="margin-top: 1rem; border-top: 1px solid var(--border); padding-top: 1rem;"></div>', unsafe_allow_html=True)
                st.markdown('<p style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem;">Audit Logs & Specific Actions</p>', unsafe_allow_html=True)
                for change in summary_report.get("detailed_changes", []):
                    st.markdown(f'<p style="font-size: 0.82rem; color: var(--subtext); margin-bottom: 0.25rem;">&bull; {change}</p>', unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)

        # Tabbed preview workspace
        tab1, tab2, tab3 = st.tabs(
            ["Dataset Preview", "Schema & Types", "Missing Summary"]
        )

        with tab1:
            st.subheader("Data Preview")
            # Show first 10 rows in premium table
            render_table_container(df.head(10), max_height_px=450)

        with tab2:
            st.subheader("Column Metadata")
            # Show column summaries
            render_table_container(profile["columns"], max_height_px=450)

        with tab3:
            st.subheader("Missing Values Breakdown")
            # Show missing report
            missing_df = profile["missing"]
            if not missing_df.empty:
                missing_df = missing_df.reset_index().rename(
                    columns={"index": "Column Name"}
                )
                render_table_container(missing_df, max_height_px=450)
            else:
                st.info("No missing values detected in the dataset. Excellent data quality!")

    else:
        render_empty_state(
            title="No Dataset Uploaded",
            message="Please drag and drop your data file above. Kosvio will display analytics metrics, summaries, and distribution profiles once a file is provided.",
        )


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    # Load external stylesheet if run standalone
    try:
        with open("styles/theme.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    render()
