"""
Enum definitions for scraper configuration.

These enums define valid values for update types and HTTP request methods.
They inherit from StrEnum to ensure values behave like strings.
"""

from enum import StrEnum


class UpdateType(StrEnum):
    """
    Defines the type of data updates the scraper can handle.

    Attributes:
        EVENTS_RESULTS: Represents updates for finished event results.
    """
    EVENTS_RESULTS = "events_results"


class RequestType(StrEnum):
    """
    Defines supported HTTP request methods for the scraper.

    Attributes:
        GET: HTTP GET request.
        POST: HTTP POST request.
    """
    GET = "get"
    POST = "post"
