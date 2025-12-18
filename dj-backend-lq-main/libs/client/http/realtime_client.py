"""
Client for LQ Realtime Service API.

Provides methods to interact with the Realtime Service HTTP endpoints.
"""

from typing import Any


from .base import AsyncHTTPClient, HttpClientConfig
from .realtime_models import (
    GlobalBroadcastRequest,
    SendMessageRequest,
    SendMessageResponse,
    WebhookResponse,
)


class RealtimeClientConfig(HttpClientConfig):
    """Configuration for Realtime Service client."""

    api_key: str | None = None


class RealtimeClient:
    """
    Client for LQ Realtime Service API.

    Provides methods to interact with all HTTP endpoints of the Realtime Service.

    Example:
        ```python
        async with RealtimeClient(
            base_url="http://localhost:8082",
            api_key="your-system-api-key"
        ) as client:
            # Health check
            health = await client.health_check()
            print(f"Service status: {health.status}")

            # Send notification to user
            response = await client.send_to_user(
                user_id="user_123",
                message_type="notification",
                payload={"title": "Hello", "message": "World"}
            )
            print(f"Message sent: {response.success}")
        ```
    """

    def __init__(
        self,
        config: RealtimeClientConfig | dict[str, Any] | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize Realtime Service client.

        Args:
            config: RealtimeClientConfig object or dict
            base_url: Base URL for the Realtime Service (e.g., "http://localhost:8082")
            api_key: System API key for authenticated endpoints
            **kwargs: Additional config parameters
        """
        # Handle config initialization
        if isinstance(config, RealtimeClientConfig):
            self.config = config
        elif isinstance(config, dict):
            self.config = RealtimeClientConfig(**config)
        else:
            config_kwargs = kwargs.copy()
            if base_url:
                config_kwargs["base_url"] = base_url
            if api_key:
                config_kwargs["api_key"] = api_key
            self.config = RealtimeClientConfig(**config_kwargs)

        # Create HTTP client with base config
        http_config = HttpClientConfig(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=self.config.headers,
            verify_ssl=self.config.verify_ssl,
            follow_redirects=self.config.follow_redirects,
        )
        self.http_client = AsyncHTTPClient(config=http_config)

    async def __aenter__(self) -> "RealtimeClient":
        """Enter async context manager."""
        await self.http_client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        await self.http_client.__aexit__(exc_type, exc_val, exc_tb)

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers with API key."""
        if not self.config.api_key:
            raise ValueError("API key is required for this endpoint")
        return {"X-API-Key": self.config.api_key}

    def _build_message_request(
        self,
        payload: dict[str, Any],
        message_type: str,
        from_user: str,
    ) -> SendMessageRequest:
        """Build a SendMessageRequest object."""
        return SendMessageRequest(
            message_type=message_type,
            payload=payload,
            from_user=from_user,
        )

    def _build_broadcast_request(
        self,
        payload: dict[str, Any],
        message_type: str,
        from_user: str,
    ) -> GlobalBroadcastRequest:
        """Build a GlobalBroadcastRequest object."""
        return GlobalBroadcastRequest(
            message_type=message_type,
            payload=payload,
            from_user=from_user,
        )

    async def _send_message(
        self,
        endpoint: str,
        payload: dict[str, Any],
        message_type: str,
        from_user: str,
    ) -> SendMessageResponse:
        """
        Internal method to send messages to any endpoint.

        Args:
            endpoint: API endpoint path
            payload: Message payload
            message_type: Type of message
            from_user: Sender identifier

        Returns:
            SendMessageResponse with send result
        """
        request_data = self._build_message_request(payload, message_type, from_user)

        response = await self.http_client.post(
            endpoint,
            json=request_data.model_dump(),
            headers=self._get_auth_headers(),
        )
        response.raise_for_status()
        return SendMessageResponse(**response.json())

    async def close(self) -> None:
        """Close the client connection."""
        await self.http_client.close()

    async def broadcast_global(
        self,
        payload: dict[str, Any],
        message_type: str = "system",
        from_user: str = "system",
    ) -> SendMessageResponse:
        """
        Send a global broadcast to all connected users.

        Args:
            payload: Message payload
            message_type: Type of message (default: "system")
            from_user: Sender identifier (default: "system")

        Returns:
            SendMessageResponse with broadcast result

        Raises:
            ValueError: If API key is not configured
            httpx.HTTPStatusError: If request fails

        Example:
            ```python
            response = await client.broadcast_global(
                payload={
                    "title": "Maintenance",
                    "message": "System will be down in 10 minutes"
                },
                message_type="system"
            )
            print(f"Reached {response.subscribers_reached} instances")
            ```
        """
        request_data = self._build_broadcast_request(payload, message_type, from_user)

        response = await self.http_client.post(
            "/api/broadcast/global",
            json=request_data.model_dump(),
            headers=self._get_auth_headers(),
        )
        response.raise_for_status()
        return SendMessageResponse(**response.json())

    async def send_to_user(
        self,
        user_id: str,
        payload: dict[str, Any],
        message_type: str = "notification",
        from_user: str = "backend",
    ) -> SendMessageResponse:
        """
        Send a message to all sessions of a specific user.

        Args:
            user_id: ID of the target user
            payload: Message payload
            message_type: Type of message (default: "notification")
            from_user: Sender identifier (default: "backend")

        Returns:
            SendMessageResponse with send result

        Raises:
            ValueError: If API key is not configured
            httpx.HTTPStatusError: If request fails

        Example:
            ```python
            response = await client.send_to_user(
                user_id="user_123",
                payload={
                    "title": "New Lesson",
                    "lesson_id": "lesson_456",
                    "action": "open_lesson"
                }
            )
            print(f"Sent to {response.local_connections} connections")
            ```
        """
        return await self._send_message(
            endpoint=f"/api/messages/user/{user_id}",
            payload=payload,
            message_type=message_type,
            from_user=from_user,
        )

    async def send_to_tenant(
        self,
        tenant_id: str,
        payload: dict[str, Any],
        message_type: str = "notification",
        from_user: str = "backend",
    ) -> SendMessageResponse:
        """
        Send a message to all users in a tenant.

        Args:
            tenant_id: ID of the target tenant
            payload: Message payload
            message_type: Type of message (default: "notification")
            from_user: Sender identifier (default: "backend")

        Returns:
            SendMessageResponse with send result

        Raises:
            ValueError: If API key is not configured
            httpx.HTTPStatusError: If request fails

        Example:
            ```python
            response = await client.send_to_tenant(
                tenant_id="org_123",
                payload={
                    "title": "Team Update",
                    "message": "New feature released"
                }
            )
            print(f"Sent to {response.local_connections} users in tenant")
            ```
        """
        return await self._send_message(
            endpoint=f"/api/messages/tenant/{tenant_id}",
            payload=payload,
            message_type=message_type,
            from_user=from_user,
        )

    async def send_to_room(
        self,
        room_id: str,
        payload: dict[str, Any],
        message_type: str = "notification",
        from_user: str = "backend",
    ) -> SendMessageResponse:
        """
        Send a message to all users subscribed to a room.

        Args:
            room_id: ID of the target room (e.g., "lesson:123", "chat:456")
            payload: Message payload
            message_type: Type of message (default: "notification")
            from_user: Sender identifier (default: "backend")

        Returns:
            SendMessageResponse with send result

        Raises:
            ValueError: If API key is not configured
            httpx.HTTPStatusError: If request fails

        Example:
            ```python
            response = await client.send_to_room(
                room_id="lesson:123",
                payload={
                    "event": "user_joined",
                    "user_name": "Juan Pérez"
                }
            )
            print(f"Sent to {response.local_connections} users in room")
            ```
        """
        return await self._send_message(
            endpoint=f"/api/messages/room/{room_id}",
            payload=payload,
            message_type=message_type,
            from_user=from_user,
        )

    async def send_webhook(
        self,
        provider: str,
        data: dict[str, Any],
        signature: str | None = None,
        tenant_id: str | None = None,
    ) -> WebhookResponse:
        """
        Send a webhook to the service.

        Args:
            provider: Webhook provider (stripe, github, slack, twilio, sendgrid, custom)
            data: Webhook payload data
            signature: Optional HMAC SHA256 signature
            tenant_id: Optional tenant ID

        Returns:
            WebhookResponse with webhook result

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            ```python
            response = await client.send_webhook(
                provider="stripe",
                data={
                    "type": "charge.succeeded",
                    "data": {"amount": 1000, "currency": "usd"}
                },
                tenant_id="tenant_123"
            )
            print(f"Webhook accepted: {response.event_id}")
            ```
        """
        headers: dict[str, str] = {}
        if signature:
            headers["X-Signature"] = signature
        if tenant_id:
            headers["X-Tenant-ID"] = tenant_id

        response = await self.http_client.post(
            f"/webhooks/{provider}", json=data, headers=headers
        )
        response.raise_for_status()
        return WebhookResponse(**response.json())
