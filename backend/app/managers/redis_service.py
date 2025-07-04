"""
Asynchronous Redis service wrapper.

This module provides a Redis utility class for storing and retrieving
event data and managing secondary indexes (e.g., time, sport, keywords).
"""

import redis.asyncio as aioredis

from app.common.mixins import LogMixin
from app.common.settings import settings


class Redis(LogMixin):
    """
    Redis service class for managing events and index structures.

    Provides methods to:
    - Store events and check their existence
    - Maintain time-based and keyword-based indexes
    - Fetch keys and values efficiently using Redis structures
    """

    def __init__(self):
        """
        Initializes the Redis client with configured connection settings.
        """
        self.redis = self._initialize_redis()

    def _initialize_redis(self) -> aioredis.Redis:
        """
        Creates an instance of the asynchronous Redis client.

        Returns:
            aioredis.Redis: Redis connection object.
        """
        return aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30,
        )

    async def check_exist_key(self, key: str) -> bool:
        """
        Checks if a given key exists in Redis.

        Args:
            key (str): The Redis key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return await self.redis.exists(key)

    async def add_event(self, key: str, event: str):
        """
        Stores a serialized event under a specific key.

        Args:
            key (str): Redis key to store the event under.
            event (str): Serialized event data (usually JSON).
        """
        return await self.redis.set(key, event)

    async def add_index_by_range(self, index: str, mapping: dict):
        """
        Adds score-based index entries using a sorted set (ZADD).

        Args:
            index (str): Name of the sorted set index.
            mapping (dict): Dictionary of {value: score}.
        """
        return await self.redis.zadd(index, mapping)

    async def add_index_by_word(self, index: str, value: str):
        """
        Adds a value to a set index for keyword lookup.

        Args:
            index (str): Name of the set index.
            value (str): Value to add to the set.
        """
        return await self.redis.sadd(index, value)

    async def get_keys_by_time(self, from_ts: int, to_ts: int) -> list[str]:
        """
        Fetches event keys from a sorted set within a timestamp range.

        Args:
            from_ts (int): Start timestamp (inclusive).
            to_ts (int): End timestamp (inclusive).

        Returns:
            list[str]: List of event keys within the time range.
        """
        return await self.redis.zrangebyscore("index:events_by_time", from_ts, to_ts)

    async def get_keys_by_sport(self, sport: str) -> set[str]:
        """
        Retrieves keys indexed by sport name.

        Args:
            sport (str): Sport name (case-insensitive).

        Returns:
            set[str]: Set of event keys for the given sport.
        """
        return set(await self.redis.smembers(f"index:sport:{sport.lower()}"))

    async def get_keys_by_words(self, words: list[str]) -> set[str]:
        """
        Finds keys that are present in all given keyword-based indexes.

        Args:
            words (list[str]): List of keywords to intersect.

        Returns:
            set[str]: Set of keys common to all keyword indexes.
        """
        result_sets = []
        for word in words:
            result_sets.append(set(await self.redis.smembers(f"index:category_word:{word}")))
        return set.intersection(*result_sets) if result_sets else set()

    async def get_events_by_keys(self, keys: list[str]) -> list[str]:
        """
        Retrieves multiple events by their Redis keys.

        Args:
            keys (list[str]): List of Redis keys to fetch.

        Returns:
            list[str]: List of serialized event strings (some may be None).
        """
        return await self.redis.mget(keys)
