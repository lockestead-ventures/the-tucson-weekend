"""Base crawler class with shared fetch/retry logic."""

import logging
import time
from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from config import config

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """Abstract base crawler with shared retry and parsing logic."""

    def __init__(self):
        """Initialize crawler with session."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"
                )
            }
        )

    def _get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Fetch a URL with retry logic.

        Args:
            url: URL to fetch
            params: Query parameters
            headers: Additional headers

        Returns:
            Response text

        Raises:
            requests.RequestException: After max retries
        """
        merged_headers = {**self.session.headers}
        if headers:
            merged_headers.update(headers)

        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.session.get(
                    url, params=params, headers=merged_headers, timeout=10
                )
                response.raise_for_status()
                return response.text

            except requests.RequestException as e:
                if attempt < config.MAX_RETRIES - 1:
                    wait = config.RETRY_BACKOFF_SECONDS * (2 ** attempt)
                    logger.warning(
                        f"Retry {attempt + 1}/{config.MAX_RETRIES} after {wait}s: {e}"
                    )
                    time.sleep(wait)
                else:
                    logger.error(f"Failed to fetch {url} after {config.MAX_RETRIES} attempts")
                    raise

    def _parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML string into BeautifulSoup object.

        Args:
            html: HTML string

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, "lxml")

    @abstractmethod
    def crawl(
        self, weekend_start: date, weekend_end: date
    ) -> List[Dict[str, Any]]:
        """
        Crawl events for a given weekend.

        Args:
            weekend_start: Friday date
            weekend_end: Sunday date

        Returns:
            List of normalized event dicts with keys:
            - name, source, source_event_id, event_url, venue_name, venue_address,
              event_date, event_end_date, event_time, description, category,
              price, image_url, weekend_of
        """
        pass
