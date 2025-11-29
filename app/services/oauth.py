"""OAuth service for Google authentication."""
import requests
from urllib.parse import quote
from typing import Optional, Dict
from app.data.credentials import CredentialsManager


class OAuthService:
    """Service for handling Google OAuth authentication."""
    
    def __init__(self):
        self.credentials = CredentialsManager()
    
    def get_oauth_url(self) -> Optional[str]:
        """Generate Google OAuth URL."""
        client_id = self.credentials.get_google_client_id()
        if not client_id:
            return None
        
        redirect_uri = self.credentials.get_redirect_uri()
        scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
        
        scope_str = " ".join(scopes)
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={quote(redirect_uri)}&"
            f"response_type=code&"
            f"scope={quote(scope_str)}&"
            f"access_type=offline"
        )
    
    def exchange_code_for_token(self, code: str) -> Optional[str]:
        """Exchange OAuth code for access token."""
        client_id = self.credentials.get_google_client_id()
        client_secret = self.credentials.get_google_client_secret()
        redirect_uri = self.credentials.get_redirect_uri()
        
        if not client_id or not client_secret:
            return None
        
        try:
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri
                }
            )
            return token_response.json().get("access_token")
        except Exception:
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get user info from Google using access token."""
        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.json()
        except Exception:
            return None

