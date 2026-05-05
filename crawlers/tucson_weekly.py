"""Tucson Weekly events crawler."""

import logging
import re
from datetime import date
from typing import Any, Dict, List

from dateutil import parser as dateutil_parser

from crawlers.base import BaseCrawler

logger = logging.getLogger(__name__)


class TucsonWeeklyCrawler(BaseCrawler):
    """Crawl events from Tucson Weekly community calendar."""

    def crawl(
        self, weekend_start: date, weekend_end: date
    ) -> List[Dict[str, Any]]:
        """
        Fetch events from Tucson Weekly.

        Args:
            weekend_start: Friday date
            weekend_end: Sunday date

        Returns:
            List of normalized event dicts
        """
        events = []

        try:
            url = "https://community.tucsonweekly.com/tucson/EventSearch"
            params = {"narrowByDate": "This Weekend"}

            page = 1
            total_pages = None

            while True:
                params["page"] = page
                html = self._get(url, params=params)
                soup = self._parse_html(html)

                # Look for pagination info
                if total_pages is None:
                    paging_text = soup.select_one(".pagination")
                    if paging_text:
                        match = re.search(
                            r"page \d+ of (\d+)", paging_text.get_text()
                        )
                        if match:
                            total_pages = int(match.group(1))
                    if not total_pages:
                        total_pages = 1

                # Find event cards
                event_cards = soup.select(".search-results article")

                if not event_cards:
                    logger.info("TucsonWeeklyCrawler: No more events found")
                    break

                for card in event_cards:
                    try:
                        # Title & URL
                        title_link = card.select_one("h2 a")
                        if not title_link:
                            continue

                        event_name = title_link.get_text(strip=True)
                        event_url = title_link.get("href", "")
                        if not event_url.startswith("http"):
                            event_url = f"https://community.tucsonweekly.com{event_url}"

                        # Date
                        date_elem = card.select_one(".event-date")
                        event_date_str = ""
                        if date_elem:
                            date_text = date_elem.get_text(strip=True)
                            try:
                                parsed_date = dateutil_parser.parse(date_text)
                                event_date_str = parsed_date.date().isoformat()
                            except:
                                pass

                        if not event_date_str:
                            continue

                        # Venue
                        venue_elem = card.select_one(".venue a")
                        venue_name = (
                            venue_elem.get_text(strip=True) if venue_elem else "TBD"
                        )

                        # Address (might be in venue location)
                        addr_elem = card.select_one(".location")
                        venue_address = (
                            addr_elem.get_text(strip=True) if addr_elem else ""
                        )

                        # Description
                        desc_elem = card.select_one(".desc p")
                        description = (
                            desc_elem.get_text(strip=True) if desc_elem else ""
                        )

                        # Image
                        img_elem = card.select_one("img")
                        image_url = img_elem.get("src", "") if img_elem else ""

                        event_dict = {
                            "name": event_name,
                            "source": "Tucson Weekly",
                            "source_event_id": f"tucsonweekly_{event_url}",
                            "event_url": event_url,
                            "venue_name": venue_name,
                            "venue_address": venue_address,
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
                        logger.warning(f"Error parsing Tucson Weekly event: {e}")

                # Check if there are more pages
                if page >= total_pages:
                    break

                page += 1

        except Exception as e:
            logger.error(f"Error crawling Tucson Weekly: {e}")

        logger.info(
            f"TucsonWeeklyCrawler: found {len(events)} events "
            f"({weekend_start} - {weekend_end})"
        )
        return events
