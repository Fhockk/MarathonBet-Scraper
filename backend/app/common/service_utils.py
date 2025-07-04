"""
Utility module for running and auto-restarting background async tasks.

This includes a helper class `ServiceUtils` that can execute a coroutine
and automatically restart it upon failure, using exponential backoff.
"""

import asyncio
from typing import Any

from app.common.mixins import LogMixin


class ServiceUtils(LogMixin):
    """
    Utility class that provides fault-tolerant execution of async tasks.

    Inherits:
        LogMixin: Provides structured logging with class name prefix.

    Methods:
        restart_on_failure(task, *args, **kwargs): Runs the task and restarts it with
        exponential backoff in case of exceptions.
    """

    async def restart_on_failure(self, task: Any, *args: Any, **kwargs: Any) -> None:
        """
        Executes the given asynchronous task and restarts it if it crashes.

        On each failure, it logs the error and retries with an increasing delay
        (exponential backoff). The delay doubles after each failure.

        Args:
            task (Any): The coroutine function to execute.
            *args (Any): Positional arguments for the task.
            **kwargs (Any): Keyword arguments for the task.
        """
        retry_delay = 4
        while True:
            try:
                await task(*args, **kwargs)
            except Exception as e:
                import traceback

                tracebak_data = str(traceback.format_exc())
                full_error = str(e) + "\n" + tracebak_data
                self.log(
                    f"Task failed with: {full_error}\nRestarting task in {retry_delay} seconds...", force=True
                )
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            else:
                break


# Singleton instance for reuse across the application
service_utils = ServiceUtils()
