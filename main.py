"""Main pipeline orchestrator for the Tucson Weekend Guide newsletter."""

import logging
import sys
from datetime import date, timedelta

from airtable.events import EventsManager
from airtable.venues import VenuesManager
from beehiiv.client import BeehiivClient
from config import config
from content.generator import generate_newsletter
from content.renderer import render_html
from crawlers.club_congress import ClubCongressCrawler
from crawlers.eventbrite import EventbriteCrawler
from crawlers.rialto import RialtoCrawler
from crawlers.tucson_weekly import TucsonWeeklyCrawler
from crawlers.visit_tucson import VisitTucsonCrawler
from selection.event_selector import select_headline
from selection.venue_selector import select_venues

# Set up logging
log_file = config.LOG_DIR / f"{date.today().isoformat()}.log"
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Run the full pipeline."""
    logger.info("=" * 80)
    logger.info("TUCSON WEEKEND GUIDE — NEWSLETTER GENERATION")
    logger.info(f"DRY RUN: {config.DRY_RUN}")
    logger.info("=" * 80)

    try:
        # 1. Compute target dates
        today = date.today()
        # If today is Tuesday (weekday 1), find the upcoming Friday (weekday 4)
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7  # If today IS Friday, get next Friday
        weekend_start = today + timedelta(days=days_until_friday)
        weekend_end = weekend_start + timedelta(days=2)
        weekend_label = weekend_start.isoformat()

        logger.info(f"Target weekend: {weekend_start} - {weekend_end}")

        # 2. Crawl all event sources
        logger.info("Crawling events from all sources...")
        all_events = []

        crawlers = [
            EventbriteCrawler(),
            VisitTucsonCrawler(),
            TucsonWeeklyCrawler(),
            RialtoCrawler(),
            ClubCongressCrawler(),
        ]

        for crawler in crawlers:
            try:
                events = crawler.crawl(weekend_start, weekend_end)
                all_events.extend(events)
                logger.info(f"✓ {crawler.__class__.__name__}: {len(events)} events")
            except Exception as e:
                logger.error(f"✗ {crawler.__class__.__name__} failed: {e}")

        logger.info(f"Total events crawled: {len(all_events)}")

        if not all_events:
            raise ValueError("No events found from any source")

        # 3. Store events in Airtable
        if not config.DRY_RUN:
            logger.info("Storing events in Airtable...")
            events_manager = EventsManager()
            events_manager.store_events(all_events)

        # 4. Get previously used event IDs
        if not config.DRY_RUN:
            events_manager = EventsManager()
            used_event_ids = events_manager.get_used_event_ids()
        else:
            used_event_ids = []

        # 5. Select headline event
        logger.info("Selecting headline event...")
        headline_event = select_headline(all_events, used_event_ids)
        if not headline_event:
            raise ValueError("No suitable headline event found")

        # 6. Select venues
        logger.info("Selecting venues...")
        venue_selections = select_venues(weekend_start)

        # 7. Generate content via Claude
        logger.info("Generating newsletter content via Claude...")
        sections = generate_newsletter(headline_event, venue_selections)

        # 8. Render HTML
        logger.info("Rendering HTML...")
        html_body = render_html(sections, headline_event, venue_selections)

        # 9. Push to Beehiiv (or dry run)
        if config.DRY_RUN:
            logger.info("=" * 80)
            logger.info("DRY RUN — NOT pushing to Beehiiv")
            logger.info("=" * 80)
            logger.info("Generated HTML:")
            logger.info(html_body)
            logger.info("=" * 80)
        else:
            logger.info("Creating draft in Beehiiv...")
            beehiiv = BeehiivClient()

            issue_title = f"Tucson Weekend Guide — {weekend_start.strftime('%b %-d')}–{weekend_end.strftime('%-d, %Y')}"
            response = beehiiv.create_draft(
                title=issue_title,
                subtitle=sections.get("subject_line", ""),
                body_content=html_body,
                thumbnail_image_url=headline_event.get("image_url"),
            )

            post_id = response.get("data", {}).get("id", "")
            draft_url = f"https://app.beehiiv.com/posts/{post_id}/edit"

            logger.info(f"✓ Draft created: {draft_url}")

            # 10. Mark items as featured in Airtable
            logger.info("Updating Airtable...")
            # Update events
            if headline_event.get("airtable_id"):
                events_manager.mark_event_used(
                    headline_event["airtable_id"], weekend_label, was_headline=True
                )

            # Update venues
            venues_manager = VenuesManager()
            for restaurant in venue_selections.get("restaurants", []):
                if restaurant.get("id"):
                    venues_manager.mark_venue_featured(restaurant["id"], weekend_label)

            for bar in venue_selections.get("bars", []):
                if bar.get("id"):
                    venues_manager.mark_venue_featured(bar["id"], weekend_label)

            under_radar = venue_selections.get("under_the_radar", {})
            if under_radar.get("id"):
                venues_manager.mark_venue_featured(under_radar["id"], weekend_label)

        logger.info("=" * 80)
        logger.info("✓ PIPELINE COMPLETE")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
