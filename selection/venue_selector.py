"""Venue selection logic."""

import logging
from datetime import date
from typing import Any, Dict, List

from airtable.venues import VenuesManager
from config import config

logger = logging.getLogger(__name__)


class InsufficientVenuesError(Exception):
    """Raised when not enough eligible venues are found."""

    pass


def select_venues(weekend_of: date) -> Dict[str, Any]:
    """
    Select restaurants, bars, and under-the-radar venue for the weekend.

    Args:
        weekend_of: The Saturday date of the target weekend

    Returns:
        Dict with keys: restaurants, bars, under_the_radar
        Each is a list of venue records (except under_the_radar which is a single record)

    Raises:
        InsufficientVenuesError: If unable to select required venues
    """
    manager = VenuesManager()
    weekend_str = weekend_of.isoformat()

    try:
        # Get eligible venues for each category
        eligible_restaurants = manager.get_eligible_venues("Restaurant", weekend_of)
        eligible_bars = manager.get_eligible_venues("Bar", weekend_of)
        eligible_under_radar = manager.get_eligible_venues("Under the Radar", weekend_of)

        # Check if we have enough
        if len(eligible_restaurants) < config.RESTAURANTS_TO_SELECT:
            logger.warning(
                f"Only {len(eligible_restaurants)} eligible restaurants, "
                f"need {config.RESTAURANTS_TO_SELECT}. Halving cooldown threshold and retrying..."
            )
            eligible_restaurants = manager.get_eligible_venues(
                "Restaurant",
                weekend_of,
                cooldown_override=config.DEFAULT_COOLDOWN_WEEKS_NORMAL // 2,
            )
            logger.info("Restaurants re-fetched with reduced cooldown")

        if len(eligible_bars) < config.BARS_TO_SELECT:
            logger.warning(
                f"Only {len(eligible_bars)} eligible bars, "
                f"need {config.BARS_TO_SELECT}. Halving cooldown threshold..."
            )
            eligible_bars = manager.get_eligible_venues(
                "Bar",
                weekend_of,
                cooldown_override=config.DEFAULT_COOLDOWN_WEEKS_NORMAL // 2,
            )

        if len(eligible_under_radar) < 1:
            logger.warning(
                "No eligible under-the-radar venues. Halving cooldown threshold..."
            )
            eligible_under_radar = manager.get_eligible_venues(
                "Under the Radar",
                weekend_of,
                cooldown_override=config.DEFAULT_COOLDOWN_WEEKS_UNDER_RADAR // 2,
            )

        # Final check
        if (
            len(eligible_restaurants) < config.RESTAURANTS_TO_SELECT
            or len(eligible_bars) < config.BARS_TO_SELECT
            or len(eligible_under_radar) < 1
        ):
            raise InsufficientVenuesError(
                f"Insufficient venues even with reduced cooldown: "
                f"Restaurants {len(eligible_restaurants)}/{config.RESTAURANTS_TO_SELECT}, "
                f"Bars {len(eligible_bars)}/{config.BARS_TO_SELECT}, "
                f"Under Radar {len(eligible_under_radar)}/1"
            )

        # Select from eligible pools
        selected_restaurants = eligible_restaurants[: config.RESTAURANTS_TO_SELECT]
        selected_bars = eligible_bars[: config.BARS_TO_SELECT]
        selected_under_radar = eligible_under_radar[0]

        logger.info(
            f"Selected {len(selected_restaurants)} restaurants, "
            f"{len(selected_bars)} bars, 1 under-the-radar venue"
        )

        return {
            "restaurants": selected_restaurants,
            "bars": selected_bars,
            "under_the_radar": selected_under_radar,
        }

    except InsufficientVenuesError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.error(f"Error selecting venues: {e}")
        raise
