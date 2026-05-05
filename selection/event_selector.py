"""Event selection logic for the headline event."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Known high-value venues in Tucson
HIGH_VALUE_VENUES = {
    "Rialto Theatre",
    "Club Congress",
    "191 Toole",
    "Arizona State Museum",
    "Sabino Canyon",
}

# Category weights for scoring
CATEGORY_WEIGHTS = {
    "Festival": 15,
    "Grand Opening": 12,
    "Concert": 10,
    "Market": 8,
    "Theatre": 8,
    "Comedy": 7,
    "Sports": 6,
    "Food & Drink": 5,
    "Art": 5,
    "Film": 5,
    "Community": 4,
    "Other": 1,
}


def score_event(event: Dict[str, Any]) -> float:
    """
    Score an event for headline selection.

    Args:
        event: Event dict

    Returns:
        Float score (higher = better)
    """
    score = 0.0

    # Category weight
    category = event.get("category", "Other")
    score += CATEGORY_WEIGHTS.get(category, 1)

    # Known high-value venue bonus
    if event.get("venue_name", "") in HIGH_VALUE_VENUES:
        score += 10

    # Has image
    if event.get("image_url"):
        score += 3

    # Has price info
    if event.get("price") and event.get("price") != "TBD":
        score += 2

    # Description length (more detailed = better)
    if len(event.get("description", "")) > 100:
        score += 2

    return score


def select_headline(
    events: List[Dict[str, Any]], used_event_ids: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Select the best headline event for the newsletter.

    Args:
        events: List of all crawled events
        used_event_ids: List of source event IDs already featured

    Returns:
        The selected event dict, or None if no suitable event found
    """
    # Filter out already-used events
    available_events = [
        e for e in events
        if e.get("source_event_id") not in used_event_ids
    ]

    if not available_events:
        logger.warning("No available events (all have been used before)")
        return None

    # Score and sort
    scored = [(e, score_event(e)) for e in available_events]
    scored.sort(key=lambda x: x[1], reverse=True)

    if not scored:
        logger.warning("No events to score")
        return None

    headline, headline_score = scored[0]

    if headline_score < 3:
        logger.warning(
            f"Headline event score is low ({headline_score}): "
            f"{headline.get('name')}"
        )

    logger.info(
        f"Selected headline: {headline.get('name')} "
        f"({headline.get('venue_name')}, score={headline_score})"
    )
    return headline
