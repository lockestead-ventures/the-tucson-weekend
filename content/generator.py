"""Content generation via Claude."""

import logging
from typing import Any, Dict, List

import anthropic

from config import config
from content import prompts

logger = logging.getLogger(__name__)


def generate_newsletter(
    headline_event: Dict[str, Any], venue_selections: Dict[str, Any]
) -> Dict[str, str]:
    """
    Generate all newsletter content sections via Claude.

    Args:
        headline_event: The selected headline event dict
        venue_selections: Dict with restaurants, bars, under_the_radar keys

    Returns:
        Dict with keys: headline, restaurants, bars, under_the_radar, subject_line
    """
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    sections = {}

    try:
        # 1. Headline event copy
        headline_prompt = prompts.HEADLINE_EVENT_PROMPT.format(prompts.SYSTEM_TONE)
        headline_prompt = headline_prompt.format(
            event_name=headline_event.get("name", ""),
            venue_name=headline_event.get("venue_name", ""),
            category=headline_event.get("category", ""),
            description=headline_event.get("description", ""),
        )

        logger.info("Generating headline event copy...")
        response = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=config.ANTHROPIC_MAX_TOKENS,
            messages=[{"role": "user", "content": headline_prompt}],
        )
        sections["headline"] = response.content[0].text

        # 2. Restaurants
        restaurants = venue_selections.get("restaurants", [])
        restaurants_list = "\n".join(
            [
                f"- {r.get('fields', {}).get('Name', 'Unknown')} "
                f"({r.get('fields', {}).get('Neighborhood', '')}): "
                f"{r.get('fields', {}).get('One-liner', '')}"
                for r in restaurants
            ]
        )

        restaurants_prompt = prompts.RESTAURANT_PICKS_PROMPT.format(prompts.SYSTEM_TONE)
        restaurants_prompt = restaurants_prompt.format(
            restaurants_list=restaurants_list
        )

        logger.info("Generating restaurant picks...")
        response = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=config.ANTHROPIC_MAX_TOKENS,
            messages=[{"role": "user", "content": restaurants_prompt}],
        )
        sections["restaurants"] = response.content[0].text

        # 3. Bars
        bars = venue_selections.get("bars", [])
        bars_list = "\n".join(
            [
                f"- {b.get('fields', {}).get('Name', 'Unknown')}: "
                f"{b.get('fields', {}).get('One-liner', '')}"
                for b in bars
            ]
        )

        bars_prompt = prompts.BAR_PICKS_PROMPT.format(prompts.SYSTEM_TONE)
        bars_prompt = bars_prompt.format(bars_list=bars_list)

        logger.info("Generating bar picks...")
        response = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=config.ANTHROPIC_MAX_TOKENS,
            messages=[{"role": "user", "content": bars_prompt}],
        )
        sections["bars"] = response.content[0].text

        # 4. Under the Radar
        under_radar = venue_selections.get("under_the_radar", {})
        under_radar_prompt = prompts.UNDER_THE_RADAR_PROMPT.format(prompts.SYSTEM_TONE)
        under_radar_prompt = under_radar_prompt.format(
            venue_name=under_radar.get("fields", {}).get("Name", ""),
            category=under_radar.get("fields", {}).get("Category", ""),
            one_liner=under_radar.get("fields", {}).get("One-liner", ""),
        )

        logger.info("Generating under the radar pick...")
        response = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=config.ANTHROPIC_MAX_TOKENS,
            messages=[{"role": "user", "content": under_radar_prompt}],
        )
        sections["under_the_radar"] = response.content[0].text

        # 5. Subject line
        subject_prompt = prompts.SUBJECT_LINE_PROMPT.format(prompts.SYSTEM_TONE)
        subject_prompt = subject_prompt.format(
            event_name=headline_event.get("name", "")
        )

        logger.info("Generating subject line...")
        response = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": subject_prompt}],
        )
        sections["subject_line"] = response.content[0].text.strip()

    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        raise

    logger.info("All content sections generated successfully")
    return sections
