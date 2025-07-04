"""
AsyncLoopManager is a utility class that repeatedly runs an asynchronous task
in the background with optional error handling and retry intervals.

It is useful for managing long-running background jobs such as periodic data fetching,
syncing, or monitoring services.
"""

import asyncio
from asyncio import Task
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import TypeVar

from app.common.logger import log

T = TypeVar("T")


class AsyncLoopManager:
    """
    Manages an asynchronous loop that repeatedly calls a target coroutine
    with optional retry logic on failure.

    Attributes:
        _initializer (Callable): Optional coroutine to initialize the loop.
        _target (Callable): The target coroutine to be executed repeatedly.
        _args (tuple): Positional arguments passed to the target function.
        _kwargs (dict): Keyword arguments passed to the target function.
        _run (bool): Flag indicating whether the loop should continue running.
        _task (Task | None): The asyncio task running the loop.
        _last_iteration_finished_at (datetime | None): Timestamp of the last loop iteration completion.
        _interval_on_error (int): Wait time in seconds after an error occurs, increases on repeated failures.
        _interval_between (float): Delay between successful iterations.
    """

    def __init__(
        self,
        loop_on: Callable[[T], Awaitable],
        initializer: Callable[[], Awaitable[T]] | None = None,
        loop_on_args: tuple = (),
        loop_on_kwargs: dict | None = None,
        interval_on_error: int = 10,
        interval_between: float = 0,
    ):
        """
        Initializes the AsyncLoopManager.

        Args:
            loop_on (Callable): The coroutine to be run in a loop.
            initializer (Callable | None): Optional coroutine to provide init state or context.
            loop_on_args (tuple): Positional arguments to pass to the loop_on function.
            loop_on_kwargs (dict | None): Keyword arguments to pass to the loop_on function.
            interval_on_error (int): Initial wait time in seconds after an error.
            interval_between (float): Delay in seconds between each successful iteration.
        """
        self._initializer = initializer
        self._target = loop_on
        self._args = loop_on_args
        self._kwargs = loop_on_kwargs if loop_on_kwargs else {}
        self._run = False
        self._task: Task | None = None
        self._last_iteration_finished_at: datetime | None = None
        self._interval_on_error = interval_on_error
        self._interval_between = interval_between

    def start(self) -> None:
        """
        Starts the background loop by creating an asyncio task.
        """
        self._last_iteration_finished_at = None
        self._run = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self, join: bool = False) -> None:
        """
        Stops the running loop.

        Args:
            join (bool): If True, waits for the current task to finish after cancelling.
        """
        self._run = False
        if join and self._task:
            self._task.cancel()
            await self._task

    async def _loop(self) -> None:
        """
        Internal coroutine that runs the target function repeatedly.
        On exception, it retries after a delay and increases the delay
        progressively up to a maximum of 1800 seconds (30 minutes).
        """
        while self._run:
            try:
                await self._target(*self._args, **self._kwargs)
                await asyncio.sleep(self._interval_between)
            except Exception as e:
                log(f"AsyncLoopManager error {e}", force=True)
                await asyncio.sleep(self._interval_on_error)
                self._interval_on_error *= 2
                if self._interval_on_error > 1800:
                    self._interval_on_error = 1800
            self._last_iteration_finished_at = datetime.utcnow()

    def debug_info(self) -> dict:
        """
        Returns diagnostic information about the loop status.

        Returns:
            dict: Contains keys like 'running', 'last_iteration_finished_at',
                  'interval_on_error', and 'interval_between'.
        """
        return {
            "running": self._run,
            "last_iteration_finished_at": self._last_iteration_finished_at,
            "interval_on_error": self._interval_on_error,
            "interval_between": self._interval_between,
            "has_active_task": self._task is not None and not self._task.done(),
        }
