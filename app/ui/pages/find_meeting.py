"""Find meeting point page component."""
import streamlit as st
import pandas as pd
from app.services.meeting_optimizer import compute_equal_time_location
from app.services.finding_places import find_places_by_category
from app.data import AccountsRepository, GroupsRepository
from app.ui import create_colored_map


def render_find_meeting():
    """Render the find meeting point page."""
    accounts_repo = AccountsRepository()
    groups_repo = GroupsRepository()
    
    accounts = accounts_repo.load_all()
    groups = groups_repo.load_all()
    
    st.markdown('<h1 class="hero-title">Find Meeting Point 📍</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Discover the fairest meeting location for your group</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    user_groups = groups_repo.get_user_groups(st.session_state.user_email)
    
    if not user_groups:
        st.warning("You need to be in a group to find a meeting point!")
        if st.button("Create a Group →"):
            st.session_state.current_page = "groups"
            st.rerun()
        return
    
    selected_group = st.selectbox(
        "Select a Group",
        list(user_groups.keys()),
        index=0 if not hasattr(st.session_state, 'selected_group') else 
              list(user_groups.keys()).index(st.session_state.get('selected_group', list(user_groups.keys())[0]))
              if st.session_state.get('selected_group') in user_groups else 0
    )
    
    # Clear results if group changed
    if hasattr(st.session_state, 'last_selected_group') and st.session_state.last_selected_group != selected_group:
        result_key = f"meeting_result_{st.session_state.last_selected_group}"
        if result_key in st.session_state:
            st.session_state[result_key] = None
            st.session_state[f"{result_key}_dataset"] = None
            st.session_state[f"{result_key}_member_lats"] = None
            st.session_state[f"{result_key}_member_lngs"] = None
            places_key = f"found_places_{result_key}"
            if places_key in st.session_state:
                st.session_state[places_key] = None
                st.session_state[f"{places_key}_category"] = None
    
    st.session_state.last_selected_group = selected_group
    
    group_data = groups[selected_group]
    members = group_data.get("members", [])
    
    st.markdown(f"### 👥 Group: {selected_group}")
    st.markdown(f"*{group_data.get('vibe', 'Meeting')} with {len(members)} members*")
    
    member_data = []
    member_lats = []
    member_lngs = []
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Members & Locations")
        for member_email in members:
            member = accounts.get(member_email, {})
            name = member.get("name", member_email.split("@")[0])
            addr = member.get("address", "Location not set")
            lat = member.get("lat")
            lng = member.get("lng")
            
            is_you = " (You)" if member_email == st.session_state.user_email else ""
            has_location = "✅" if lat and lng else "❌"
            
            st.markdown(f"""
            <div class="member-card">
                <strong>{name}{is_you}</strong> {has_location}<br>
                <small>📍 {addr}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if lat and lng:
                member_lats.append(lat)
                member_lngs.append(lng)
                member_data.append({
                    'user_id': name,
                    'lat': lat,
                    'lng': lng
                })
    
    with col2:
        st.markdown("### Group Map")
        if member_lats and member_lngs:
            map_data = pd.DataFrame({
                'lat': member_lats,
                'lon': member_lngs
            })
            st.map(map_data, zoom=11)
        else:
            st.info("No member locations available yet")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    if len(member_data) >= 2:
        # Show button only if results haven't been calculated or group changed
        result_key = f"meeting_result_{selected_group}"
        if result_key not in st.session_state or st.session_state[result_key] is None:
            if st.button("🎯 Find Optimal Meeting Point", use_container_width=True):
                with st.spinner("🔍 Analyzing locations and calculating the fairest meeting point..."):
                    try:
                        dataset = pd.DataFrame(member_data)
                        result = compute_equal_time_location(dataset)
                        
                        # Store results in session state
                        st.session_state[result_key] = result
                        st.session_state[f"{result_key}_dataset"] = dataset
                        st.session_state[f"{result_key}_member_lats"] = member_lats
                        st.session_state[f"{result_key}_member_lngs"] = member_lngs
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error calculating meeting point: {str(e)}")
                        st.info("Make sure the LATLONG_API_KEY is set in credentials.json")
        
        # Display results if they exist in session state
        if result_key in st.session_state and st.session_state[result_key] is not None:
            result = st.session_state[result_key]
            dataset = st.session_state[f"{result_key}_dataset"]
            stored_member_lats = st.session_state[f"{result_key}_member_lats"]
            stored_member_lngs = st.session_state[f"{result_key}_member_lngs"]
            
            # Option to recalculate
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Recalculate", key="recalc_meeting"):
                    st.session_state[result_key] = None
                    st.session_state[f"{result_key}_dataset"] = None
                    st.session_state[f"{result_key}_member_lats"] = None
                    st.session_state[f"{result_key}_member_lngs"] = None
                    st.rerun()
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("## 🎯 Optimal Meeting Point Found!")
            
            equal_point = result['equal_point']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="stat-number">{result['avg_time_min']:.0f}</div>
                    <p>Avg. Travel (min)</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="stat-number">{result['equality_score']:.1f}</div>
                    <p>Fairness Score</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="stat-number">{result['time_spread']:.0f}</div>
                    <p>Time Spread (min)</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 📍 Optimal Meeting Point")
            
            # Reconstruct member_data from stored dataset for the map
            map_member_data = []
            if dataset is not None and not dataset.empty:
                for _, row in dataset.iterrows():
                    map_member_data.append({
                        'user_id': row.get('user_id', 'Unknown'),
                        'lat': row.get('lat'),
                        'lng': row.get('lng')
                    })
            
            # Get places if they exist
            places_key = f"found_places_{result_key}"
            places_for_map = st.session_state.get(places_key) if places_key in st.session_state else None
            
            # Create colored map
            colored_map = create_colored_map(
                member_data=map_member_data,
                meeting_point=equal_point,
                places=places_for_map
            )
            
            if colored_map:
                st.pydeck_chart(colored_map)
            else:
                # Fallback to simple map if pydeck fails
                all_lats = stored_member_lats + [equal_point[0]]
                all_lngs = stored_member_lngs + [equal_point[1]]
                map_data = pd.DataFrame({
                    'lat': all_lats,
                    'lon': all_lngs
                })
                st.map(map_data, zoom=12)
            
            # Legend
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                <strong>Map Legend:</strong><br>
                <span style="color: #f59e0b;">🟠 Orange/Amber</span> = Meeting Point<br>
                <span style="color: #10b981;">🟢 Green</span> = Restaurants/Places<br>
                <span style="color: #6366f1;">🔵 Various Colors</span> = Group Members (each person has a unique color)
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            **Coordinates:** {equal_point[0]:.6f}, {equal_point[1]:.6f}
            
            *The orange marker shows the optimal meeting point that minimizes travel inequality!*
            """)
            
            # Display alternative meeting spots
            if 'alternative_spots' in result and result['alternative_spots']:
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown("### 🗺️ Alternative Meeting Spots")
                st.markdown("*Other fair locations nearby if the optimal point doesn't work for your group:*")
                
                alt_cols = st.columns(min(3, len(result['alternative_spots'])))
                for idx, alt_spot in enumerate(result['alternative_spots'][:3]):
                    with alt_cols[idx]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <small>📍 Option {idx+1}</small><br>
                            <div style="font-size: 0.9rem; margin: 0.5rem 0;">
                                <strong>{alt_spot['avg_time']:.0f}</strong> min avg<br>
                                <strong>{alt_spot['equality_score']:.1f}</strong> fairness
                            </div>
                            <small>{alt_spot['lat']:.4f}, {alt_spot['lng']:.4f}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Map of alternatives
                alt_lats = stored_member_lats + [spot['lat'] for spot in result['alternative_spots'][:3]]
                alt_lngs = stored_member_lngs + [spot['lng'] for spot in result['alternative_spots'][:3]]
                
                alt_map_data = pd.DataFrame({
                    'lat': alt_lats,
                    'lon': alt_lngs
                })
                st.map(alt_map_data, zoom=12)
            
            st.markdown("### 👥 Individual Travel Times")
            user_times = result['user_times']
            for _, row in user_times.iterrows():
                deviation = row['travel_time_min'] - result['avg_time_min']
                color = "green" if abs(deviation) < 5 else "orange" if abs(deviation) < 10 else "red"
                st.markdown(f"""
                <div class="member-card" style="border-left-color: {color};">
                    <strong>{row['user_id']}</strong><br>
                    <span style="font-size: 1.2rem;">{row['travel_time_min']:.0f} minutes</span>
                    <small>({'+' if deviation > 0 else ''}{deviation:.0f} from avg)</small>
                </div>
                """, unsafe_allow_html=True)
            
            # --- FIND NEARBY PLACES ---
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("### 🍽️ Nearby Places to Meet")
            
            # Initialize session state for places
            places_key = f"found_places_{result_key}"
            if places_key not in st.session_state:
                st.session_state[places_key] = None
                st.session_state[f"{places_key}_category"] = None
            
            col1, col2 = st.columns([3, 1])
            with col1:
                place_category = st.selectbox("What are you looking for?", 
                    ["Restaurant", "Coffee", "Park", "Bar", "Cafe"], 
                    key=f"place_search_{result_key}")
            with col2:
                if st.session_state[places_key]:
                    if st.button("🔄 Reset", key=f"reset_places_{result_key}"):
                        st.session_state[places_key] = None
                        st.session_state[f"{places_key}_category"] = None
                        st.rerun()
            
            if st.button("🔍 Find Nearby Places", key=f"find_places_{result_key}"):
                with st.spinner(f"Finding {place_category.lower()}s near your meeting point..."):
                    try:
                        places = find_places_by_category(dataset, category_name=place_category)
                        st.session_state[places_key] = places
                        st.session_state[f"{places_key}_category"] = place_category
                        st.rerun()
                    except Exception as e:
                        st.warning(f"Could not find nearby places. Make sure your LatLong API key is set in credentials.json")
            
            # Display stored places if they exist
            if st.session_state[places_key]:
                places = st.session_state[places_key]
                category = st.session_state[f"{places_key}_category"]
                
                if places:
                    # Count places with valid coordinates
                    places_with_coords = [p for p in places if p.get('latitude') and p.get('longitude')]
                    st.success(f"✅ Found {len(places)} {category.lower()}(s)! ({len(places_with_coords)} with map coordinates)")
                    for i, place in enumerate(places, 1):
                        full_text = place.get('name', 'Unknown')
                        parts = full_text.split(',', 1)
                        if len(parts) > 1:
                            display_name = parts[0].strip()
                            display_addr = parts[1].strip()
                        else:
                            display_name = full_text
                            display_addr = "Location details in name"
                        
                        st.markdown(f"""
                        <div class="member-card">
                            <strong>#{i} {display_name}</strong><br>
                            <small>📍 {display_addr}</small><br>
                            <small style="color: #a0a0a0;">Near: {place.get('found_near', 'Meeting point')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"No {category.lower()}s found near your meeting point. Try a different category!")
    else:
        st.warning(f"Need at least 2 members with locations set. Currently have {len(member_data)} member(s) with locations.")
        st.info("Ask your group members to set their locations in their profiles!")

