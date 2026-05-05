"""Club Congress Hotel crawler."""

import logging
import re
from datetime import date
from typing import Any, Dict, List

from dateutil import parser as dateutil_parser

from crawlers.base import BaseCrawler

logger = logging.getLogger(__name__)


class ClubCongressCrawler(BaseCrawler):
    """Crawl events from Club Congress Hotel."""

    def crawl(
        self, weekend_start: date, weekend_end: date
    ) -> List[Dict[str, Any]]:
        """
        Fetch events from Club Congress.

        Args:
            weekend_start: Friday date
            weekend_end: Sunday date

        Returns:
            List of normalized event dicts
        """
        events = []

        try:
            url = "https://clubcongress.com/events/"
            html = self._get(url)
            soup = self._parse_html(html)

            # Find Tribe Events
            event_elements = soup.select(
                ".tribe-events-loop article, "
                ".tribe-events-list .type-tribe_events"
            )

            for event_elem in event_elements:
                try:
                    # Event title & link
                    title_link = event_elem.select_one(".tribe-event-url")
                    if not title_link:
                        continue

                    event_name = title_link.get_text(strip=True)
                    event_url = title_link.get("href", "")

                    # Date
                    date_elem = event_elem.select_one(
                        ".tribe-events-schedule abbr[title]"
                    )
                    event_date_str = ""

                    if date_elem:
                        date_attr = date_elem.get("title", "")
                        if date_attr:
                            try:
                                parsed_date = dateutil_parser.parse(date_attr)
                                event_date_str = parsed_date.date().isoformat()
                            except:
                                pass

                    if not event_date_str:
                        continue

                    # Time
                    event_time = ""
                    time_match = re.search(
                        r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))",
                        event_elem.get_text(),
                    )
                    if time_match:
                        event_time = time_match.group(1)

                    # Determine venue (Club Congress has multiple spaces)
                    # For now, assume main Hotel Congress unless otherwise specified
                    venue_name = "Club Congress"
                    venue_address = "311 E Congress St, Tucson, AZ 85701"

                    # Description
                    desc_elem = event_elem.select_one(".tribe-events-excerpt")
                    description = (
                        desc_elem.get_text(strip=True) if desc_elem else ""
                    )

                    # Image
                    img_elem = event_elem.select_one("img")
                    image_url = img_elem.get("src", "") if img_elem else ""

                    event_dict = {
                        "name": event_name,
                        "source": "Club Congress",
                        "source_event_id": f"clubcongress_{event_url}",
                        "event_url": event_url,
                        "venue_name": venue_name,
                        "venue_address": venue_address,
                        "event_date": event_date_str,
                        "event_end_date": event_date_str,
                        "event_time": event_time,
                        "description": description,
                        "category": "Other",
                        "price": "TBD",
                        "image_url": image_url,
                        "weekend_of": weekend_start.isoformat(),
                    }
                    events.append(event_dict)

                except Exception as e:
                    logger.warning(f"Error parsing Club Congress event: {e}")

        except Exception as e:
            logger.error(f"Error crawling Club Congress: {e}")

        logger.info(
            f"ClubCongressCrawler: found {len(events)} events "
            f"({weekend_start} - {weekend_end})"
        )
        return events
