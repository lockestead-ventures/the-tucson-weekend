"""Global configuration for the Tucson Weekend Guide newsletter agent."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env file
load_dotenv()


@dataclass
class Config:
    """All configuration for the pipeline."""

    # Anthropic API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = "claude-opus-4-5"
    ANTHROPIC_MAX_TOKENS: int = 400

    # Airtable
    AIRTABLE_PAT: str = os.getenv("AIRTABLE_PAT", "")
    AIRTABLE_BASE_ID: str = os.getenv("AIRTABLE_BASE_ID", "")
    AIRTABLE_VENUES_TABLE_ID: str = os.getenv("AIRTABLE_VENUES_TABLE_ID", "")
    AIRTABLE_EVENTS_TABLE_ID: str = os.getenv("AIRTABLE_EVENTS_TABLE_ID", "")
    AIRTABLE_BASE_URL: str = "https://api.airtable.com/v0"
    AIRTABLE_META_BASE_URL: str = "https://api.airtable.com/v0/meta/bases"

    # Eventbrite
    EVENTBRITE_API_KEY: str = os.getenv("EVENTBRITE_API_KEY", "")
    EVENTBRITE_BASE_URL: str = "https://www.eventbriteapi.com/v3"

    # Google Places
    GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
    GOOGLE_PLACES_BASE_URL: str = "https://maps.googleapis.com/maps/api/place"

    # Yelp
    YELP_API_KEY: str = os.getenv("YELP_API_KEY", "")
    YELP_BASE_URL: str = "https://api.yelp.com/v3"

    # Beehiiv
    BEEHIIV_API_KEY: str = os.getenv("BEEHIIV_API_KEY", "")
    BEEHIIV_PUB_ID: str = os.getenv("BEEHIIV_PUB_ID", "")
    BEEHIIV_BASE_URL: str = "https://api.beehiiv.com/v2"

    # Tucson geo
    TUCSON_LAT: float = 32.2226
    TUCSON_LON: float = -110.9747
    TUCSON_SEARCH_RADIUS_KM: int = 20

    # Newsletter logic
    RESTAURANTS_TO_SELECT: int = 3
    BARS_TO_SELECT: int = 1
    DEFAULT_COOLDOWN_WEEKS_NORMAL: int = 8
    DEFAULT_COOLDOWN_WEEKS_UNDER_RADAR: int = 12

    # Retry logic
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_SECONDS: float = 2.0

    # Rate limiting
    AIRTABLE_RATE_LIMIT_DELAY: float = 0.25  # seconds between API calls

    # Logging
    LOG_DIR: Path = Path(__file__).parent / "logs"

    # Testing
    DRY_RUN: bool = os.getenv("DRY_RUN", "").lower() == "1"

    def __post_init__(self):
        """Validate that all required credentials are present."""
        required = [
            "ANTHROPIC_API_KEY",
            "AIRTABLE_PAT",
            "AIRTABLE_BASE_ID",
            "AIRTABLE_VENUES_TABLE_ID",
            "AIRTABLE_EVENTS_TABLE_ID",
            "EVENTBRITE_API_KEY",
            "GOOGLE_PLACES_API_KEY",
            "YELP_API_KEY",
            "BEEHIIV_API_KEY",
            "BEEHIIV_PUB_ID",
        ]
        missing = [key for key in required if not getattr(self, key)]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")

        self.LOG_DIR.mkdir(exist_ok=True)


# Global config instance
config = Config()
