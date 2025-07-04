"""
Converter service that transforms raw scraped data into structured Event objects.

This class consumes data from an internal async queue, processes finished football events,
and notifies observers about each converted event using the Observer pattern.
"""

import asyncio
from asyncio import Queue
from datetime import datetime
from typing import Tuple, Any

from app.common.observable import Observer, Observable, DataType, EventType
from app.converter.schemas import EventState, EventMetadata, Event


class Converter(Observer):
    """
    Asynchronous data converter that receives raw event trees and transforms them
    into structured Event schemas. It supports real-time queue processing and notifies
    observers when new or updated events are created.

    Inherits:
        Observer: Allows the converter to receive updates if needed.
    """

    def __init__(self):
        """
        Initializes the Converter instance with an empty queue and event broadcaster.
        """
        self.processing: bool = True
        self.queue = Queue()
        self.on_event: Observable = Observable()
        self.last_changed: datetime | None = None
        self._wait_task: asyncio.Task | None = None

    def debug_info(self) -> dict:
        """
        Returns a dictionary with debugging information about the queue.

        Returns:
            dict: Contains current queue size and timestamp of last update.
        """
        return {
            "queue_size": self.queue.qsize(),
            "last_changed": self.last_changed,
        }

    def clean(self) -> None:
        """
        Clears the queue and resets last changed timestamp.
        """
        self.log("Starting cleaning converter data", force=True)
        self.queue._queue.clear()
        self.last_changed = datetime.now()
        self.log("Converter data cleaned", force=True)

    def add_data(self, data: list) -> None:
        """
        Pushes raw event data into the processing queue.

        Args:
            data (list): A list of raw sport event structures.
        """
        self.queue.put_nowait(data)

    async def start_loop(self):
        """
        Starts the infinite processing loop to continuously process incoming data.
        """
        while True:
            await self.process_queue()
            await asyncio.sleep(1)

    async def process_queue(self) -> None:
        """
        Consumes items from the queue and processes them. Handles processing errors
        gracefully and logs them.
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

                self.last_changed = datetime.now()
        except asyncio.CancelledError:
            pass

    def stop_processing(self) -> None:
        """
        Stops queue processing and cancels the current wait task if needed.
        """
        self.log("Stop storage processing")
        self.processing = False
        if self._wait_task is not None:
            self._wait_task.cancel()

    def start_processing(self) -> None:
        """
        Resumes queue processing.
        """
        self.log("Start storage processing")
        self.processing = True

    async def process_data(self, data: list[dict]) -> None:
        """
        Processes incoming raw event data, converts finished football events into Event objects,
        and notifies observers.

        Args:
            data (list[dict]): A list of raw sport data structures.
        """
        try:
            for sport_events in data:
                sport = sport_events.get("name")

                for competition_events in sport_events.get("childs", []):
                    competition_id = competition_events.get("treeId")
                    competition_name = competition_events.get("name")

                    for event in competition_events.get("childs", []):
                        event_id = event.get("treeId")

                        if self._should_skip_event(event):
                            self.log(f"Skipping event with id {event_id}. It is still not finished.")
                            continue

                        event_schema = self._create_event(
                            event, event_id, sport, competition_id, competition_name
                        )

                        if event_schema:
                            self.on_event.notify(event_schema, DataType.EVENT, EventType.UPDATE)

                    await asyncio.sleep(0)  # Yield control to event loop
        except Exception as e:
            self.log(f"Unexpected error in process_data: {e}", force=True)

    def _should_skip_event(self, event: dict) -> bool:
        """
        Checks if the event should be skipped (e.g., not finished yet).

        Args:
            event (dict): The event dictionary to check.

        Returns:
            bool: True if event should be skipped.
        """
        return event.get("live") is True

    def _create_event(
        self,
        event: dict,
        event_id: int,
        sport: str,
        competition_id: int,
        competition_name: str
    ) -> Event | None:
        """
        Converts a raw event dictionary into a structured Event object.

        Args:
            event (dict): Raw event data.
            event_id (int): Unique ID of the event.
            sport (str): Sport name.
            competition_id (int): ID of the competition.
            competition_name (str): Name of the competition.

        Returns:
            Event | None: An Event object if valid, otherwise None.
        """
        try:
            event_state = EventState(
                scores=event.get("scores"),
            )

            home_team, away_team = self.extract_teams(event.get("name"))
            event_metadata = EventMetadata(
                competition_id=competition_id,
                competition_name=competition_name,
                home_team=home_team,
                away_team=away_team,
                start_time=event.get("date"),
                extra=event.get("results"),
            )

            event_schema = Event(
                event_id=event_id,
                sport=sport,
                metadata=event_metadata,
                state=event_state,
            )
            event_schema.extra["key"] = event_schema.key

            return event_schema
        except Exception:
            self.log(f"Error while converting Event, data: {event}")
            return None

    @staticmethod
    def extract_teams(raw: str) -> Tuple[str, str]:
        """
        Extracts home and away team names from a raw event name string.

        Args:
            raw (str): Raw string like "Team A vs Team B", possibly with HTML tags.

        Returns:
            Tuple[str, str]: A tuple containing (home_team, away_team).
        """
        html_tags = ["<b>", "</b>"]
        for tag in html_tags:
            raw = raw.replace(tag, "")
        text = raw.strip()

        sep = " vs "
        if sep in text:
            parts = text.split(sep, maxsplit=1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        return "", ""
