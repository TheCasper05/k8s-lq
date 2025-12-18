"""
Redis client module with Pub/Sub support.
Handles message broadcasting across WebSocket server instances.
"""

import asyncio
import logging
from collections.abc import Callable
from typing import Any

import orjson
import redis.asyncio as aioredis
from redis.asyncio.client import PubSub

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisClient:
    """
    Redis client for pub/sub and caching operations.
    Manages connections and provides fanout messaging for WebSocket instances.
    """

    def __init__(self):
        self.redis: aioredis.Redis | None = None
        self.pubsub: PubSub | None = None
        self.subscribed_channels: set[str] = set()
        self.message_handlers: dict[str, Callable] = {}
        self._listener_task: asyncio.Task | None = None
        self._is_listening = False

    async def connect(self):
        """Establish connection to Redis."""
        try:
            self.redis = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=False,  # We'll handle decoding with orjson
                max_connections=settings.redis_max_connections,
            )

            # Test connection
            await self.redis.ping()
            logger.info(f"Connected to Redis at {settings.redis_host}:{settings.redis_port}")

            # Initialize pubsub
            self.pubsub = self.redis.pubsub()

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e!s}")
            raise

    async def disconnect(self):
        """Close Redis connection and cleanup."""
        try:
            self._is_listening = False

            if self._listener_task and not self._listener_task.done():
                self._listener_task.cancel()
                import contextlib

                with contextlib.suppress(asyncio.CancelledError):
                    await self._listener_task

            if self.pubsub:
                await self.pubsub.unsubscribe()
                await self.pubsub.close()

            if self.redis:
                await self.redis.close()

            logger.info("Disconnected from Redis")

        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e!s}")

    async def publish(self, channel: str, message: dict[str, Any]) -> int:
        """
        Publish message to Redis channel.

        Args:
            channel: Channel name
            message: Message dictionary to publish

        Returns:
            Number of subscribers that received the message
        """
        try:
            # Serialize message with orjson for performance
            serialized = orjson.dumps(message)

            # Publish to channel
            subscribers = await self.redis.publish(channel, serialized)

            logger.debug(f"Published to channel '{channel}': {subscribers} subscribers")
            return subscribers

        except Exception as e:
            logger.error(f"Failed to publish to channel '{channel}': {e!s}")
            raise

    async def subscribe(self, channel: str, handler: Callable):
        """
        Subscribe to Redis channel with a message handler.

        Args:
            channel: Channel name to subscribe to
            handler: Async function to handle incoming messages
        """
        try:
            if channel in self.subscribed_channels:
                logger.warning(f"Already subscribed to channel '{channel}'")
                return

            # Store handler
            self.message_handlers[channel] = handler

            # Subscribe to channel
            await self.pubsub.subscribe(channel)
            self.subscribed_channels.add(channel)

            logger.info(f"Subscribed to Redis channel: {channel}")

            # Start listener if not running
            if not self._is_listening:
                await self._start_listener()

        except Exception as e:
            logger.error(f"Failed to subscribe to channel '{channel}': {e!s}")
            raise

    async def unsubscribe(self, channel: str):
        """
        Unsubscribe from Redis channel.

        Args:
            channel: Channel name to unsubscribe from
        """
        try:
            if channel not in self.subscribed_channels:
                logger.warning(f"Not subscribed to channel '{channel}'")
                return

            await self.pubsub.unsubscribe(channel)
            self.subscribed_channels.discard(channel)
            self.message_handlers.pop(channel, None)

            logger.info(f"Unsubscribed from Redis channel: {channel}")

        except Exception as e:
            logger.error(f"Failed to unsubscribe from channel '{channel}': {e!s}")
            raise

    async def _start_listener(self):
        """Start background task to listen for pub/sub messages."""
        if self._is_listening:
            return

        self._is_listening = True
        self._listener_task = asyncio.create_task(self._listen_for_messages())
        logger.info("Started Redis pub/sub listener")

    async def _listen_for_messages(self):
        """
        Background task that listens for pub/sub messages.
        Routes messages to registered handlers.
        """
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = (
                        message["channel"].decode()
                        if isinstance(message["channel"], bytes)
                        else message["channel"]
                    )
                    data = message["data"]

                    # Deserialize message
                    try:
                        if isinstance(data, bytes):
                            decoded_message = orjson.loads(data)
                        else:
                            decoded_message = data

                        # Route to handler
                        handler = self.message_handlers.get(channel)
                        if handler:
                            await handler(channel, decoded_message)
                        else:
                            logger.warning(f"No handler for channel '{channel}'")

                    except Exception as e:
                        logger.error(f"Error processing message from '{channel}': {e!s}")

        except asyncio.CancelledError:
            logger.info("Redis listener task cancelled")
        except Exception as e:
            logger.error(f"Error in Redis listener: {e!s}")
            self._is_listening = False

    async def get(self, key: str) -> Any | None:
        """
        Get value from Redis by key.

        Args:
            key: Redis key

        Returns:
            Deserialized value or None if not found
        """
        try:
            value = await self.redis.get(key)
            if value is None:
                return None

            # Deserialize with orjson
            return orjson.loads(value)

        except Exception as e:
            logger.error(f"Failed to get key '{key}': {e!s}")
            return None

    async def set(self, key: str, value: Any, expire: int | None = None):
        """
        Set value in Redis.

        Args:
            key: Redis key
            value: Value to store (will be JSON serialized)
            expire: Optional expiration time in seconds
        """
        try:
            serialized = orjson.dumps(value)
            await self.redis.set(key, serialized, ex=expire)

        except Exception as e:
            logger.error(f"Failed to set key '{key}': {e!s}")
            raise

    async def delete(self, key: str):
        """
        Delete key from Redis.

        Args:
            key: Redis key to delete
        """
        try:
            await self.redis.delete(key)

        except Exception as e:
            logger.error(f"Failed to delete key '{key}': {e!s}")
            raise

    async def is_connected(self) -> bool:
        """
        Check if Redis connection is alive.

        Returns:
            True if connected, False otherwise
        """
        try:
            if not self.redis:
                return False
            await self.redis.ping()
            return True
        except Exception:
            return False


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """
    Dependency to get Redis client instance.

    Returns:
        RedisClient instance
    """
    return redis_client


def get_tenant_channel(tenant_id: str) -> str:
    """
    Generate Redis channel name for a tenant.

    Args:
        tenant_id: Tenant identifier

    Returns:
        Redis channel name
    """
    return f"tenant:{tenant_id}"


def get_user_channel(user_id: str) -> str:
    """
    Generate Redis channel name for a specific user.

    Args:
        user_id: User identifier

    Returns:
        Redis channel name
    """
    return f"user:{user_id}"


def get_global_channel() -> str:
    """
    Generate Redis channel name for global broadcasts.
    This channel is used to send messages to all connected users
    regardless of tenant.

    Returns:
        Redis channel name
    """
    return "global:broadcast"
