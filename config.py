"""
Configuration management for Teams Transcript Scraper
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""

    # Microsoft Graph API settings
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    TENANT_ID = os.getenv('TENANT_ID')

    # Graph API endpoints
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"

    # Required scopes for accessing Teams data
    SCOPES = [
        "https://graph.microsoft.com/.default"
    ]

    # Output configuration
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', './transcripts'))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.CLIENT_ID:
            raise ValueError("CLIENT_ID not set in .env file")
        if not cls.CLIENT_SECRET:
            raise ValueError("CLIENT_SECRET not set in .env file")
        if not cls.TENANT_ID:
            raise ValueError("TENANT_ID not set in .env file")

        # Create output directory if it doesn't exist
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        return True
