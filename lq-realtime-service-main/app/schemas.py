"""
Pydantic schemas for request/response validation and data structures.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# ==================== JWT Schemas ====================


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: str = Field(..., description="Subject (user ID)")
    tenant_id: str = Field(..., description="Tenant/Organization ID")
    scope: str = Field(default="ws:connect", description="Token scope")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int | None = Field(None, description="Issued at timestamp")
    user_role: str | None = Field(None, description="User role")
    metadata: dict[str, Any] | None = Field(default_factory=dict, description="Additional metadata")


# ==================== WebSocket Schemas ====================


class WSMessageType(str, Enum):
    """WebSocket message types."""

    PING = "ping"
    PONG = "pong"
    MESSAGE = "message"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"
    ERROR = "error"
    SYSTEM = "system"


class WSMessage(BaseModel):
    """WebSocket message schema."""

    type: WSMessageType = Field(..., description="Message type")
    payload: dict[str, Any] = Field(default_factory=dict, description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    message_id: str | None = Field(None, description="Unique message identifier")
    from_user: str | None = Field(None, description="Sender user ID")
    to_user: str | None = Field(None, description="Target user ID")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class WSConnectionInfo(BaseModel):
    """WebSocket connection information."""

    user_id: str
    tenant_id: str
    connection_id: str
    connected_at: datetime
    last_activity: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


# ==================== Webhook Schemas ====================


class WebhookProvider(str, Enum):
    """Supported webhook providers."""

    STRIPE = "stripe"
    GITHUB = "github"
    SLACK = "slack"
    TWILIO = "twilio"
    SENDGRID = "sendgrid"
    CUSTOM = "custom"


class WebhookEvent(BaseModel):
    """Webhook event schema."""

    provider: WebhookProvider = Field(..., description="Webhook provider")
    event_type: str = Field(..., description="Event type from provider")
    event_id: str | None = Field(None, description="Unique event ID")
    payload: dict[str, Any] = Field(..., description="Event payload")
    received_at: datetime = Field(
        default_factory=datetime.utcnow, description="Event received timestamp"
    )
    signature: str | None = Field(None, description="Webhook signature")
    tenant_id: str | None = Field(None, description="Associated tenant ID")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class WebhookRegistration(BaseModel):
    """Webhook registration configuration."""

    provider: WebhookProvider
    tenant_id: str
    secret: str = Field(..., description="Webhook signing secret")
    enabled: bool = Field(default=True, description="Whether webhook is active")
    retry_policy: dict[str, Any] = Field(
        default_factory=lambda: {"max_retries": 3, "retry_delay": 5},
        description="Retry policy configuration",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# ==================== Response Schemas ====================


class HealthCheckResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(default="healthy", description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    redis_connected: bool = Field(..., description="Redis connection status")
    active_connections: int = Field(..., description="Number of active WebSocket connections")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class MetricsResponse(BaseModel):
    """Metrics response schema."""

    active_websocket_connections: int
    total_messages_sent: int
    total_messages_received: int
    total_webhooks_processed: int
    redis_pubsub_channels: int
    uptime_seconds: float
    memory_usage_mb: float

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: dict[str, Any] | None = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ==================== Broadcast Schemas ====================


class GlobalBroadcastRequest(BaseModel):
    """Request schema for global broadcast to all users."""

    message_type: WSMessageType = Field(
        default=WSMessageType.SYSTEM,
        description="Type of message to broadcast",
    )
    payload: dict[str, Any] = Field(..., description="Message payload")
    from_user: str | None = Field(
        default="system",
        description="Sender identifier (defaults to 'system')",
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class GlobalBroadcastResponse(BaseModel):
    """Response schema for global broadcast."""

    success: bool = Field(..., description="Whether broadcast was successful")
    message: str = Field(..., description="Status message")
    subscribers_reached: int = Field(
        ..., description="Number of Redis subscribers that received the message"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Broadcast timestamp")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
