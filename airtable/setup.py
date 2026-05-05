"""
One-time Airtable setup script.

Creates all required fields on Venues and Events tables, and creates the Newsletter Drafts table.
Run this once before the first pipeline execution.
"""

import logging

from airtable.client import AirtableClient
from config import config

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def setup_venues_table(client: AirtableClient) -> None:
    """Create all fields on the Venues table."""
    table_id = config.AIRTABLE_VENUES_TABLE_ID

    fields_to_create = [
        {
            "name": "Category",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "Restaurant"},
                    {"name": "Bar"},
                    {"name": "Under the Radar"},
                ]
            },
        },
        {
            "name": "Cuisine / Vibe",
            "type": "singleLineText",
        },
        {
            "name": "Neighborhood",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "Downtown"},
                    {"name": "4th Ave"},
                    {"name": "Midtown"},
                    {"name": "Eastside"},
                    {"name": "Westside"},
                    {"name": "Foothills"},
                    {"name": "South Tucson"},
                    {"name": "University"},
                    {"name": "Other"},
                ]
            },
        },
        {"name": "Address", "type": "singleLineText"},
        {"name": "Website", "type": "url"},
        {"name": "Yelp URL", "type": "url"},
        {"name": "Google Place ID", "type": "singleLineText"},
        {"name": "Yelp ID", "type": "singleLineText"},
        {"name": "Rating", "type": "number", "options": {"precision": 1}},
        {
            "name": "Price Level",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "$"},
                    {"name": "$$"},
                    {"name": "$$$"},
                    {"name": "$$$$"},
                ]
            },
        },
        {"name": "One-liner", "type": "singleLineText"},
        {"name": "Notes", "type": "multilineText"},
        {"name": "Active", "type": "checkbox"},
        {"name": "Last Featured Date", "type": "date"},
        {"name": "Times Featured", "type": "number", "options": {"precision": 0}},
        {"name": "Cooldown Weeks", "type": "number", "options": {"precision": 0}},
        {
            "name": "Tags",
            "type": "multipleSelect",
            "options": {
                "choices": [
                    {"name": "patio"},
                    {"name": "live-music"},
                    {"name": "dog-friendly"},
                    {"name": "late-night"},
                    {"name": "brunch"},
                    {"name": "BYOB"},
                    {"name": "hidden-gem"},
                    {"name": "local-only"},
                ]
            },
        },
        {"name": "Photos URL", "type": "url"},
    ]

    logger.info("Setting up Venues table fields...")
    for field_config in fields_to_create:
        try:
            client.create_field(table_id, field_config)
        except Exception as e:
            logger.error(f"Error creating field {field_config['name']}: {e}")

    logger.info("Venues table setup complete!")


def setup_events_table(client: AirtableClient) -> None:
    """Create all fields on the Events table."""
    table_id = config.AIRTABLE_EVENTS_TABLE_ID

    fields_to_create = [
        {
            "name": "Source",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "Eventbrite"},
                    {"name": "Visit Tucson"},
                    {"name": "Tucson Weekly"},
                    {"name": "Rialto Theatre"},
                    {"name": "Club Congress"},
                    {"name": "Manual"},
                ]
            },
        },
        {"name": "Source Event ID", "type": "singleLineText"},
        {"name": "Event URL", "type": "url"},
        {"name": "Venue Name", "type": "singleLineText"},
        {"name": "Venue Address", "type": "singleLineText"},
        {"name": "Event Date", "type": "date"},
        {"name": "Event End Date", "type": "date"},
        {"name": "Event Time", "type": "singleLineText"},
        {"name": "Description", "type": "multilineText"},
        {
            "name": "Category",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "Concert"},
                    {"name": "Festival"},
                    {"name": "Market"},
                    {"name": "Comedy"},
                    {"name": "Theatre"},
                    {"name": "Sports"},
                    {"name": "Food & Drink"},
                    {"name": "Art"},
                    {"name": "Film"},
                    {"name": "Grand Opening"},
                    {"name": "Community"},
                    {"name": "Other"},
                ]
            },
        },
        {"name": "Price", "type": "singleLineText"},
        {"name": "Image URL", "type": "url"},
        {"name": "Weekend Of", "type": "singleLineText"},
        {"name": "Score", "type": "number", "options": {"precision": 1}},
        {"name": "Featured In Issue", "type": "singleLineText"},
        {"name": "Was Headline", "type": "checkbox"},
        {"name": "Crawled Date", "type": "date"},
        {"name": "Suppressed", "type": "checkbox"},
    ]

    logger.info("Setting up Events table fields...")
    for field_config in fields_to_create:
        try:
            client.create_field(table_id, field_config)
        except Exception as e:
            logger.error(f"Error creating field {field_config['name']}: {e}")

    logger.info("Events table setup complete!")


def create_newsletter_drafts_table(client: AirtableClient) -> None:
    """Create the Newsletter Drafts table."""

    fields_config = [
        {
            "name": "Issue Name",
            "type": "singleLineText",
        },
        {
            "name": "Weekend Of",
            "type": "date",
        },
        {
            "name": "Created At",
            "type": "singleLineText",
        },
        {
            "name": "Status",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "Draft"},
                    {"name": "Scheduled"},
                    {"name": "Sent"},
                    {"name": "Skipped"},
                ]
            },
        },
        {
            "name": "Beehiiv Post ID",
            "type": "singleLineText",
        },
        {
            "name": "Beehiiv Draft URL",
            "type": "url",
        },
        {
            "name": "Headline Event Name",
            "type": "singleLineText",
        },
        {
            "name": "Headline Event URL",
            "type": "url",
        },
        {
            "name": "Restaurant Picks",
            "type": "multilineText",
        },
        {
            "name": "Bar Picks",
            "type": "multilineText",
        },
        {
            "name": "Under the Radar Pick",
            "type": "singleLineText",
        },
        {
            "name": "Raw Claude Output",
            "type": "multilineText",
        },
        {
            "name": "HTML Body",
            "type": "multilineText",
        },
        {
            "name": "Generation Notes",
            "type": "multilineText",
        },
    ]

    logger.info("Creating Newsletter Drafts table...")
    try:
        client.create_table("Newsletter Drafts", fields_config)
        logger.info("Newsletter Drafts table created successfully!")
    except Exception as e:
        logger.error(f"Error creating Newsletter Drafts table: {e}")


def main():
    """Run all setup steps."""
    logger.info("Starting Airtable setup...")
    client = AirtableClient()

    setup_venues_table(client)
    setup_events_table(client)
    create_newsletter_drafts_table(client)

    logger.info("✓ Airtable setup complete!")
    logger.info(
        "Next: Manually add 10+ venues to the Venues table before running main.py"
    )


if __name__ == "__main__":
    main()
