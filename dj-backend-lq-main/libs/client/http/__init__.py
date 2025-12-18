"""
HTTP client library for LingoQuesto services.

Provides HTTP clients and models for interacting with LingoQuesto services.
"""

from .base import AsyncHTTPClient, HTTPClient, HttpClientConfig
from .realtime_client import RealtimeClient, RealtimeClientConfig
from .realtime_models import (
    DebugConnectionsResponse,
    DebugConnectionsStats,
    ErrorDetail,
    ErrorResponse,
    GlobalBroadcastRequest,
    HealthCheckResponse,
    HealthStatus,
    MetricsResponse,
    PingMessage,
    PongMessage,
    RoomSubscriptionResponse,
    RootResponse,
    SendMessageRequest,
    SendMessageResponse,
    SubscribeRequest,
    TokenPayload,
    UnsubscribeRequest,
    WebhookResponse,
    WSConnectionInfo,
    WSMessage,
    WSMessageType,
)

__all__ = [
    # Base HTTP clients
    "AsyncHTTPClient",
    "HTTPClient",
    "HttpClientConfig",
    # Realtime client
    "RealtimeClient",
    "RealtimeClientConfig",
    # Request models
    "GlobalBroadcastRequest",
    "SendMessageRequest",
    "SubscribeRequest",
    "UnsubscribeRequest",
    # Response models
    "RootResponse",
    "HealthCheckResponse",
    "MetricsResponse",
    "SendMessageResponse",
    "WebhookResponse",
    "DebugConnectionsResponse",
    "DebugConnectionsStats",
    "ErrorResponse",
    "ErrorDetail",
    "RoomSubscriptionResponse",
    # Data models
    "TokenPayload",
    "WSMessage",
    "WSConnectionInfo",
    "PingMessage",
    "PongMessage",
    # Enums
    "WSMessageType",
    "HealthStatus",
]
