"""
Observable-Observer pattern implementation for handling event-based updates.

This module defines:
- `DataType` and `EventType`: Constants to identify data and event types.
- `Observer`: A base class for any component that wants to receive updates.
- `Observable`: A class that manages subscribers and notifies them of changes.
"""

from typing import Any

from app.common.mixins import LogMixin


class DataType:
    """
    Enum-like class representing types of data that can trigger updates.

    Attributes:
        EVENT (str): Represents event-related data.
    """
    EVENT = "event"


class EventType:
    """
    Enum-like class representing types of update events.

    Attributes:
        CREATE (str): Indicates data creation.
        UPDATE (str): Indicates data update.
        DELETE (str): Indicates data deletion.
    """
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Observer(LogMixin):
    """
    Base class for observers that react to updates from Observable.

    Inherits:
        LogMixin: Provides self.log(...) for consistent logging.

    Methods:
        update(data, data_type, event_type): Handles an incoming update.
    """

    def update(
        self, data: dict[str, Any], data_type: DataType, event_type: EventType
    ) -> None:
        """
        Called when the Observable sends a notification.

        Args:
            data (dict): The data payload associated with the update.
            data_type (DataType): The category/type of the data.
            event_type (EventType): The type of event (create, update, delete).
        """
        short_data = str(data)[:100]
        self.log(f"Data has been updated: {data_type}, {event_type}, {short_data}")


class Observable:
    """
    Class that manages a list of observers and notifies them of updates.

    Methods:
        subscribe(observer): Adds an observer to the list.
        unsubscribe(observer): Removes an observer from the list.
        notify(data, data_type, event_type): Sends an update to all observers.
    """

    def __init__(self) -> None:
        """
        Initializes the observable with an empty list of observers.
        """
        self.observers: list[Observer] = []

    def notify(
        self, data: dict[str, Any], data_type: DataType, event_type: EventType
    ) -> None:
        """
        Notifies all subscribed observers with the given data.

        Args:
            data (dict): The data payload.
            data_type (DataType): The type of the data.
            event_type (EventType): The type of update event.
        """
        for observer in self.observers:
            observer.update(data, data_type, event_type)

    def subscribe(self, observer: Observer) -> None:
        """
        Subscribes a new observer to receive updates.

        Args:
            observer (Observer): The observer instance to add.
        """
        self.observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        """
        Unsubscribes an observer from receiving further updates.

        Args:
            observer (Observer): The observer instance to remove.
        """
        self.observers.remove(observer)
