"""
BaseScraper class providing shared scraping logic.

This abstract base class handles HTTP requests, logging, and data forwarding
to a converter. Specific scrapers should inherit from it and implement `get_updated_data`.
"""

from asyncio import Future
from typing import Optional

from app.common.common_requests import send_request
from app.common.mixins import LogMixin
from app.converter.converter import Converter
from app.scraper.schemas import UpdateType, RequestType


class BaseScraper(LogMixin):
    """
    Abstract base class for Marathonbet scrapers.

    Responsibilities:
    - Defines base domain and common request logic.
    - Sends parsed data to the converter.
    - Provides structured logging for scraping operations.

    Attributes:
        init_flag (bool): Marks whether the scraper has been initialized.
        scraper_error (Optional[Future]): Placeholder for error tracking.
        domain (str): Base URL for all requests.
        converter (Converter): Reference to the Converter instance.
    """

    def __init__(self, converter: Converter):
        """
        Initializes the scraper with a given Converter instance.

        Args:
            converter (Converter): The data converter used to handle results.
        """
        self.init_flag: bool = False
        self.scraper_error: Optional[Future] = None
        self.domain = "https://www.marathonbet.com"
        self.converter: Converter = converter

    async def get_updated_data(self, update_type: UpdateType):
        """
        Abstract method to be implemented by subclasses.

        Args:
            update_type (UpdateType): The type of update to fetch.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError()

    async def update(self, update_type: UpdateType):
        """
        Fetches updated data using `get_updated_data()` and sends it to the converter.

        Args:
            update_type (UpdateType): Type of update to fetch and process.
        """
        self.log(f"Update {update_type.value}")
        data = await self.get_updated_data(update_type)
        if data:
            self.converter.add_data(data)
        else:
            self.log(f"Get empty data: {data}", force=True)
        self.log(f"update {update_type.value} done")

    async def request(
        self,
        url: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        request_type: RequestType = RequestType.GET,
    ) -> dict:
        """
        Sends an HTTP request and logs the result.

        Args:
            url (str): The request URL.
            params (Optional[dict]): Query parameters.
            json (Optional[dict]): JSON body for POST requests.
            request_type (RequestType): HTTP method (GET, POST, etc.).

        Returns:
            dict: Parsed JSON response (may be empty if request fails).
        """
        default_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/119.0.0.0 Safari/537.36",
            "Host": "www.marathonbet.com"
        }

        self.log(
            f"Sending {request_type} request to {url}, params: {params}, json: {json}"
        )

        response = await send_request(
            method=request_type,
            url=url,
            params=params,
            json=json,
            headers=default_headers
        )

        short_response = str(response)[:200]
        self.log(f"Get response from {url}: {short_response}")

        return response
