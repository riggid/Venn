"""Credentials management."""
import json
from typing import Dict, Optional


class CredentialsManager:
    """Manager for application credentials."""
    
    def __init__(self, file_path: str = "credentials.json"):
        self.file_path = file_path
    
    def load(self) -> Dict:
        """Load credentials from JSON file."""
        try:
            with open(self.file_path, "r") as f:
                creds = json.load(f)
                return creds.get("installed", {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a specific credential value."""
        creds = self.load()
        return creds.get(key, default)
    
    def get_latlong_api_key(self) -> Optional[str]:
        """Get LatLong API key."""
        return self.get("latlong_api_key")
    
    def get_google_client_id(self) -> Optional[str]:
        """Get Google OAuth client ID."""
        return self.get("client_id")
    
    def get_google_client_secret(self) -> Optional[str]:
        """Get Google OAuth client secret."""
        return self.get("client_secret")
    
    def get_redirect_uri(self) -> str:
        """Get OAuth redirect URI."""
        return self.get("redirect_uris", ["http://localhost:5000/"])[0]

