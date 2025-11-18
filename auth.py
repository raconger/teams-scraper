"""
Microsoft Graph API Authentication using MSAL
"""
import msal
import pickle
from pathlib import Path
from config import Config


class GraphAuthenticator:
    """Handles authentication with Microsoft Graph API"""

    def __init__(self, cache_file="token_cache.bin"):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
        self.app = msal.ConfidentialClientApplication(
            Config.CLIENT_ID,
            authority=Config.AUTHORITY,
            client_credential=Config.CLIENT_SECRET,
            token_cache=self.cache
        )

    def _load_cache(self):
        """Load token cache from file"""
        cache = msal.SerializableTokenCache()
        if self.cache_file.exists():
            with open(self.cache_file, 'rb') as f:
                cache.deserialize(pickle.load(f))
        return cache

    def _save_cache(self):
        """Save token cache to file"""
        if self.cache.has_state_changed:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache.serialize(), f)

    def get_access_token(self):
        """
        Get access token for Microsoft Graph API
        Uses cached token if available, otherwise acquires new one
        """
        # Try to get token from cache first
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(Config.SCOPES, account=accounts[0])
            if result and "access_token" in result:
                return result["access_token"]

        # Acquire new token using client credentials flow
        result = self.app.acquire_token_for_client(scopes=Config.SCOPES)

        if "access_token" in result:
            self._save_cache()
            return result["access_token"]
        else:
            error = result.get("error")
            error_description = result.get("error_description")
            raise Exception(f"Authentication failed: {error} - {error_description}")
