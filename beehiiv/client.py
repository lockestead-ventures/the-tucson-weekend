"""Beehiiv API client."""

import logging
from typing import Any, Dict, Optional

import requests

from config import config

logger = logging.getLogger(__name__)


class BeehiivClient:
    """Beehiiv API client."""

    def __init__(self):
        """Initialize with API credentials."""
        self.api_key = config.BEEHIIV_API_KEY
        self.pub_id = config.BEEHIIV_PUB_ID
        self.base_url = config.BEEHIIV_BASE_URL

    def _headers(self) -> Dict[str, str]:
        """Return authorization headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_draft(
        self,
        title: str,
        subtitle: str,
        body_content: str,
        thumbnail_image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a draft post in Beehiiv.

        Args:
            title: Post title
            subtitle: Post subtitle (email subject line)
            body_content: HTML body content
            thumbnail_image_url: Optional image URL for thumbnail

        Returns:
            Response dict with post data
        """
        url = f"{self.base_url}/publications/{self.pub_id}/posts"

        payload = {
            "title": title,
            "subtitle": subtitle,
            "body_content": body_content,
            "status": "draft",
            "content_tags": ["weekend", "tucson", "events"],
        }

        if thumbnail_image_url:
            payload["thumbnail_image_url"] = thumbnail_image_url

        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=30)
            response.raise_for_status()

            data = response.json()
            post_id = data.get("data", {}).get("id", "")
            logger.info(f"Created draft post: {post_id}")

            return data

        except requests.RequestException as e:
            logger.error(f"Error creating Beehiiv draft: {e}")
            raise

    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Retrieve a post by ID.

        Args:
            post_id: Beehiiv post ID

        Returns:
            Response dict
        """
        url = f"{self.base_url}/publications/{self.pub_id}/posts/{post_id}"

        try:
            response = requests.get(url, headers=self._headers(), timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Error fetching Beehiiv post {post_id}: {e}")
            raise
