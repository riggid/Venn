import pandas as pd
import requests
from typing import Dict, Optional, List, Any
from .meeting_optimizer import compute_equal_time_location

# Category mapping: display name -> query term for OSM
CATEGORY_MAP = {
    "Restaurant": "restaurant",
    "Coffee": "cafe",
    "Park": "park",
    "Bar": "bar",
    "Cafe": "cafe"
}

# Cache for places search results
# Key format: f"{center_lat:.6f}_{center_lng:.6f}_{category_name}"
places_cache: Dict[str, list] = {}


def get_places_cache_key(center_point: tuple, category_name: str) -> str:
    """Generate cache key for places search."""
    return f"{center_point[0]:.6f}_{center_point[1]:.6f}_{category_name}"


def search_osm_places(lat: float, lon: float, query: str, radius_km: int = 2) -> List[Dict[str, Any]]:
    """
    Search nearby places using OpenStreetMap Nominatim API.
    """
    # Convert radius (km) into degrees (approx.)
    # 1 degree latitude ≈ 111km
    delta = radius_km / 111

    # Create a bounding box
    lat_min = lat - delta
    lat_max = lat + delta
    lon_min = lon - delta
    lon_max = lon + delta

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "bounded": 1,
        "limit": 15,  # Fetch slightly more to account for filtering
        "viewbox": f"{lon_min},{lat_max},{lon_max},{lat_min}"  # Note: order matters for Nominatim
    }

    # Nominatim requires a User-Agent
    headers = {
        "User-Agent": "MeetingPointFinder/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"OSM Search failed: {e}")
        return []
    return []


def find_places_by_category(users_df,
                            category_name="Restaurant",
                            api_filter=None):
    """
    Find places of a specific category near the optimal meeting point using OSM.
    
    Process:
    1. Finds fair meeting point using optimization algorithm.
    2. Searches for places using OpenStreetMap (Nominatim).
    3. Filters results to remove irrelevant matches (e.g. hotels in restaurant search).
    
    Args:
        users_df: DataFrame with user locations
        category_name: Display name of category
        api_filter: Ignored (legacy argument)
    
    Returns:
        List of places matching the category.
    """

    # --- STEP 1: OPTIMIZATION ---
    opt_result = compute_equal_time_location(users_df)
    center_point = opt_result['equal_point']
    
    # Check cache first
    cache_key = get_places_cache_key(center_point, category_name)
    if cache_key in places_cache:
        return places_cache[cache_key]

    # --- STEP 2: SEARCH (OpenStreetMap) ---
    # Get the appropriate query for OSM
    query_term = CATEGORY_MAP.get(category_name, category_name.lower())
    
    osm_results = search_osm_places(
        lat=center_point[0],
        lon=center_point[1],
        query=query_term
    )
    
    final_suggestions = []
    seen_ids = set()

    for item in osm_results:
        display_name = item.get('display_name', '')
        if not display_name:
            continue
            
        # Parse name: usually the first part of the comma-separated string
        short_name = display_name.split(',')[0]
        name_lower = short_name.lower()
        
        # --- STEP 3: FILTERING ---
        # Filter out irrelevant places based on category keywords
        if category_name == "Restaurant":
            exclude_keywords = ['market', 'hotel', 'oyo', 'stay', 'resort', 'lodge', 'hostel']
            if any(keyword in name_lower for keyword in exclude_keywords):
                continue
        elif category_name == "Park":
            exclude_keywords = ['restaurant', 'hotel', 'market', 'dining', 'cafe', 'bar']
            if any(keyword in name_lower for keyword in exclude_keywords):
                continue
        
        # Deduplication
        if short_name not in seen_ids:
            seen_ids.add(short_name)
            
            final_suggestions.append({
                'name': short_name,
                'address': display_name,
                'latitude': float(item.get('lat')),
                'longitude': float(item.get('lon')),
                'found_near': "Optimal Center Point"
            })

    # Cache the results before returning
    result = final_suggestions[:5] if final_suggestions else None
    places_cache[cache_key] = result
    
    return result