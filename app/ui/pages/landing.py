"""Landing page component."""
import streamlit as st
from app.services import OAuthService


def render_landing_page():
    """Render the landing page."""
    try:
        oauth_service = OAuthService()
    except Exception as e:
        st.error(f"Error initializing OAuth service: {e}")
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="compass-icon">🧭</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="hero-title">Social Compass</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle">Find the perfect meeting spot that\'s fair for everyone</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📍 Smart Location Finding</h3>
            <p>Our algorithm finds meeting points that minimize travel time inequality for all participants.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>👥 Group Management</h3>
            <p>Create groups, add friends, and plan meetups with ease. Everyone's location matters.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>⚖️ Fair for All</h3>
            <p>Get detailed fairness metrics showing travel times for each member of your group.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    st.markdown("### 🔐 Sign In with Google")
    google_oauth_url = oauth_service.get_oauth_url()
    
    if google_oauth_url:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <a href="{google_oauth_url}" target="_self" class="google-signin-btn">
                🔐 Sign In with Google
            </a>
            """, unsafe_allow_html=True)
        
        st.markdown("<p style='text-align: center; color: #a0a0a0;'>*Securely sign in using your Google account*</p>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Google OAuth not configured. Please set credentials in credentials.json.")

