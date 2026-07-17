import streamlit as st

def clear_workspace():
    """
    Securely clear all dataset-related session state variables,
    cached data profiling, AI insights, and workspace configurations.
    """
    keys_to_clear = [
        "dataset",
        "original_df",
        "cleaned_df",
        "dataset_filename",
        "dataset_health_score",
        "last_processed_file",
        "uploaded_file_id",
        "recent_uploads",
        "cleaning_summary",
        "just_cleaned",
        "last_filter_state",
        "forecast_logged",
        "activity_log",
        "ai_messages"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
            
    # Reinitialize recent_uploads to empty list
    st.session_state["recent_uploads"] = []
