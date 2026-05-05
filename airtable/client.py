"""Airtable REST API client."""

import time
import logging
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import config

logger = logging.getLogger(__name__)


class AirtableClient:
    """Thin wrapper around Airtable REST API v0."""

    def __init__(self):
        """Initialize the client with auth headers and retry strategy."""
        self.base_url = config.AIRTABLE_BASE_URL
        self.meta_base_url = config.AIRTABLE_META_BASE_URL
        self.pat = config.AIRTABLE_PAT
        self.base_id = config.AIRTABLE_BASE_ID

        self.session = requests.Session()

        # Add retry strategy: retry on 429 and 5xx errors
        retry_strategy = Retry(
            total=config.MAX_RETRIES,
            backoff_factor=config.RETRY_BACKOFF_SECONDS,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _headers(self) -> Dict[str, str]:
        """Return authorization headers."""
        return {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json",
        }

    def _rate_limit(self) -> None:
        """Apply rate limiting (5 requests/sec for Airtable)."""
        time.sleep(config.AIRTABLE_RATE_LIMIT_DELAY)

    def list_records(
        self,
        table_id: str,
        filter_formula: Optional[str] = None,
        fields: Optional[List[str]] = None,
        max_records: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Fetch records from a table.

        Args:
            table_id: Airtable table ID
            filter_formula: Optional filterByFormula string
            fields: Optional list of field names to return
            max_records: Max records to fetch

        Returns:
            List of record dicts with 'id', 'fields', 'createdTime'
        """
        self._rate_limit()

        url = f"{self.base_url}/{self.base_id}/{table_id}"
        params = {"pageSize": min(max_records, 100)}

        if filter_formula:
            params["filterByFormula"] = filter_formula
        if fields:
            params["fields[]"] = fields

        response = self.session.get(url, params=params, headers=self._headers())
        response.raise_for_status()

        records = response.json().get("records", [])
        logger.info(f"Fetched {len(records)} records from {table_id}")

        # Handle pagination if needed (for now, simple approach)
        return records

    def create_record(
        self, table_id: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new record in a table.

        Args:
            table_id: Airtable table ID
            fields: Field values dict

        Returns:
            Created record dict
        """
        self._rate_limit()

        url = f"{self.base_url}/{self.base_id}/{table_id}"
        payload = {"fields": fields}

        response = self.session.post(
            url, json=payload, headers=self._headers()
        )
        response.raise_for_status()

        record = response.json()
        logger.info(f"Created record {record['id']} in {table_id}")
        return record

    def update_record(
        self, table_id: str, record_id: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a record (PATCH — partial update).

        Args:
            table_id: Airtable table ID
            record_id: Record ID to update
            fields: Field values to update

        Returns:
            Updated record dict
        """
        self._rate_limit()

        url = f"{self.base_url}/{self.base_id}/{table_id}/{record_id}"
        payload = {"fields": fields}

        response = self.session.patch(
            url, json=payload, headers=self._headers()
        )
        response.raise_for_status()

        record = response.json()
        logger.info(f"Updated record {record_id} in {table_id}")
        return record

    def create_table(
        self, name: str, fields_config: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a new table in the base.

        Args:
            name: Table name
            fields_config: List of field config dicts

        Returns:
            Created table dict
        """
        self._rate_limit()

        url = f"{self.meta_base_url}/{self.base_id}/tables"
        payload = {"name": name, "fields": fields_config}

        response = self.session.post(
            url, json=payload, headers=self._headers()
        )
        response.raise_for_status()

        table = response.json()
        logger.info(f"Created table {name}")
        return table

    def create_field(
        self, table_id: str, field_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add a new field to a table.

        Args:
            table_id: Airtable table ID
            field_config: Field config dict with 'name', 'type', optional 'options'

        Returns:
            Created field dict
        """
        self._rate_limit()

        url = f"{self.meta_base_url}/{self.base_id}/tables/{table_id}/fields"

        response = self.session.post(
            url, json=field_config, headers=self._headers()
        )

        # 422 = duplicate field name, which is OK if we're idempotent
        if response.status_code == 422:
            logger.warning(
                f"Field {field_config.get('name')} already exists, skipping"
            )
            return {}

        response.raise_for_status()

        field = response.json()
        logger.info(f"Created field {field_config['name']} in {table_id}")
        return field

    def upsert_record(
        self,
        table_id: str,
        filter_formula: str,
        fields: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Upsert: update if exists, create if not.

        Args:
            table_id: Airtable table ID
            filter_formula: Formula to find existing record
            fields: Field values

        Returns:
            Created or updated record dict
        """
        existing = self.list_records(table_id, filter_formula=filter_formula)

        if existing:
            return self.update_record(table_id, existing[0]["id"], fields)
        else:
            return self.create_record(table_id, fields)
