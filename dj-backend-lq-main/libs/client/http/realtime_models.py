"""
Pydantic models for LQ Realtime Service API.

Based on the API documentation in API_REALTIME.md
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# Enums
class WSMessageType(str, Enum):
    """WebSocket message types."""

    PING = "ping"
    PONG = "pong"
    MESSAGE = "message"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"
    SYSTEM = "system"
    ERROR = "error"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


class HealthStatus(str, Enum):
    """Health check status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"


# Request Models
class GlobalBroadcastRequest(BaseModel):
    """Request model for global broadcast endpoint."""

    message_type: WSMessageType = Field(
        default=WSMessageType.SYSTEM, description="Type of message to broadcast"
    )
    payload: dict[str, Any] = Field(..., description="Message payload")
    from_user: str = Field(default="system", description="Sender identifier")


class SendMessageRequest(BaseModel):
    """Request model for sending messages to user/tenant/room."""

    message_type: WSMessageType = Field(
        default=WSMessageType.NOTIFICATION, description="Type of message to send"
    )
    payload: dict[str, Any] = Field(..., description="Message payload")
    from_user: str = Field(default="backend", description="Sender identifier")


class SubscribeRequest(BaseModel):
    """Request model for subscribing to rooms."""

    rooms: list[str] = Field(..., description="List of room IDs to subscribe to")


class UnsubscribeRequest(BaseModel):
    """Request model for unsubscribing from rooms."""

    rooms: list[str] = Field(..., description="List of room IDs to unsubscribe from")


# Response Models
class RootResponse(BaseModel):
    """Response model for root endpoint."""

    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    status: str = Field(..., description="Service status")
    docs: str = Field(..., description="Documentation URL")


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""

    status: HealthStatus = Field(..., description="Service health status")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Health check timestamp (ISO 8601)")
    redis_connected: bool = Field(..., description="Redis connection status")
    active_connections: int = Field(
        ..., description="Number of active WebSocket connections"
    )


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""

    active_websocket_connections: int = Field(
        ..., description="Active WebSocket connections"
    )
    total_messages_sent: int = Field(..., description="Total messages sent")
    total_messages_received: int = Field(..., description="Total messages received")
    total_webhooks_processed: int = Field(..., description="Total webhooks processed")
    redis_pubsub_channels: int = Field(
        ..., description="Number of Redis pub/sub channels"
    )
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    memory_usage_mb: float = Field(..., description="Memory usage in megabytes")


class SendMessageResponse(BaseModel):
    """Response model for message sending endpoints."""

    success: bool = Field(..., description="Whether the message was sent successfully")
    message: str = Field(..., description="Status message")
    subscribers_reached: int = Field(
        ..., description="Number of Redis instances reached"
    )
    local_connections: int = Field(
        default=0, description="Number of local connections reached"
    )
    timestamp: str = Field(
        ..., description="Timestamp of the send operation (ISO 8601)"
    )


class WebhookResponse(BaseModel):
    """Response model for webhook endpoint."""

    status: str = Field(..., description="Webhook processing status")
    event_id: str = Field(..., description="Event ID")


# Data Models
class TokenPayload(BaseModel):
    """JWT token payload for WebSocket authentication."""

    sub: str = Field(..., description="User ID (subject)")
    tenant_id: str = Field(..., description="Tenant/organization ID")
    scope: str = Field(..., description="Token scope (must be 'realtime')")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int | None = Field(None, description="Issued at timestamp")
    session_id: str | None = Field(None, description="Django session ID")
    jti: str = Field(..., description="Token ID (unique identifier)")
    user_role: str | None = Field(None, description="User role")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class WSMessage(BaseModel):
    """WebSocket message structure."""

    type: WSMessageType = Field(..., description="Message type")
    payload: dict[str, Any] = Field(..., description="Message payload")
    timestamp: str = Field(..., description="Message timestamp (ISO 8601)")
    message_id: str | None = Field(None, description="Unique message ID")
    from_user: str | None = Field(None, description="Sender user ID")
    to_user: str | None = Field(None, description="Recipient user ID")


class WSConnectionInfo(BaseModel):
    """WebSocket connection information."""

    user_id: str = Field(..., description="User ID")
    tenant_id: str = Field(..., description="Tenant ID")
    connection_id: str = Field(..., description="Unique connection ID")
    connected_at: str = Field(..., description="Connection timestamp (ISO 8601)")
    last_activity: str = Field(..., description="Last activity timestamp (ISO 8601)")
    session_id: str | None = Field(None, description="Django session ID")
    token_jti: str | None = Field(None, description="JWT token JTI")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class DebugConnectionsStats(BaseModel):
    """Statistics for debug connections endpoint."""

    active_connections: int = Field(..., description="Number of active connections")
    unique_users: int = Field(..., description="Number of unique users")
    unique_tenants: int = Field(..., description="Number of unique tenants")
    subscribed_channels: int = Field(..., description="Number of subscribed channels")
    total_messages_sent: int = Field(..., description="Total messages sent")
    total_messages_received: int = Field(..., description="Total messages received")


class DebugConnectionsResponse(BaseModel):
    """Response model for debug connections endpoint."""

    stats: DebugConnectionsStats = Field(..., description="Connection statistics")
    connections: list[WSConnectionInfo] = Field(
        ..., description="List of active connections"
    )


# Error Models
class ErrorDetail(BaseModel):
    """Error detail information."""

    reason: str | None = Field(None, description="Detailed error reason")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error code or type")
    message: str = Field(..., description="Human-readable error message")
    detail: ErrorDetail | dict[str, Any] | None = Field(
        None, description="Additional error details"
    )
    timestamp: str = Field(..., description="Error timestamp (ISO 8601)")


# Room Subscription Models
class RoomSubscriptionResponse(BaseModel):
    """Response for room subscription/unsubscription."""

    message: str = Field(..., description="Status message")
    subscribed: list[str] | None = Field(
        None, description="Successfully subscribed rooms"
    )
    failed: list[str] | None = Field(None, description="Failed room subscriptions")
    total: int | None = Field(None, description="Total number of rooms processed")
    rooms: list[str] | None = Field(
        None, description="List of affected rooms (for unsubscribe)"
    )


# Ping/Pong Models
class PingMessage(BaseModel):
    """Ping message payload."""

    type: WSMessageType = Field(default=WSMessageType.PING, description="Message type")
    payload: dict[str, Any] = Field(default_factory=dict, description="Empty payload")


class PongMessage(BaseModel):
    """Pong response payload."""

    type: WSMessageType = Field(default=WSMessageType.PONG, description="Message type")
    payload: dict[str, Any] = Field(..., description="Pong payload with timestamp")
    timestamp: str = Field(..., description="Server timestamp (ISO 8601)")
