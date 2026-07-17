"""
Upload Service.

Handles filesystem storage, file type validation, and pandas parsing for CSV and XLSX files.
"""

import os
import pandas as pd
from typing import Tuple

class UploadService:
    UPLOAD_DIR = "data/uploads"

    @classmethod
    def ensure_upload_dir(cls) -> None:
        """Ensure the upload directory exists."""
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)

    @classmethod
    def process_upload(cls, uploaded_file) -> Tuple[pd.DataFrame, str]:
        """
        Process the uploaded file completely in-memory:
        1. Validate filename extension (CSV, XLSX)
        2. Read the file into a pandas DataFrame directly from memory buffer
        3. Validate that the dataset is not empty
        
        Returns:
            Tuple[pd.DataFrame, str]: (DataFrame, "")
            
        Raises:
            ValueError: for unsupported, empty, corrupted, or failed files.
        """
        filename = uploaded_file.name
        ext = os.path.splitext(filename.lower())[1]
        
        if ext not in [".csv", ".xlsx"]:
            raise ValueError(f"Unsupported file format '{ext}'. Only CSV and XLSX are supported.")
            
        # Read the file using pandas directly from memory buffer, leveraging cached loader
        try:
            from analytics.data_loader import load_dataset
            df = load_dataset(uploaded_file, filename)
        except Exception as e:
            raise ValueError(f"Corrupted or invalid file. Could not parse tabular data: {str(e)}")
            
        if df.empty:
            raise ValueError("The uploaded dataset is empty (contains no data rows).")
            
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        return df, ""
