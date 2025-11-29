"""
Main entry point for Social Compass application.
Run this from the root directory: streamlit run main.py
"""
import streamlit as st
from datetime import datetime

# Import data repositories
from app.data import AccountsRepository, GroupsRepository, CredentialsManager

# Import services
from app.services import OAuthService, GeocodingService

# Import UI components
from app.ui import CUSTOM_CSS

# Import page components
from app.ui.pages import (
    render_landing_page,
    render_sidebar,
    render_onboarding,
    render_dashboard,
    render_profile,
    render_groups,
    render_find_meeting
)

# Configure page
st.set_page_config(
    page_title="Social Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS with error handling
try:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
except Exception as e:
    st.warning(f"CSS loading issue: {e}")
    # Fallback simple CSS
    st.markdown("""
    <style>
    body { background: #0d1b2a; color: white; }
    .stApp { background: #0d1b2a; }
    </style>
    """, unsafe_allow_html=True)

# Initialize repositories and services (only once)
if "repos_initialized" not in st.session_state:
    st.session_state.accounts_repo = AccountsRepository()
    st.session_state.groups_repo = GroupsRepository()
    st.session_state.credentials = CredentialsManager()
    st.session_state.oauth_service = OAuthService()
    st.session_state.geocoding_service = GeocodingService()
    st.session_state.repos_initialized = True

# Use session state repositories
accounts_repo = st.session_state.accounts_repo
groups_repo = st.session_state.groups_repo
credentials = st.session_state.credentials
oauth_service = st.session_state.oauth_service
geocoding_service = st.session_state.geocoding_service

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 0


def handle_oauth_callback():
    """Handle Google OAuth callback from URL parameters."""
    # Only process OAuth callback once per session
    if "oauth_processed" in st.session_state:
        return
    
    query_params = st.query_params
    
    # If no OAuth params, return early
    if "code" not in query_params and "error" not in query_params:
        return
    
    if "code" in query_params:
        code = query_params["code"]
        access_token = oauth_service.exchange_code_for_token(code)
        
        if access_token:
            user_info = oauth_service.get_user_info(access_token)
            if user_info:
                email = user_info.get("email")
                name = user_info.get("name", email.split("@")[0])
                
                accounts = accounts_repo.load_all()
                
                if email not in accounts:
                    accounts[email] = {
                        "name": name,
                        "email": email,
                        "oauth_provider": "google",
                        "age": None,
                        "address": None,
                        "lat": None,
                        "lng": None,
                        "transport_modes": [],
                        "created_at": datetime.now().isoformat()
                    }
                    accounts_repo.save_all(accounts)
                    st.session_state.onboarding_step = 1
                else:
                    accounts[email]["name"] = name
                    accounts_repo.save_all(accounts)
                
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.current_page = "dashboard"
                st.session_state.oauth_processed = True
                st.query_params.clear()
                st.rerun()
    
    if "error" in query_params:
        st.error(f"Authentication failed: {query_params['error']}")
        st.session_state.oauth_processed = True


def main():
    """Main application entry point."""
    try:
        handle_oauth_callback()
        
        if not st.session_state.authenticated:
            render_landing_page()
        elif st.session_state.current_page == "onboarding":
            render_onboarding()
        else:
            render_sidebar()
            
            if st.session_state.current_page == "dashboard":
                render_dashboard()
            elif st.session_state.current_page == "profile":
                render_profile()
            elif st.session_state.current_page == "groups":
                render_groups()
            elif st.session_state.current_page == "find_meeting":
                render_find_meeting()
            else:
                render_dashboard()
    except Exception as e:
        st.error(f"❌ ERROR: {str(e)}")
        st.exception(e)
        import traceback
        st.code(traceback.format_exc())
        # Show a basic fallback
        st.title("🧭 Social Compass")
        st.write("An error occurred. Please check the terminal for details.")


# Streamlit runs the script top-to-bottom on every rerun
# Call main() to render the appropriate page
try:
    main()
except Exception as e:
    # Show error prominently
    st.error("❌ CRITICAL ERROR")
    st.exception(e)
    import traceback
    st.code(traceback.format_exc())
    st.write("---")
    st.write("**Debug Info:**")
    st.write(f"Authenticated: {st.session_state.get('authenticated', 'NOT SET')}")
    st.write(f"Current Page: {st.session_state.get('current_page', 'NOT SET')}")
    st.write(f"User Email: {st.session_state.get('user_email', 'NOT SET')}")

