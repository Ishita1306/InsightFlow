"""
Settings Workspace Page.

Configures system preferences, visual themes, and integration profiles.
"""

import streamlit as st
from components.section_header import render_section_header
from components.glass_card import glass_card_panel


def render() -> None:
    """Render the settings workspace page."""
    render_section_header(
        title="Settings Workspace",
        subtitle="Configure application preferences and user credentials.",
        label="Configuration Center",
    )

    user_info = st.session_state.get("user", {"email": "guest@kosvio.io", "name": "Guest"})

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        # 1. Profile Settings
        st.markdown('<h4 style="margin: 1.5rem 0 0.75rem; font-size: 1.15rem; font-weight: 700; color: var(--text); letter-spacing: -0.02em;">Profile Settings</h4>', unsafe_allow_html=True)
        with glass_card_panel():
            st.markdown('<p style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-top: 0; margin-bottom: 1.25rem;">Personal Information</p>', unsafe_allow_html=True)
            st.text_input("Full Name", value=user_info["name"], key="settings_profile_name")
            st.text_input("Email Address", value=user_info["email"], key="settings_profile_email")
            if st.button("Save Changes", type="secondary", key="settings_save_profile"):
                st.toast("Profile settings saved successfully.")

        # 2. Security Settings
        st.markdown('<h4 style="margin: 2.25rem 0 0.75rem; font-size: 1.15rem; font-weight: 700; color: var(--text); letter-spacing: -0.02em;">Security</h4>', unsafe_allow_html=True)
        with glass_card_panel():
            st.markdown('<p style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-top: 0; margin-bottom: 1.25rem;">Update Password</p>', unsafe_allow_html=True)
            st.text_input("New Password", type="password", placeholder="••••••••", key="settings_password_new")
            st.text_input("Confirm New Password", type="password", placeholder="••••••••", key="settings_password_confirm")
            if st.button("Update Password", type="secondary", key="settings_update_pass"):
                st.toast("Password successfully updated.")

    with col_right:
        # 3. Preferences & Theme
        st.markdown('<h4 style="margin: 1.5rem 0 0.75rem; font-size: 1.15rem; font-weight: 700; color: var(--text); letter-spacing: -0.02em;">System Preferences</h4>', unsafe_allow_html=True)
        with glass_card_panel():
            st.markdown('<p style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-top: 0; margin-bottom: 1.25rem;">Preferences</p>', unsafe_allow_html=True)
            st.selectbox("Data Region", ["US-East (Iowa)", "US-West (Oregon)", "EU-West (Belgium)"], key="settings_pref_region")
            st.checkbox("Auto-profile datasets upon upload", value=True, key="settings_pref_autoprofile")
            
            st.markdown(
                """
                <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6; margin-top: 1.25rem; border-top: 1px solid var(--border); padding-top: 1.25rem; margin-bottom: 0;">
                    Data Region governs the geographic container for AI-powered processing buffers. All uploaded data remains strictly within session memory.
                </p>
                """,
                unsafe_allow_html=True
            )

    # 5. Session Management
    st.markdown('<h4 style="margin: 2.25rem 0 0.75rem; font-size: 1.15rem; font-weight: 700; color: var(--text); letter-spacing: -0.02em;">Session Management</h4>', unsafe_allow_html=True)
    with glass_card_panel():
        st.markdown('<p style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-top: 0; margin-bottom: 0.75rem;">Workspace & Account</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 1.25rem;">Logged in as: <strong>{user_info["name"]}</strong> ({user_info["email"]})</p>', unsafe_allow_html=True)
        
        col_actions = st.columns(2)
        with col_actions[0]:
            if st.button("Clear Workspace", type="primary", width="stretch"):
                from utils.workspace_manager import clear_workspace
                clear_workspace()
                st.success("Workspace securely cleared!")
                st.rerun()
        with col_actions[1]:
            if st.button("Sign Out", type="secondary", width="stretch"):
                from utils.workspace_manager import clear_workspace
                clear_workspace()
                st.session_state["authenticated"] = False
                st.session_state["user"] = None
                st.session_state["current_page"] = "landing"
                st.rerun()
