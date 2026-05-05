"""Airtable Venues table management."""

import logging
import random
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from airtable.client import AirtableClient
from config import config

logger = logging.getLogger(__name__)


class VenuesManager:
    """Manage Venues table in Airtable."""

    def __init__(self):
        """Initialize with Airtable client."""
        self.client = AirtableClient()
        self.table_id = config.AIRTABLE_VENUES_TABLE_ID

    def get_eligible_venues(
        self, category: str, weekend_of: date, cooldown_override: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get venues eligible for selection (respecting cooldown).

        Args:
            category: "Restaurant", "Bar", or "Under the Radar"
            weekend_of: The Saturday date of the target weekend
            cooldown_override: Optional override for cooldown weeks (for fallback)

        Returns:
            Shuffled list of eligible venue records
        """
        # Filter: Active = true, Category = category
        filter_formula = f'AND({{Active}}=TRUE(),{{Category}}="{category}")'
        records = self.client.list_records(self.table_id, filter_formula=filter_formula)

        eligible = []

        for record in records:
            fields = record.get("fields", {})

            # Determine cooldown threshold
            stored_cooldown = fields.get("Cooldown Weeks")
            if cooldown_override:
                cooldown_weeks = cooldown_override
            elif stored_cooldown:
                cooldown_weeks = int(stored_cooldown)
            else:
                # Use default from config
                if category == "Under the Radar":
                    cooldown_weeks = config.DEFAULT_COOLDOWN_WEEKS_UNDER_RADAR
                else:
                    cooldown_weeks = config.DEFAULT_COOLDOWN_WEEKS_NORMAL

            # Check cooldown
            last_featured_str = fields.get("Last Featured Date")
            if last_featured_str:
                try:
                    last_featured = date.fromisoformat(last_featured_str)
                    weeks_since = (date.today() - last_featured).days // 7
                    if weeks_since < cooldown_weeks:
                        logger.debug(
                            f"Venue {fields.get('Name')} in cooldown "
                            f"({weeks_since}w < {cooldown_weeks}w)"
                        )
                        continue
                except:
                    pass

            # This venue is eligible
            record["airtable_id"] = record.get("id")
            eligible.append(record)

        logger.info(
            f"Found {len(eligible)} eligible {category} venues (cooldown: {cooldown_weeks}w)"
        )

        # Shuffle and return
        random.shuffle(eligible)
        return eligible

    def mark_venue_featured(self, record_id: str, weekend_of: str) -> None:
        """
        Mark a venue as featured in a newsletter.

        Args:
            record_id: Airtable record ID
            weekend_of: YYYY-MM-DD of the weekend it was used
        """
        # Get current record to increment Times Featured
        records = self.client.list_records(
            self.table_id,
            filter_formula=f'{{Name}}="{record_id}"',  # This is hacky; ideally we'd fetch by ID
        )

        times_featured = 1
        if records:
            times_featured = int(records[0].get("fields", {}).get("Times Featured", 0)) + 1

        fields = {
            "Last Featured Date": weekend_of,
            "Times Featured": times_featured,
        }
        self.client.update_record(self.table_id, record_id, fields)
        logger.info(f"Marked venue {record_id} as featured on {weekend_of}")

    def get_venue_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a venue record by ID."""
        try:
            url = f"{self.client.base_url}/{self.client.base_id}/{self.table_id}/{record_id}"
            import requests
            response = requests.get(url, headers=self.client._headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching venue {record_id}: {e}")
            return None
