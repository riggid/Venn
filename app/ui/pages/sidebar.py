"""Sidebar navigation component."""
import streamlit as st
from app.data import AccountsRepository


def render_sidebar():
    """Render the sidebar navigation."""
    accounts_repo = AccountsRepository()
    
    with st.sidebar:
        st.markdown("## 🧭 Social Compass")
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        accounts = accounts_repo.load_all()
        user = accounts.get(st.session_state.user_email, {})
        st.markdown(f"### 👋 Hi, {user.get('name', 'Friend')}!")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        if st.button("🏠 Dashboard", key="nav_dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        if st.button("👤 My Profile", key="nav_profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()
        
        if st.button("👥 My Groups", key="nav_groups", use_container_width=True):
            st.session_state.current_page = "groups"
            st.rerun()
        
        if st.button("📍 Find Meeting Point", key="nav_find", use_container_width=True):
            st.session_state.current_page = "find_meeting"
            st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        if st.button("🚪 Sign Out", key="signout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.current_page = "home"
            st.rerun()

