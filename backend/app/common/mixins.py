"""
Mixin to provide logging capability to any class.

This mixin adds a `self.log(...)` method that automatically prefixes
log messages with the class name, making it easier to trace logs.
"""

from typing import Any

from app.common.logger import log


class LogMixin:
    """
    Mixin class that adds a simple logging method to any class that inherits from it.

    Methods:
        log(msg: Any, force: bool = False): Logs a message with the class name as prefix.
    """

    def log(self, msg: Any, force: bool = False) -> None:
        """
        Logs a message prefixed with the class name.

        Args:
            msg (Any): The message to log.
            force (bool): If True, forces the message to be logged regardless of log level settings.
        """
        log(f"{self.__class__.__name__} {msg}", force=force)
