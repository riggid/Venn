import requests

# ==========================================
# LATLONG.AI API WRAPPER
# ==========================================
class LatLongAPI:
    def __init__(self, api_key):
        self.base_url = "https://apihub.latlong.ai/v4"
        self.headers = {"X-Authorization-Token": api_key}

    def _send_request(self, endpoint, params):
        """Internal helper to handle requests and errors"""
        try:
            url = f"{self.base_url}{endpoint}"
            resp = requests.get(url, headers=self.headers, params=params)
            data = resp.json()
            
            # LatLong success codes can be status="success" or code=1001
            if data.get("status") == "success" or data.get("code") == 1001:
                return data.get("data")
            else:
                print(f"⚠️ API Warning ({endpoint}): {data.get('message') or data}")
                return None
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return None

    def autocomplete(self, query, lat=None, lng=None, limit=5):
        """
        Get real-time suggestions as user types.
        """
        params = {"query": query, "limit": limit}
        if lat and lng:
            params["lat"] = lat
            params["long"] = lng 
            
        return self._send_request("/autocomplete.json", params)

    def geocode(self, address):
        """
        Converts Address String -> (Latitude, Longitude)
        """
        data = self._send_request("/geocode.json", {"address": address})
        if data:
            # Returns a tuple (lat, lon)
            return float(data["latitude"]), float(data["longitude"])
        return None

    def autosuggest(self, query, lat=None, lon=None, category=None):
        """
        Finds Points of Interest (POIs) near a specific location.
        
        According to API docs: Query is REQUIRED.
        Results are filtered within 50km radius of lat/lon if provided.
        
        Args:
            query: Required search query string
            lat: Optional latitude for spatial context (50km radius)
            lon: Optional longitude for spatial context (50km radius)
            category: Optional category filter (e.g., "catering" for restaurants)
        """
        params = {
            "query": query,  # Required parameter
            "limit": 10
        }
        if lat is not None:
            params["latitude"] = lat
        if lon is not None:
            params["longitude"] = lon
        if category:
            params["category"] = category

        data = self._send_request("/autosuggest.json", params)
        
        # NORMALIZATION: Flatten nested coordinates
        results = []
        if isinstance(data, list):
            for item in data:
                # Handle inconsistent API spelling (coordintes vs coordinates)
                coords = item.get("coordintes") or item.get("coordinates") or {}
                if coords:
                    lat = coords.get("latitude")
                    lon = coords.get("longitude")
                    # Only add coordinates if they're valid numbers
                    if lat is not None and lon is not None:
                        try:
                            item["latitude"] = float(lat)
                            item["longitude"] = float(lon)
                        except (ValueError, TypeError):
                            # Skip invalid coordinates
                            item["latitude"] = None
                            item["longitude"] = None
                    else:
                        item["latitude"] = None
                        item["longitude"] = None
                else:
                    # No coordinates found
                    item["latitude"] = None
                    item["longitude"] = None
                results.append(item)
        return results

    def landmarks(self, lat, lon):
        """
        Fetch top 4 nearby landmarks instantly.
        Useful for: "What's near me?" or context on a map click.
        """
        # FIXED: Changed parameters from latitude/longitude to lat/lon
        params = {
            "lat": lat,
            "lon": lon
        }
        return self._send_request("/landmarks.json", params)

    def get_route_data(self, start_coords, end_coords):
        """
        Get driving route details (Time, Distance, Geometry).
        """
        # Accepts tuples (lat, lon) or strings "lat,lon"
        if isinstance(start_coords, tuple): start_coords = f"{start_coords[0]},{start_coords[1]}"
        if isinstance(end_coords, tuple): end_coords = f"{end_coords[0]},{end_coords[1]}"

        params = {
            "origin": start_coords,
            "destination": end_coords
        }
        return self._send_request("/directions.json", params)

    def get_map_tile_html(self, lat, lon, zoom=15, mode="point"):
        """
        Returns full HTML content for an embeddable map.
        Endpoints: https://naksha.latlong.ai/tiles
        """
        url = "https://naksha.latlong.ai/tiles"
        params = {
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "mode": mode, # 'tile' or 'point'
            "pan": "On",
            "zoom_control": "On"
        }
        try:
            # This endpoint returns HTML, not JSON, and uses a different base URL
            resp = requests.get(url, headers=self.headers, params=params)
            if resp.status_code == 200:
                return resp.text
            else:
                print(f"⚠️ Map Tile Error: {resp.status_code}")
                return None
        except Exception as e:
            print(f"❌ Map Connection Error: {e}")
            return None

    def parse_minutes(self, time_str):
        """Helper: Converts '1 hour, 10 minutes' -> 70 (integer)"""
        if not time_str: return 0
        minutes = 0
        try:
            parts = time_str.split(',')
            for p in parts:
                if 'hour' in p: minutes += int(p.split('hour')[0].strip()) * 60
                if 'minute' in p: minutes += int(p.split('minute')[0].strip())
        except:
            return 0
        return minutes

