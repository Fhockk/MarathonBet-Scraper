"""
Schema definitions for structured event data using Pydantic models.

This module defines:
- EventMetadata: Metadata for a sports event (teams, competition, time).
- EventState: Live status and score details.
- Event: Full event structure with serialization methods for Redis.
"""

from datetime import datetime, timezone
from typing import Optional

from orjson import orjson
from pydantic import BaseModel


class EventMetadata(BaseModel):
    """
    Contains metadata for a sports event.

    Attributes:
        competition_id (Optional[int]): ID of the competition.
        competition_name (str): Name of the competition.
        home_team (str): Name of the home team.
        away_team (str): Name of the away team.
        start_time (int): Unix timestamp (UTC) of the event start time.
        extra (Optional[str]): Additional metadata, e.g., raw JSON or HTML.
    """

    competition_id: Optional[int] = None
    competition_name: str
    home_team: str
    away_team: str
    start_time: int
    extra: Optional[str] = None

    @property
    def start_time_dt(self) -> datetime:
        """
        Returns the start_time as a UTC datetime object.

        Returns:
            datetime: The start time converted from Unix timestamp.
        """
        return datetime.fromtimestamp(self.start_time, tz=timezone.utc)


class EventState(BaseModel):
    """
    Contains the live status and score data of an event.

    Attributes:
        is_live (Optional[bool]): Whether the event is live.
        scores (Optional[list]): List of score-related data.
    """

    is_live: bool | None = None
    scores: Optional[list] = None


class Event(BaseModel):
    """
    Represents a complete event, including ID, sport, metadata, state, and extra data.

    Attributes:
        event_id (int): Unique identifier for the event.
        sport (str): Name of the sport (e.g., "Football").
        metadata (EventMetadata): Metadata about the event.
        state (EventState): State information (live status, scores).
        extra (Optional[dict]): Additional data (e.g., derived values or context).
    """

    event_id: int
    sport: str
    metadata: EventMetadata
    state: EventState
    extra: Optional[dict] = {}

    @property
    def key(self) -> str:
        """
        Returns a unique string key representing the event.

        Returns:
            str: A stringified version of event_id.
        """
        return str(self.event_id)

    def get_dict(self) -> dict:
        """
        Returns the full event data as a Python dictionary.

        Returns:
            dict: All fields including nested metadata and state.
        """
        return {
            "event_id": self.event_id,
            "sport": self.sport,
            "metadata": self.metadata.model_dump(),
            "state": self.state.model_dump(),
            "extra": self.extra or {},
        }

    def to_redis(self) -> str:
        """
        Serializes the event to a JSON string for Redis storage.

        Returns:
            str: JSON representation of the event.
        """
        return orjson.dumps(self.get_dict())

    @classmethod
    def from_redis(cls, value: str) -> "Event":
        """
        Deserializes an event from a Redis-stored JSON string.

        Args:
            value (str): JSON-encoded string from Redis.

        Returns:
            Event: A reconstructed Event instance.
        """
        return cls.model_validate(orjson.loads(value))
