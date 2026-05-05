"""Airtable Events table management."""

import logging
from datetime import date
from typing import Any, Dict, List

from airtable.client import AirtableClient
from config import config

logger = logging.getLogger(__name__)


class EventsManager:
    """Manage Events table in Airtable."""

    def __init__(self):
        """Initialize with Airtable client."""
        self.client = AirtableClient()
        self.table_id = config.AIRTABLE_EVENTS_TABLE_ID

    def store_events(self, events: List[Dict[str, Any]]) -> List[str]:
        """
        Store or update events in the Events table (upsert by Source Event ID).

        Args:
            events: List of event dicts

        Returns:
            List of Airtable record IDs
        """
        record_ids = []

        for event in events:
            try:
                source_event_id = event.get("source_event_id", "")
                if not source_event_id:
                    logger.warning("Event missing source_event_id, skipping")
                    continue

                # Prepare fields for Airtable
                fields = {
                    "Name": event.get("name", "Unknown")[:999],
                    "Source": event.get("source", ""),
                    "Source Event ID": source_event_id,
                    "Event URL": event.get("event_url", "")[:999],
                    "Venue Name": event.get("venue_name", "")[:999],
                    "Venue Address": event.get("venue_address", "")[:999],
                    "Event Date": event.get("event_date", ""),
                    "Event End Date": event.get("event_end_date", ""),
                    "Event Time": event.get("event_time", "")[:99],
                    "Description": event.get("description", ""),
                    "Category": event.get("category", "Other"),
                    "Price": event.get("price", "")[:99],
                    "Image URL": event.get("image_url", "")[:999],
                    "Weekend Of": event.get("weekend_of", ""),
                    "Crawled Date": date.today().isoformat(),
                }

                # Upsert: check if exists by Source Event ID
                filter_formula = f'{{Source Event ID}}="{source_event_id}"'
                record = self.client.upsert_record(
                    self.table_id, filter_formula, fields
                )

                if "id" in record:
                    record_ids.append(record["id"])

            except Exception as e:
                logger.error(f"Error storing event {event.get('name')}: {e}")

        logger.info(f"Stored/updated {len(record_ids)} events")
        return record_ids

    def get_events_for_weekend(self, weekend_of: str) -> List[Dict[str, Any]]:
        """
        Get all events for a given weekend.

        Args:
            weekend_of: YYYY-MM-DD date string

        Returns:
            List of event records
        """
        filter_formula = f'{{Weekend Of}}="{weekend_of}"'
        records = self.client.list_records(self.table_id, filter_formula=filter_formula)
        return records

    def mark_event_used(
        self, record_id: str, issue_date: str, was_headline: bool = False
    ) -> None:
        """
        Mark an event as used in a newsletter issue.

        Args:
            record_id: Airtable record ID
            issue_date: YYYY-MM-DD of the weekend it was used
            was_headline: True if this was the headline event
        """
        fields = {
            "Featured In Issue": issue_date,
            "Was Headline": was_headline,
        }
        self.client.update_record(self.table_id, record_id, fields)
        logger.info(f"Marked event {record_id} as used in {issue_date}")

    def get_used_event_ids(self) -> List[str]:
        """
        Get list of Source Event IDs that have been featured.

        Returns:
            List of source event IDs (e.g. "eventbrite_12345")
        """
        # Filter for records where Featured In Issue is not blank
        filter_formula = 'NOT({Featured In Issue}="")'
        records = self.client.list_records(self.table_id, filter_formula=filter_formula)

        used_ids = [
            r.get("fields", {}).get("Source Event ID", "")
            for r in records
            if r.get("fields", {}).get("Source Event ID")
        ]
        logger.info(f"Found {len(used_ids)} previously featured events")
        return used_ids
