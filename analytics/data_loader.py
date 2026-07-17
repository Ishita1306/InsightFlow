"""
Data loader module.

Responsible for reading datasets from different formats (CSV, XLSX)
into Pandas DataFrames, handling encodings and sheets safely.
"""

from typing import Union, IO, Optional
import os
import pandas as pd


import streamlit as st
from io import BytesIO

@st.cache_data
def _cached_load_dataset(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """
    Cached helper to load dataset from raw bytes.
    This function caches the parsed pandas DataFrame using Streamlit's @st.cache_data.
    It automatically invalidates when the file contents or filename changes.
    """
    ext = os.path.splitext(file_name.lower())[1]
    file_source = BytesIO(file_bytes)

    if ext == ".csv":
        try:
            # Attempt default UTF-8 first, fallback to ISO-8859-1 on failure
            try:
                file_source.seek(0)
                df = pd.read_csv(file_source, encoding="utf-8")
            except UnicodeDecodeError:
                file_source.seek(0)
                df = pd.read_csv(file_source, encoding="latin1")
            
            if df.empty:
                raise ValueError("The uploaded dataset contains no rows or data.")
            return df
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Failed to parse CSV file: {str(e)}")

    elif ext in {".xlsx", ".xls"}:
        try:
            file_source.seek(0)
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
    file_source: Union[str, IO[bytes]], file_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Load a dataset from a file path or a binary file buffer.
    Utilizes Streamlit's cache_data to avoid re-reading and re-parsing file contents.

    Args:
        file_source (Union[str, IO[bytes]]): The file path or file-like object containing data.
        file_name (Optional[str]): Original filename to detect extension when file_source is a buffer.

    Returns:
        pd.DataFrame: Loaded DataFrame.

    Raises:
        ValueError: If file type is unsupported or corrupted.
    """
    # Determine the extension
    ext = ""
    if isinstance(file_source, str):
        ext = os.path.splitext(file_source)[1].lower()
        if not os.path.exists(file_source):
            raise ValueError(f"The file '{file_source}' does not exist.")
        if os.path.getsize(file_source) == 0:
            raise ValueError("The specified file is empty (0 bytes).")
        
        # Read the file bytes to cache it by contents
        with open(file_source, "rb") as f:
            file_bytes = f.read()
        return _cached_load_dataset(file_bytes, os.path.basename(file_source))

    elif file_name:
        ext = os.path.splitext(file_name)[1].lower()
        if hasattr(file_source, "seek") and hasattr(file_source, "tell"):
            file_source.seek(0, 2)
            size = file_source.tell()
            file_source.seek(0)
            if size == 0:
                raise ValueError("The uploaded file is empty (0 bytes).")

        # Get raw bytes from buffer
        if hasattr(file_source, "getvalue"):
            file_bytes = file_source.getvalue()
        else:
            file_source.seek(0)
            file_bytes = file_source.read()
            file_source.seek(0)
            
        return _cached_load_dataset(file_bytes, file_name)

    else:
        raise ValueError("Filename must be provided when file_source is a buffer.")
