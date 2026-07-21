"""
Document AI service package.
"""

from services.document_service import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_tables_from_docx,
    detect_charts_in_pdf,
    detect_charts_in_docx,
    analyze_document_text,
    validate_and_process_tables,
)
