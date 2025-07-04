"""
Concrete implementation of BaseScraper for fetching Marathonbet event results.

This scraper fetches the root event tree from the /react/unionresults/resulttree endpoint.
"""

from app.scraper.base import BaseScraper
from app.scraper.schemas import UpdateType, RequestType


class Scraper(BaseScraper):
    """
    Marathonbet event results scraper.

    Fetches finished events data from the Marathonbet
    and passes the results to the converter for processing.

    Inherits:
        BaseScraper: Provides request logic, logging, and update orchestration.
    """
    async def get_updated_data(self, update_type: UpdateType) -> list[dict] | None:
        """
        Retrieves updated event data from the Marathonbet.

        Args:
            update_type (UpdateType): Type of update to fetch (currently unused but required by interface).

        Returns:
            list[dict] | None: List of sport/competition/event trees or None if data is invalid or missing.
        """
        self.log(f"Starting update data for {update_type}")

        response = await self.request(
            url=f"{self.domain}/en/react/unionresults/resulttree",
            request_type=RequestType.POST,
        )
        response_data = response.get("root", {}).get("childs", [])

        return response_data
