"""Onboarding page component."""
import streamlit as st
from app.data import AccountsRepository
from app.services import GeocodingService


def render_onboarding():
    """Render the onboarding flow."""
    accounts_repo = AccountsRepository()
    geocoding_service = GeocodingService()
    
    st.markdown('<h1 class="hero-title">Welcome to Social Compass! 🧭</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Let\'s set up your profile so we can find the best meeting spots for you</p>', unsafe_allow_html=True)
    
    progress = st.session_state.onboarding_step / 3
    st.progress(progress)
    st.markdown(f"**Step {st.session_state.onboarding_step} of 3**")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    if st.session_state.onboarding_step == 1:
        accounts = accounts_repo.load_all()
        user = accounts.get(st.session_state.user_email, {})
        
        st.markdown("### 📍 Where are you located?")
        st.markdown("*This helps us calculate fair meeting points for your groups*")
        
        address = st.text_input(
            "Your Address or Area",
            value=user.get("address", "") or "",
            placeholder="e.g., MG Road, Bengaluru or your neighborhood"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Skip for now →", key="onboard_skip_1"):
                st.session_state.onboarding_step = 2
                st.rerun()
        with col2:
            if st.button("Next →", key="onboard_next_1"):
                if address.strip():
                    accounts = accounts_repo.load_all()
                    accounts[st.session_state.user_email]["address"] = address
                    coords = geocoding_service.get_coordinates(address)
                    if coords:
                        accounts[st.session_state.user_email]["lat"] = coords[0]
                        accounts[st.session_state.user_email]["lng"] = coords[1]
                        accounts_repo.save_all(accounts)
                        st.session_state.onboarding_step = 2
                        st.rerun()
                    else:
                        accounts_repo.save_all(accounts)
                        st.warning("Could not geocode address. You can update this later in your profile.")
                        st.session_state.onboarding_step = 2
                        st.rerun()
                else:
                    st.warning("Please enter your address to continue")
    
    elif st.session_state.onboarding_step == 2:
        accounts = accounts_repo.load_all()
        user = accounts.get(st.session_state.user_email, {})
        
        st.markdown("### 🚗 How do you usually travel?")
        st.markdown("*This helps us estimate travel times accurately*")
        
        transport_options = ["🚗 Car", "🚌 Bus", "🚇 Metro/Train", "🚲 Bike", "🚶 Walking", "🛺 Auto/Cab"]
        current_transport = user.get("transport_modes", [])
        if not isinstance(current_transport, list):
            current_transport = []
        
        selected_transport = st.multiselect(
            "Select your preferred transport modes",
            transport_options,
            default=current_transport
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back", key="onboard_back_2"):
                st.session_state.onboarding_step = 1
                st.rerun()
        with col2:
            if st.button("Next →", key="onboard_next_2"):
                accounts = accounts_repo.load_all()
                accounts[st.session_state.user_email]["transport_modes"] = selected_transport
                accounts_repo.save_all(accounts)
                st.session_state.onboarding_step = 3
                st.rerun()
    
    elif st.session_state.onboarding_step == 3:
        accounts = accounts_repo.load_all()
        user = accounts.get(st.session_state.user_email, {})
        
        st.markdown("### 🎂 A bit more about you")
        st.markdown("*Optional info to personalize your experience*")
        
        current_age = user.get("age")
        age = st.number_input(
            "Your Age",
            min_value=13,
            max_value=120,
            value=current_age if current_age and current_age >= 13 else 25
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back", key="onboard_back_3"):
                st.session_state.onboarding_step = 2
                st.rerun()
        with col2:
            if st.button("Complete Setup ✨", key="onboard_complete"):
                accounts = accounts_repo.load_all()
                accounts[st.session_state.user_email]["age"] = int(age)
                accounts_repo.save_all(accounts)
                st.session_state.onboarding_step = 0
                st.session_state.current_page = "dashboard"
                st.balloons()
                st.rerun()

