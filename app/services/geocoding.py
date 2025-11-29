"""Geocoding service for address to coordinates conversion."""
from typing import Optional, Tuple
from .latlong_api import LatLongAPI
from app.data.credentials import CredentialsManager


class GeocodingService:
    """Service for geocoding addresses to coordinates."""
    
    def __init__(self):
        self.credentials = CredentialsManager()
    
    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for an address using LatLong API."""
        api_key = self.credentials.get_latlong_api_key()
        if not api_key or api_key == "YOUR_LATLONG_API_KEY_HERE":
            return None
        
        api = LatLongAPI(api_key)
        return api.geocode(address)

