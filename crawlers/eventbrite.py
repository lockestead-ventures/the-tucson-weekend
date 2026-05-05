"""Eventbrite REST API crawler."""

import logging
from datetime import date
from typing import Any, Dict, List
from urllib.parse import urljoin

from crawlers.base import BaseCrawler
from config import config

logger = logging.getLogger(__name__)


class EventbriteCrawler(BaseCrawler):
    """Crawl events from Eventbrite API."""

    def crawl(
        self, weekend_start: date, weekend_end: date
    ) -> List[Dict[str, Any]]:
        """
        Fetch events from Eventbrite for the given weekend.

        Args:
            weekend_start: Friday date (YYYY-MM-DD)
            weekend_end: Sunday date (YYYY-MM-DD)

        Returns:
            List of normalized event dicts
        """
        events = []
        page = 1

        start_datetime = f"{weekend_start}T00:00:00"
        end_datetime = f"{weekend_end}T23:59:59"

        while True:
            try:
                url = f"{config.EVENTBRITE_BASE_URL}/events/search/"
                headers = {"Authorization": f"Bearer {config.EVENTBRITE_API_KEY}"}
                params = {
                    "location.address": "Tucson, AZ",
                    "location.latitude": config.TUCSON_LAT,
                    "location.longitude": config.TUCSON_LON,
                    "location.within": f"{config.TUCSON_SEARCH_RADIUS_KM}km",
                    "start_date.range_start": start_datetime,
                    "start_date.range_end": end_datetime,
                    "expand": "venue,category",
                    "sort_by": "best",
                    "page_size": 50,
                    "page": page,
                }

                html = self._get(url, params=params, headers=headers)
                import json

                data = json.loads(html)
                page_events = data.get("events", [])

                for event in page_events:
                    # Skip private events
                    if not event.get("listed", True):
                        continue

                    # Parse the event
                    try:
                        event_dict = {
                            "name": event.get("name", {}).get("text", "Unknown"),
                            "source": "Eventbrite",
                            "source_event_id": f"eventbrite_{event.get('id')}",
                            "event_url": event.get("url", ""),
                            "venue_name": event.get("venue", {})
                            .get("name", "TBD"),
                            "venue_address": event.get("venue", {})
                            .get("address", {})
                            .get("localized_address_display", ""),
                            "event_date": event.get("start", {}).get("local", "").split("T")[0],
                            "event_end_date": event.get("end", {})
                            .get("local", "")
                            .split("T")[0],
                            "event_time": event.get("start", {})
                            .get("local", "")
                            .split("T")[1][:5]
                            if "T" in event.get("start", {}).get("local", "")
                            else "",
                            "description": event.get("description", {}).get("text", ""),
                            "category": event.get("category", {}).get("name", "Other"),
                            "price": "Free"
                            if event.get("is_free")
                            else "Paid",
                            "image_url": event.get("logo", {})
                            .get("original", {})
                            .get("url", ""),
                            "weekend_of": weekend_start.isoformat(),
                        }
                        events.append(event_dict)
                    except Exception as e:
                        logger.warning(f"Error parsing Eventbrite event: {e}")

                # Check pagination
                if not data.get("pagination", {}).get("has_more_items"):
                    break

                page += 1

            except Exception as e:
                logger.error(f"Error crawling Eventbrite page {page}: {e}")
                break

        logger.info(
            f"EventbriteCrawler: found {len(events)} events "
            f"({weekend_start} - {weekend_end})"
        )
        return events