# ==========================================
# EXAMPLES / TESTS
# ==========================================
if __name__ == "__main__":
    # REPLACE WITH YOUR API KEY
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJUb2tlbklEIjoiMzNmMjY3MTgtMjRiOC00NTFlLWJlMGYtOGZmMzA1ZDI3ZDk5IiwiQ2xpZW50SUQiOiI2YTA3ZDNkMC01MTNkLTRjMTMtYjRjMi04NTdiY2YzNDJiNWIiLCJCdW5pdElEIjozMCwiQXBwTmFtZSI6InBlcyBoYWNrYXRob24gbWFwcy1yZWltYWdpbmVkIiwiQXBwSUQiOjE4Mzk1LCJUaW1lU3RhbXAiOiIyMDI1LTExLTI4IDE3OjEyOjUyIiwiZXhwIjoxNzY0NTIyNzcyfQ.q5AqBLmiB3KlPMt58O5N767uBJ6qNxGmt6X2aYWtrbI"
    
    api = LatLongAPI(API_KEY)
    
    print("--- 1. Testing AUTOCOMPLETE ---")
    # Simulating a user typing "Indira"
    suggestions = api.autocomplete("Indira", limit=3)
    if suggestions:
        print(f"Suggestions found: {len(suggestions)}")
        print(f"Top result: {suggestions[0]['name']}")
    else:
        print("No suggestions.")

    print("\n--- 2. Testing GEOCODE ---")
    # Getting coordinates for "MG Road"
    addr = "MG Road, Bengaluru"
    coords_start = api.geocode(addr)
    if coords_start:
        print(f"Coordinates for '{addr}': {coords_start}")
    else:
        print("Geocoding failed.")

    print("\n--- 3. Testing LANDMARKS ---")
    # Finding landmarks near the geocoded location
    if coords_start:
        nearby_landmarks = api.landmarks(coords_start[0], coords_start[1])
        if nearby_landmarks:
            print(f"Found {len(nearby_landmarks)} landmarks near {addr}:")
            for lm in nearby_landmarks:
                print(f" - {lm.get('name')}")
        else:
            print("No landmarks found nearby.")

    print("\n--- 4. Testing AUTOSUGGEST ---")
    # Searching for "Pizza" near MG Road
    if coords_start:
        places = api.autosuggest("Pizza", coords_start[0], coords_start[1])
        if places:
            top_place = places[0]
            print(f"Found {len(places)} Pizza places.")
            print(f"Top pick: {top_place.get('name')}")
            # Ensure we use float for coordinates
            try:
                t_lat = float(top_place.get('latitude'))
                t_lon = float(top_place.get('longitude'))
                coords_end = (t_lat, t_lon)
                print(f"Coords: {coords_end}")
            except (ValueError, TypeError):
                print("Invalid coordinates in autosuggest result")
                coords_end = None
        else:
            print("No pizza found nearby.")
            coords_end = None

    print("\n--- 5. Testing DIRECTIONS ---")
    # Calculating route from MG Road to the Pizza place
    if coords_start and coords_end:
        route = api.get_route_data(coords_start, coords_end)
        if route:
            raw_time = route.get('time')
            mins = api.parse_minutes(raw_time)
            dist = route.get('distance')
            print(f"Route Found!")
            print(f"Distance: {dist}")
            print(f"Time: {raw_time} ({mins} mins)")
        else:
            print("Could not calculate route.")

    print("\n--- 6. Testing MAP TILES ---")
    # This will save an HTML file to your computer
    if coords_start:
        print("Fetching Map HTML...")
        map_html = api.get_map_tile_html(coords_start[0], coords_start[1], zoom=15, mode="point")
        if map_html:
            filename = "latlong_map_test.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(map_html)
            print(f"✅ Map saved to '{filename}'. Open this file in your browser to see the map!")
        else:
            print("Failed to fetch map tiles.")