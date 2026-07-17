import streamlit as st
from components.glass_card import glass_card_panel
from database.auth_db import verify_user, create_user


def render() -> None:
    """Render the authentication workspace."""
    # Ensure auth and terms states exist
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "signin"
    if "show_terms" not in st.session_state:
        st.session_state["show_terms"] = False
    if "terms_accepted" not in st.session_state:
        st.session_state["terms_accepted"] = False

    if st.session_state["show_terms"]:
        from pages import terms_privacy
        terms_privacy.render()
        return

    # Inject CSS to hide the sidebar completely, use full screen, and center the card
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        [data-testid="stHeader"] {
            display: none !important;
        }
        .main .block-container {
            max-width: 100% !important;
            padding: 2rem 1rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 100vh !important;
        }
        div[data-testid="stVerticalBlock"] {
            width: 100% !important;
            max-width: 440px !important;
            margin: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Wrap in premium glass card
    with glass_card_panel():
        # Brand Header
        st.markdown(
            '<h2 style="margin: 0 0 0.25rem; font-size: 2.25rem; font-weight: 800; color: var(--text); text-align: center;">'
            'CLARIO <span style="color: var(--primary);">AI</span></h2>',
            unsafe_allow_html=True
        )
        
        if st.session_state["auth_mode"] == "signin":
            st.markdown(
                '<p style="font-size: 0.95rem; color: var(--subtext); margin-bottom: 2rem; text-align: center;">'
                'Sign in to access your analytics workspace.</p>',
                unsafe_allow_html=True
            )
            
            # Sign In Form
            email = st.text_input("Email Address", placeholder="name@company.com", key="auth_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="auth_password")
            
            # Remember Me Checkbox
            remember_me = st.checkbox("Remember Me", value=True, key="auth_remember")
            
            # Terms Agreement Checkbox & Read Link
            terms_accepted = st.checkbox(
                "I have read and agree to the Terms of Service and Privacy Policy.", 
                value=st.session_state.get("terms_accepted", False), 
                key="auth_terms_checkbox_signin"
            )
            st.session_state["terms_accepted"] = terms_accepted
            
            if st.button("Read Terms of Service", type="secondary", use_container_width=True, key="read_terms_signin"):
                st.session_state["show_terms"] = True
                st.rerun()

            st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
            
            if st.button("Sign In", use_container_width=True, type="primary", disabled=not st.session_state.get("terms_accepted", False)):
                if not email or not password:
                    st.error("Please fill in all credentials.")
                else:
                    user = verify_user(email, password)
                    if user:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user
                        st.session_state["remember_me"] = remember_me
                        st.success("Successfully authenticated!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please verify your credentials.")
            
            # Forgot Password placeholder
            if st.button("Forgot Password?", use_container_width=True, type="secondary"):
                st.info("Password recovery instructions have been sent to your email (placeholder).")
                    
            st.markdown('<div style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1rem; text-align: center;"></div>', unsafe_allow_html=True)
            if st.button("Don't have an account? Sign Up", use_container_width=True):
                st.session_state["auth_mode"] = "signup"
                st.rerun()
                
        else:
            st.markdown(
                '<p style="font-size: 0.95rem; color: var(--subtext); margin-bottom: 2rem; text-align: center;">'
                'Create an account to get started with CLARIO.</p>',
                unsafe_allow_html=True
            )
            
            # Sign Up Form
            name = st.text_input("Full Name", placeholder="John Doe", key="auth_name")
            email = st.text_input("Email Address", placeholder="name@company.com", key="auth_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="auth_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="auth_confirm")
            # Terms Agreement Checkbox & Read Link
            terms_accepted = st.checkbox(
                "I have read and agree to the Terms of Service and Privacy Policy.", 
                value=st.session_state.get("terms_accepted", False), 
                key="auth_terms_checkbox_signup"
            )
            st.session_state["terms_accepted"] = terms_accepted
            
            if st.button("Read Terms of Service", type="secondary", use_container_width=True, key="read_terms_signup"):
                st.session_state["show_terms"] = True
                st.rerun()

            st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
            
            if st.button("Sign Up", use_container_width=True, type="primary", disabled=not st.session_state.get("terms_accepted", False)):
                if not name or not email or not password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, msg = create_user(email, password, name)
                    if success:
                        st.success("Account successfully created!")
                        # Auto sign in
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = {
                            "email": email,
                            "name": name
                        }
                        st.rerun()
                    else:
                        st.error(msg)
                    
            st.markdown('<div style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1rem; text-align: center;"></div>', unsafe_allow_html=True)
            if st.button("Already have an account? Sign In", use_container_width=True):
                st.session_state["auth_mode"] = "signin"
                st.rerun()
