import streamlit as st
from components.glass_card import glass_card_panel
from database.auth_db import verify_user, create_user, validate_email, validate_password_strength


def render() -> None:
    """Render the authentication workspace."""
    # Ensure auth and terms states exist
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "signin"
    if "show_terms" not in st.session_state:
        st.session_state["show_terms"] = False
    if "terms_accepted" not in st.session_state:
        st.session_state["terms_accepted"] = False
    
    # Initialize failed login attempts state
    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = 0
    if "login_locked" not in st.session_state:
        st.session_state["login_locked"] = False

    if st.session_state["show_terms"]:
        from pages import terms_privacy
        terms_privacy.render()
        return

    # Inject CSS to hide sidebar, collapse header, and center the container
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
        # Brand Header (using styles/theme.css classes instead of inline style rules)
        st.markdown(
            '<h2 class="auth-title">Kosvio</h2>',
            unsafe_allow_html=True
        )
        
        if st.session_state["auth_mode"] == "signin":
            st.markdown(
                '<p class="auth-subtitle">Sign in to access your analytics workspace.</p>',
                unsafe_allow_html=True
            )
            
            # Show lock warning if attempts are exceeded
            if st.session_state["login_locked"]:
                st.error("Too many failed login attempts. Access is temporarily locked. Please try again later or restart your session.")
            
            # Sign In Form
            email = st.text_input("Email Address", placeholder="name@company.com", key="auth_email")
            password = st.text_input("Password", type="password", placeholder="********", key="auth_password")
            
            # Terms Agreement Checkbox & Read Link
            terms_accepted = st.checkbox(
                "I have read and agree to the Terms of Service and Privacy Policy.", 
                value=st.session_state.get("terms_accepted", False), 
                key="auth_terms_checkbox_signin"
            )
            st.session_state["terms_accepted"] = terms_accepted
            
            if st.button("Read Terms of Service", type="secondary", width="stretch", key="read_terms_signin"):
                st.session_state["show_terms"] = True
                st.rerun()

            st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
            
            # Enable button only if terms are accepted and login is not locked
            is_locked = st.session_state["login_locked"]
            submit_disabled = is_locked or not st.session_state.get("terms_accepted", False)
            
            if st.button("Sign In", width="stretch", type="primary", disabled=submit_disabled):
                if not email or not password:
                    st.error("Please fill in all credentials.")
                else:
                    user = verify_user(email, password)
                    if user:
                        # Reset attempts upon success
                        st.session_state["login_attempts"] = 0
                        st.session_state["login_locked"] = False
                        
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user
                        st.success("Successfully authenticated!")
                        st.rerun()
                    else:
                        st.session_state["login_attempts"] += 1
                        attempts_left = 5 - st.session_state["login_attempts"]
                        if st.session_state["login_attempts"] >= 5:
                            st.session_state["login_locked"] = True
                            st.error("Too many failed login attempts. Access is temporarily locked.")
                            st.rerun()
                        else:
                            st.error(f"Invalid email or password. Please verify your credentials. ({attempts_left} attempts remaining)")
            st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)
            if st.button("Don't have an account? Sign Up", width="stretch"):
                st.session_state["auth_mode"] = "signup"
                st.rerun()
                
        else:
            st.markdown(
                '<p class="auth-subtitle">Create an account to get started with Kosvio.</p>',
                unsafe_allow_html=True
            )
            
            # Sign Up Form
            name = st.text_input("Full Name", placeholder="John Doe", key="auth_name")
            email = st.text_input("Email Address", placeholder="name@company.com", key="auth_email")
            password = st.text_input("Password", type="password", placeholder="********", key="auth_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="********", key="auth_confirm")
            
            # Terms Agreement Checkbox & Read Link
            terms_accepted = st.checkbox(
                "I have read and agree to the Terms of Service and Privacy Policy.", 
                value=st.session_state.get("terms_accepted", False), 
                key="auth_terms_checkbox_signup"
            )
            st.session_state["terms_accepted"] = terms_accepted
            
            if st.button("Read Terms of Service", type="secondary", width="stretch", key="read_terms_signup"):
                st.session_state["show_terms"] = True
                st.rerun()

            st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
            
            if st.button("Sign Up", width="stretch", type="primary", disabled=not st.session_state.get("terms_accepted", False)):
                if not name or not email or not password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif not validate_email(email):
                    st.error("Invalid email address format. Please enter a valid email (e.g., name@company.com).")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    is_strong, strength_msg = validate_password_strength(password)
                    if not is_strong:
                        st.error(strength_msg)
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
                    
            st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)
            if st.button("Already have an account? Sign In", width="stretch"):
                st.session_state["auth_mode"] = "signin"
                st.rerun()
