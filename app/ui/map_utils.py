"""Map utilities for creating colored visualizations."""
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any

try:
    import pydeck as pdk
    PYDECK_AVAILABLE = True
except ImportError:
    PYDECK_AVAILABLE = False
    pdk = None


def create_colored_map(
    member_data: List[Dict],
    meeting_point: Tuple[float, float],
    places: Optional[List[Dict]] = None
) -> Optional[Any]:
    """
    Create a pydeck map with colored markers:
    - Each person gets a unique color
    - Meeting point gets a specific color (red/pink)
    - Restaurants get another color (green/orange)
    """
    if not PYDECK_AVAILABLE:
        return None
    
    # Color palette for people (distinct colors - NOT red)
    person_colors = [
        [99, 102, 241],   # Indigo #6366f1
        [139, 92, 246],   # Purple #8b5cf6
        [59, 130, 246],   # Blue #3b82f6
        [16, 185, 129],   # Green #10b981
        [245, 158, 11],   # Yellow/Amber #f59e0b
        [236, 72, 153],   # Pink #ec4899
        [14, 165, 233],   # Sky Blue #0ea5e9
        [168, 85, 247],   # Violet #a855f7
    ]
    
    # Meeting point color (bright orange/gold - distinct from people)
    meeting_color = [245, 158, 11, 255]  # Amber/Orange #f59e0b - distinct meeting point
    
    # Restaurant/Places color (green)
    restaurant_color = [16, 185, 129, 200]  # Green #10b981 with alpha
    
    layers = []
    
    # Add person markers with unique colors
    if member_data:
        person_points = []
        for idx, member in enumerate(member_data):
            color = person_colors[idx % len(person_colors)]
            # Ensure color has 4 elements [R, G, B, A]
            if len(color) == 3:
                color = color + [200]  # Add alpha
            person_points.append({
                'lat': member['lat'],
                'lon': member['lng'],
                'name': member['user_id'],
                'color_rgba': color
            })
        
        if person_points:
            person_df = pd.DataFrame(person_points)
            person_layer = pdk.Layer(
                'ScatterplotLayer',
                data=person_df,
                get_position='[lon, lat]',
                get_fill_color='color_rgba',
                get_radius=250,
                pickable=True,
                radius_min_pixels=8,
                radius_max_pixels=15,
            )
            layers.append(person_layer)
    
    # Add meeting point marker (orange/amber - distinct)
    if meeting_point:
        meeting_df = pd.DataFrame([{
            'lat': meeting_point[0],
            'lon': meeting_point[1],
            'name': 'Meeting Point',
            'color_rgba': meeting_color
        }])
        meeting_layer = pdk.Layer(
            'ScatterplotLayer',
            data=meeting_df,
            get_position='[lon, lat]',
            get_fill_color='color_rgba',
            get_radius=350,
            pickable=True,
            radius_min_pixels=12,
            radius_max_pixels=20,
        )
        layers.append(meeting_layer)
    
    # Add restaurant/place markers
    if places:
        restaurant_points = []
        for place in places:
            try:
                # Try different possible coordinate field names
                lat = place.get('latitude') or place.get('lat')
                lng = place.get('longitude') or place.get('lon') or place.get('lng')
                
                # Convert to float if they're strings
                if lat:
                    lat = float(lat)
                if lng:
                    lng = float(lng)
                
                # Only add if we have valid coordinates
                if lat and lng and lat != 0 and lng != 0:
                    restaurant_points.append({
                        'lat': lat,
                        'lon': lng,
                        'name': place.get('name', 'Place'),
                        'color_rgba': restaurant_color
                    })
            except (ValueError, TypeError):
                continue
        
        if restaurant_points:
            restaurant_df = pd.DataFrame(restaurant_points)
            restaurant_layer = pdk.Layer(
                'ScatterplotLayer',
                data=restaurant_df,
                get_position='[lon, lat]',
                get_fill_color='color_rgba',
                get_radius=200,
                pickable=True,
                radius_min_pixels=6,
                radius_max_pixels=12,
            )
            layers.append(restaurant_layer)
    
    # Calculate center point
    all_lats = []
    all_lngs = []
    if member_data:
        all_lats.extend([m['lat'] for m in member_data])
        all_lngs.extend([m['lng'] for m in member_data])
    if meeting_point:
        all_lats.append(meeting_point[0])
        all_lngs.append(meeting_point[1])
    if places:
        for place in places:
            try:
                # Try different possible coordinate field names
                lat = place.get('latitude') or place.get('lat')
                lng = place.get('longitude') or place.get('lon') or place.get('lng')
                
                if lat and lng:
                    lat = float(lat)
                    lng = float(lng)
                    if lat != 0 and lng != 0:
                        all_lats.append(lat)
                        all_lngs.append(lng)
            except (ValueError, TypeError):
                pass
    
    if all_lats and all_lngs:
        center_lat = sum(all_lats) / len(all_lats)
        center_lon = sum(all_lngs) / len(all_lngs)
    else:
        return None
    
    # Create the map
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=12,
        pitch=0
    )
    
    # Use a map style that's easier to see
    # Try light style first, fallback to dark if needed
    deck = pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v12',  # Streets style for better visibility
        initial_view_state=view_state,
        layers=layers,
        tooltip={
            'text': '{name}'
        }
    )
    
    return deck

