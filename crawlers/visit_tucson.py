"""Visit Tucson calendar crawler."""

import logging
import re
from datetime import date
from typing import Any, Dict, List
from urllib.parse import urljoin

from dateutil import parser as dateutil_parser

from crawlers.base import BaseCrawler

logger = logging.getLogger(__name__)


class VisitTucsonCrawler(BaseCrawler):
    """Crawl events from Visit Tucson official calendar."""

    def crawl(
        self, weekend_start: date, weekend_end: date
    ) -> List[Dict[str, Any]]:
        """
        Fetch events from Visit Tucson calendar.

        Args:
            weekend_start: Friday date
            weekend_end: Sunday date

        Returns:
            List of normalized event dicts
        """
        events = []

        try:
            url = "https://visittucson.org/events/"
            html = self._get(url)
            soup = self._parse_html(html)

            # Look for event cards in the carousel
            # SimpleView typically renders event cards as <a> tags in a carousel
            event_links = soup.select(".slide-title a, .event-card a")

            if not event_links:
                logger.warning(
                    "VisitTucsonCrawler: No event cards found, page may be JS-only"
                )
                return events

            for link in event_links[:20]:  # Limit to first 20 to avoid too many requests
                try:
                    event_url = link.get("href", "")
                    if not event_url:
                        continue

                    # Make absolute URL
                    if event_url.startswith("/"):
                        event_url = f"https://visittucson.org{event_url}"
                    elif not event_url.startswith("http"):
                        event_url = f"https://visittucson.org/{event_url}"

                    # Fetch the detail page
                    event_html = self._get(event_url)
                    event_soup = self._parse_html(event_html)

                    # Extract event details from detail page
                    title_elem = event_soup.select_one("h1.page-title")
                    event_name = (
                        title_elem.get_text(strip=True) if title_elem else "Unknown"
                    )

                    # Try to find date in various places
                    date_elem = event_soup.select_one(
                        "time, .event-date, [class*='date']"
                    )
                    event_date_str = ""
                    if date_elem:
                        date_text = date_elem.get("title") or date_elem.get_text(
                            strip=True
                        )
                        try:
                            parsed_date = dateutil_parser.parse(date_text)
                            event_date_str = parsed_date.date().isoformat()
                        except:
                            pass

                    # If no date found or date not in target weekend, skip
                    if not event_date_str:
                        logger.warning(
                            f"Could not parse date for {event_name}, skipping"
                        )
                        continue

                    # Venue
                    venue_elem = event_soup.select_one(
                        ".event-venue, [class*='venue']"
                    )
                    venue_name = (
                        venue_elem.get_text(strip=True) if venue_elem else "TBD"
                    )

                    # Description
                    desc_elem = event_soup.select_one(
                        ".event-description, [class*='description']"
                    )
                    description = (
                        desc_elem.get_text(strip=True) if desc_elem else ""
                    )

                    # Image
                    img_elem = event_soup.select_one(".event-image img, img[alt]")
                    image_url = (
                        img_elem.get("src", "") if img_elem else ""
                    )
                    if image_url and not image_url.startswith("http"):
                        image_url = f"https://visittucson.org{image_url}"

                    event_dict = {
                        "name": event_name,
                        "source": "Visit Tucson",
                        "source_event_id": f"visittucson_{event_url}",
                        "event_url": event_url,
                        "venue_name": venue_name,
                        "venue_address": "",
                        "event_date": event_date_str,
                        "event_end_date": event_date_str,
                        "event_time": "",
                        "description": description,
                        "category": "Other",
                        "price": "TBD",
                        "image_url": image_url,
                        "weekend_of": weekend_start.isoformat(),
                    }
                    events.append(event_dict)

                except Exception as e:
                    logger.warning(f"Error parsing Visit Tucson event: {e}")

        except Exception as e:
            logger.error(f"Error crawling Visit Tucson: {e}")

        logger.info(
            f"VisitTucsonCrawler: found {len(events)} events "
            f"({weekend_start} - {weekend_end})"
        )
        return events
