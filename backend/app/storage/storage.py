"""
Storage service that consumes Event objects, stores them in Redis, and maintains secondary indexes.

This service listens to event updates using the Observer pattern and processes them asynchronously.
"""

import asyncio

from asyncio import Queue
from datetime import datetime

from app.common.helpers import tokenize
from app.common.observable import Observer, DataType, EventType
from app.converter.schemas import Event
from app.managers.redis_service import Redis


class Storage(Observer):
    """
    Asynchronous storage processor for handling finalized event data.

    Responsibilities:
    - Listens for Event updates via the Observer pattern.
    - Deduplicates and stores event data in Redis.
    - Builds indexes for time, sport, and keyword-based lookups.

    Attributes:
        redis_service (Redis): Redis utility instance.
        queue (Queue): Internal async queue for processing events.
        processing (bool): Whether queue processing is active.
        last_update (datetime | None): Timestamp of the last successful event processing.
        _wait_task (asyncio.Task | None): Currently awaited queue task.
    """

    def __init__(self, redis_service: Redis):
        """
        Initializes the Storage service.

        Args:
            redis_service (Redis): Redis client for storing event data.
        """
        self.processing: bool = True
        self.queue = Queue()
        self.last_update: datetime | None = None
        self._wait_task: asyncio.Task | None = None
        self.redis_service: Redis = redis_service

    def update(
        self, data: Event, data_type: DataType, event_type: EventType
    ) -> None:
        """
        Handles observable updates and enqueues events for processing.

        Args:
            data (Event): The event object to store.
            data_type (DataType): The type of incoming data.
            event_type (EventType): The type of update event (CREATE, UPDATE, DELETE).
        """
        if event_type == EventType.UPDATE and data_type == DataType.EVENT:
            self.add_data(data)

    def debug_info(self) -> dict:
        """
        Returns debugging statistics about the storage queue.

        Returns:
            dict: Queue size and last update timestamp.
        """
        return {
            "queue_size": self.queue.qsize(),
            "last_update": self.last_update,
        }

    def clean(self) -> None:
        """
        Clears the queue and resets last update timestamp.
        """
        self.log("Starting cleaning storage data", force=True)
        self.queue._queue.clear()
        self.last_update = datetime.now()
        self.log("Storage data cleaned", force=True)

    def add_data(self, data: list) -> None:
        """
        Adds new data to the queue for background processing.

        Args:
            data (list): The event data to store.
        """
        self.queue.put_nowait(data)

    async def start_loop(self):
        """
        Starts the infinite loop for processing events from the queue.
        """
        while True:
            await self.process_queue()
            await asyncio.sleep(1)

    async def process_queue(self) -> None:
        """
        Internal method that fetches data from the queue and processes it.

        Handles errors gracefully and logs progress.
        """
        try:
            while self.processing:
                self._wait_task = asyncio.create_task(self.queue.get())
                data = await self._wait_task

                short_data = str(data)[:200]
                self.log(f"Processing queue: {short_data}, {self.queue.qsize()}")

                try:
                    await self.process_data(data)
                except Exception as e:
                    self.log(f"Error while working with processing data: {e}", force=True)

                self.last_update = datetime.now()
        except asyncio.CancelledError:
            pass

    async def process_data(self, event: Event) -> None:
        """
        Saves a new event to Redis and updates related indexes.

        Performs checks to avoid duplicate storage.

        Args:
            event (Event): The event object to process and store.
        """
        key = event.extra["key"]

        if await self.redis_service.check_exist_key(key):
            self.log(f"Already present event for key {key}")
            return

        # Store event
        await self.redis_service.add_event(key, event.to_redis())
        self.log(f"New event added with key {key}")

        # Time-based index
        timestamp = int(event.metadata.start_time)
        await self.redis_service.add_index_by_range("index:events_by_time", {key: timestamp})

        # Sport-based index
        sport = event.sport.lower()
        await self.redis_service.add_index_by_word(f"index:sport:{sport}", key)

        # Keyword-based index from competition name
        for word in tokenize(event.metadata.competition_name):
            await self.redis_service.add_index_by_word(f"index:category_word:{word}", key)

    def stop_processing(self) -> None:
        """
        Stops processing the queue and cancels the current wait task if active.
        """
        self.log("Stop storage processing")
        self.processing = False
        if self._wait_task is not None:
            self._wait_task.cancel()

    def start_processing(self) -> None:
        """
        Resumes processing of queued events.
        """
        self.log("Start storage processing")
        self.processing = True
