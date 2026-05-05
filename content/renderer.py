"""Render newsletter HTML."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def render_html(
    sections: Dict[str, str],
    headline_event: Dict[str, Any],
    venue_selections: Dict[str, Any],
) -> str:
    """
    Render final HTML newsletter body.

    Args:
        sections: Generated content sections (headline, restaurants, bars, etc.)
        headline_event: The headline event dict
        venue_selections: Venue selections dict

    Returns:
        HTML string suitable for Beehiiv
    """
    event_date_display = headline_event.get("event_date", "")
    event_time = headline_event.get("event_time", "")

    html_parts = []

    # Header with event info
    html_parts.append(
        f"""<h1 style="font-size: 28px; font-weight: bold; margin-bottom: 4px; color: #222;">
This Weekend in Tucson</h1>"""
    )

    html_parts.append(
        f"""<p style="font-size: 14px; color: #888; margin-bottom: 24px;">
{event_date_display} {event_time}</p>"""
    )

    # Headline event
    html_parts.append(
        f"""<h2 style="font-size: 20px; font-weight: bold; margin-bottom: 12px; margin-top: 24px; color: #222;">
{headline_event.get('name', 'TBD')}</h2>"""
    )

    html_parts.append(
        f"""<p style="font-size: 13px; color: #666; margin-bottom: 16px; line-height: 1.6;">
{headline_event.get('venue_name', 'TBD')}</p>"""
    )

    html_parts.append(
        f"""<p style="font-size: 14px; color: #333; margin-bottom: 24px; line-height: 1.6;">
{sections.get('headline', '')}</p>"""
    )

    if headline_event.get("event_url"):
        html_parts.append(
            f"""<p style="margin-bottom: 24px;">
<a href="{headline_event.get('event_url')}" style="color: #0066cc; text-decoration: none; font-weight: 500;">
Get tickets →</a></p>"""
        )

    # Restaurant picks
    html_parts.append(
        """<h2 style="font-size: 18px; font-weight: bold; margin-bottom: 16px; margin-top: 32px; color: #222;">
Where to eat</h2>"""
    )

    html_parts.append(
        f"""<p style="font-size: 14px; color: #333; margin-bottom: 24px; line-height: 1.6;">
{sections.get('restaurants', '')}</p>"""
    )

    # Bar picks
    html_parts.append(
        """<h2 style="font-size: 18px; font-weight: bold; margin-bottom: 16px; margin-top: 32px; color: #222;">
Where to drink</h2>"""
    )

    html_parts.append(
        f"""<p style="font-size: 14px; color: #333; margin-bottom: 24px; line-height: 1.6;">
{sections.get('bars', '')}</p>"""
    )

    # Under the radar
    html_parts.append(
        """<h2 style="font-size: 18px; font-weight: bold; margin-bottom: 16px; margin-top: 32px; color: #222;">
Under the radar</h2>"""
    )

    under_radar = venue_selections.get("under_the_radar", {})
    html_parts.append(
        f"""<p style="font-size: 14px; font-weight: 500; margin-bottom: 8px; color: #222;">
{under_radar.get('fields', {}).get('Name', 'TBD')}</p>"""
    )

    html_parts.append(
        f"""<p style="font-size: 14px; color: #333; margin-bottom: 24px; line-height: 1.6;">
{sections.get('under_the_radar', '')}</p>"""
    )

    # Footer
    html_parts.append(
        """<hr style="border: none; border-top: 1px solid #ddd; margin: 32px 0;">"""
    )

    html_parts.append(
        """<p style="font-size: 12px; color: #999; margin-top: 24px;">
Have a favorite spot? Let us know — we're always looking for great recommendations.</p>"""
    )

    html = "\n".join(html_parts)
    logger.info("HTML rendered successfully")

    return html
