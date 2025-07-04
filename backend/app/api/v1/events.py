"""
API router for retrieving stored event results.

This endpoint allows filtering by:
- sport
- keyword(s) (from competition name)
- time range (relative via `hours` or absolute via `from_date` / `to_date`)
"""

import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter

from app.common.helpers import tokenize
from app.converter.schemas import Event
from app.services import redis_service


# API router with base path /v1
events_router = APIRouter(prefix="/v1")


@events_router.get("/get_results")
async def get_results(
    keyword: Optional[str] = None,
    sport: Optional[str] = None,
    hours: Optional[int] = None,
    from_date: Optional[str] = None,  # '2025-07-01'
    to_date: Optional[str] = None     # '2025-07-04'
):
    """
    Retrieves a list of event results filtered by keyword, sport, and time.

    Query Parameters:
        keyword (Optional[str]): Text used to match against competition names (tokenized).
        sport (Optional[str]): Sport name (e.g., 'football').
        hours (Optional[int]): Number of hours from now to look back.
        from_date (Optional[str]): Start date in 'YYYY-MM-DD' format.
        to_date (Optional[str]): End date in 'YYYY-MM-DD' format.

    Returns:
        list[dict]: A list of event dictionaries matching the given filters.
    """
    sets = []

    # Filter by sport
    if sport:
        sets.append(await redis_service.get_keys_by_sport(sport))

    # Filter by keyword (tokenized competition name)
    if keyword:
        words = tokenize(keyword)
        if words:
            keyword_keys = await redis_service.get_keys_by_words(words)
            sets.append(keyword_keys)

    # Filter by time
    now = int(time.time())
    from_ts = 0
    to_ts = now

    if hours is not None:
        from_ts = now - hours * 3600
    elif from_date or to_date:
        if from_date:
            from_ts = int(datetime.strptime(from_date, "%Y-%m-%d").timestamp())
        if to_date:
            to_ts = int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())

    time_keys = set(await redis_service.get_keys_by_time(from_ts, to_ts))
    sets.append(time_keys)

    # Intersection of all filters
    if sets:
        final_keys = set.intersection(*sets)
    else:
        final_keys = time_keys

    # Fetch and deserialize events
    values = await redis_service.get_events_by_keys(list(final_keys))
    events = [Event.from_redis(v) for v in values if v]

    return [e.get_dict() for e in events]
