"""
Main script to initialize and run background services: Scraper, Converter, and Storage.

Modules:
- Scraper: collects data from external sources.
- Converter: transforms raw data into a desired format.
- Storage: persists processed data into Redis.
- AsyncLoopManager: manages periodic asynchronous tasks.

Functions:
- run_services(): starts all core async services and ensures fault tolerance.
"""

import asyncio

from app.common.async_loop_manager import AsyncLoopManager
from app.common.service_utils import service_utils
from app.converter.converter import Converter
from app.scraper.schemas import UpdateType
from app.scraper.scraper import Scraper
from app.managers.redis_service import Redis
from app.storage.storage import Storage

redis_service = Redis()

converter = Converter()
storage = Storage(redis_service=redis_service)

converter.on_event.subscribe(storage)

scraper = Scraper(converter=converter)
scraper_update_loop = AsyncLoopManager(
    loop_on=scraper.update,
    loop_on_args=(UpdateType.EVENTS_RESULTS,),
    interval_on_error=60 * 10,  # retry after 10 minutes on error
    interval_between=60 * 30,   # run every 30 minutes normally
)


async def run_services():
    """
        Starts the scraper update loop and concurrently runs the
        converter and storage services with automatic restart on failure.
    """
    scraper_update_loop.start()

    await asyncio.gather(
        service_utils.restart_on_failure(converter.start_loop),
        service_utils.restart_on_failure(storage.start_loop)
    )
