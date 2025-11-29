"""Profile page component."""
import streamlit as st
import pandas as pd
from app.data import AccountsRepository
from app.services import GeocodingService


def render_profile():
    """Render the profile page."""
    accounts_repo = AccountsRepository()
    geocoding_service = GeocodingService()
    
    accounts = accounts_repo.load_all()
    user = accounts.get(st.session_state.user_email, {})
    
    st.markdown('<h1 class="hero-title">Your Profile 👤</h1>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Personal Information")
        
        name = st.text_input("Name", value=user.get("name", ""))
        age = st.number_input("Age", min_value=13, max_value=120, value=user.get("age") or 25)
        
        st.markdown("### 📍 Location")
        address = st.text_input(
            "Your Address",
            value=user.get("address", ""),
            placeholder="e.g., MG Road, Bengaluru"
        )
        
        if st.button("Update Location on Map"):
            if address.strip():
                coords = geocoding_service.get_coordinates(address)
                if coords:
                    accounts[st.session_state.user_email]["lat"] = coords[0]
                    accounts[st.session_state.user_email]["lng"] = coords[1]
                    accounts[st.session_state.user_email]["address"] = address
                    accounts_repo.save_all(accounts)
                    st.success("Location updated!")
                    st.rerun()
                else:
                    st.error("Could not find location. Please try a different address.")
            else:
                st.warning("Please enter an address")
    
    with col2:
        st.markdown("### 🚗 Transport Preferences")
        transport_options = ["🚗 Car", "🚌 Bus", "🚇 Metro/Train", "🚲 Bike", "🚶 Walking", "🛺 Auto/Cab"]
        selected_transport = st.multiselect(
            "How do you usually travel?",
            transport_options,
            default=user.get("transport_modes", [])
        )
        
        st.markdown("### 📍 Your Location on Map")
        if user.get("lat") and user.get("lng"):
            map_data = pd.DataFrame({
                'lat': [user["lat"]],
                'lon': [user["lng"]]
            })
            st.map(map_data, zoom=14)
        else:
            st.info("Enter your address and click 'Update Location' to see it on the map")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    if st.button("💾 Save All Changes", use_container_width=True):
        accounts[st.session_state.user_email]["name"] = name
        accounts[st.session_state.user_email]["age"] = age
        accounts[st.session_state.user_email]["address"] = address
        accounts[st.session_state.user_email]["transport_modes"] = selected_transport
        accounts_repo.save_all(accounts)
        st.success("Profile updated successfully! ✨")

