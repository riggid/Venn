"""Dashboard page component."""
import streamlit as st
import pandas as pd
from app.data import AccountsRepository, GroupsRepository


def render_dashboard():
    """Render the dashboard page."""
    accounts_repo = AccountsRepository()
    groups_repo = GroupsRepository()
    
    accounts = accounts_repo.load_all()
    groups = groups_repo.load_all()
    user = accounts.get(st.session_state.user_email, {})
    
    st.markdown(f'<h1 class="hero-title">Welcome back, {user.get("name", "Friend")}! 🧭</h1>', unsafe_allow_html=True)
    
    user_groups = groups_repo.get_user_groups(st.session_state.user_email)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="stat-number">{len(user_groups)}</div>
            <p>Groups</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="stat-number">{len(accounts)}</div>
            <p>Community Members</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        location_set = "✅" if user.get("address") else "❌"
        st.markdown(f"""
        <div class="metric-card">
            <div class="stat-number">{location_set}</div>
            <p>Location Set</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📍 Your Location")
        if user.get("lat") and user.get("lng"):
            map_data = pd.DataFrame({
                'lat': [user["lat"]],
                'lon': [user["lng"]]
            })
            st.map(map_data, zoom=12)
            st.markdown(f"📌 **{user.get('address', 'Not set')}**")
        else:
            st.info("Set your location in your profile to see it on the map!")
            if st.button("Set Location →"):
                st.session_state.current_page = "profile"
                st.rerun()
    
    with col2:
        st.markdown("### 👥 Your Groups")
        if user_groups:
            for group_name in list(user_groups.keys())[:5]:
                group_data = groups[group_name]
                member_count = len(group_data.get("members", []))
                st.markdown(f"""
                <div class="group-card">
                    <h4>{group_name}</h4>
                    <p>👥 {member_count} members • {group_data.get('vibe', 'Casual meetup')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("You haven't joined any groups yet!")
            if st.button("Create or Join a Group →"):
                st.session_state.current_page = "groups"
                st.rerun()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📍 Find Meeting Point", key="quick_find", use_container_width=True):
            st.session_state.current_page = "find_meeting"
            st.rerun()
    with col2:
        if st.button("➕ Create Group", key="quick_group", use_container_width=True):
            st.session_state.current_page = "groups"
            st.rerun()
    with col3:
        if st.button("👤 Update Profile", key="quick_profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()

