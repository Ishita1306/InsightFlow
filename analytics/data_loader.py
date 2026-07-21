"""
Data loader module.

Responsible for reading datasets from different formats (CSV, XLSX, XLS)
into Pandas DataFrames, handling encodings and sheets safely using chunk-based processing
for memory optimization and progress monitoring.
"""

import os
from typing import Union, IO, Optional
from io import BytesIO
import pandas as pd
import streamlit as st
from utils.stream_helper import ProgressBytesIO


def _parse_csv_chunks(file_bytes: bytes, progress_callback=None) -> pd.DataFrame:
    """
    Parse CSV bytes in chunks to optimize memory and report progress.
    """
    file_source = ProgressBytesIO(file_bytes, progress_callback)
    chunksize = 20000
    chunks = []

    try:
        # Attempt UTF-8 first, fallback to Latin1 on UnicodeDecodeError
        try:
            file_source.seek(0)
            reader = pd.read_csv(file_source, encoding="utf-8", chunksize=chunksize)
            for chunk in reader:
                # Optimize category datatypes for object columns to reduce RAM footprint
                for col in chunk.select_dtypes(include=["object"]).columns:
                    chunk[col] = chunk[col].astype("category")
                chunks.append(chunk)
        except (UnicodeDecodeError, pd.errors.ParserError):
            file_source.seek(0)
            file_source.bytes_read = 0  # Reset counter
            reader = pd.read_csv(file_source, encoding="latin1", chunksize=chunksize)
            for chunk in reader:
                for col in chunk.select_dtypes(include=["object"]).columns:
                    chunk[col] = chunk[col].astype("category")
                chunks.append(chunk)

        if not chunks:
            raise ValueError("The uploaded dataset contains no rows or data.")

        df = pd.concat(chunks, ignore_index=True)
        
        # Convert category columns back to object to avoid breaking downstream analytics that expect object type
        for col in df.select_dtypes(include=["category"]).columns:
            df[col] = df[col].astype("object")
            
        return df
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Failed to parse CSV file: {str(e)}")


@st.cache_data
def _cached_load_dataset(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """
    Cached helper to load dataset from raw bytes.
    Used when no progress callback is provided.
    """
    ext = os.path.splitext(file_name.lower())[1]
    
    if ext == ".csv":
        return _parse_csv_chunks(file_bytes, None)
    elif ext in {".xlsx", ".xls"}:
        try:
            file_source = BytesIO(file_bytes)
            df = pd.read_excel(file_source)
            if df.empty:
                raise ValueError("The uploaded dataset contains no rows or data.")
            return df
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
    else:
        raise ValueError(
            f"Unsupported file format '{ext}'. Only CSV and Excel (.xlsx, .xls) are supported."
        )


def load_dataset(
    file_source: Union[str, IO[bytes]], file_name: Optional[str] = None, progress_callback=None
) -> pd.DataFrame:
    """
    Load a dataset from a file path or a binary file buffer.
    Supports real-time progress callbacks and uses memory-optimized chunking for CSVs.

    Args:
        file_source (Union[str, IO[bytes]]): The file path or file-like object containing data.
        file_name (Optional[str]): Original filename to detect extension.
        progress_callback (Optional[Callable]): Callback triggered during chunk loading.

    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    # 1. Resolve file path source
    if isinstance(file_source, str):
        if not os.path.exists(file_source):
            raise ValueError(f"The file '{file_source}' does not exist.")
        if os.path.getsize(file_source) == 0:
            raise ValueError("The specified file is empty (0 bytes).")
        
        file_name = file_name or os.path.basename(file_source)
        with open(file_source, "rb") as f:
            file_bytes = f.read()
            
    # 2. Resolve buffer source
    else:
        if not file_name:
            raise ValueError("Filename must be provided when file_source is a buffer.")
            
        if hasattr(file_source, "seek") and hasattr(file_source, "tell"):
            file_source.seek(0, 2)
            size = file_source.tell()
            file_source.seek(0)
            if size == 0:
                raise ValueError("The uploaded file is empty (0 bytes).")

        if hasattr(file_source, "getvalue"):
            file_bytes = file_source.getvalue()
        else:
            file_source.seek(0)
            file_bytes = file_source.read()
            file_source.seek(0)

    # 3. Load with progress or retrieve cache
    ext = os.path.splitext(file_name.lower())[1]
    
    if progress_callback and ext == ".csv":
        # Stream with real-time progress updates (bypasses st.cache_data to enable UI updates)
        return _parse_csv_chunks(file_bytes, progress_callback)
    elif progress_callback and ext in {".xlsx", ".xls"}:
        # Excel does not support row-by-row streaming; call hook at start/end
        progress_callback(0, len(file_bytes))
        df = _cached_load_dataset(file_bytes, file_name)
        progress_callback(len(file_bytes), len(file_bytes))
        return df
    else:
        # Fallback to standard cached loader
        return _cached_load_dataset(file_bytes, file_name)

