"""
WebSocket connection handler module.
Manages WebSocket connections, message routing, and pub/sub integration.
"""

import logging
import uuid
from datetime import datetime

import orjson
from fastapi import WebSocket, WebSocketDisconnect

from app.auth import verify_websocket_token
from app.config import get_settings
from app.redis_client import get_global_channel, get_tenant_channel, redis_client
from app.schemas import TokenPayload, WSConnectionInfo, WSMessage, WSMessageType

logger = logging.getLogger(__name__)
settings = get_settings()


class ConnectionManager:
    """
    Manages active WebSocket connections for this server instance.
    Integrates with Redis Pub/Sub for cross-instance messaging.
    """

    def __init__(self):
        # Active connections: {connection_id: WebSocket}
        self.active_connections: dict[str, WebSocket] = {}

        # Connection metadata: {connection_id: WSConnectionInfo}
        self.connection_info: dict[str, WSConnectionInfo] = {}

        # User to connections mapping: {user_id: {connection_id1, connection_id2, ...}}
        self.user_connections: dict[str, set] = {}

        # Tenant to connections mapping: {tenant_id: {connection_id1, connection_id2, ...}}
        self.tenant_connections: dict[str, set] = {}

        # Subscribed tenant channels
        self.subscribed_tenants: set = set()

        # Global channel subscription flag
        self.global_channel_subscribed: bool = False

        # Statistics
        self.total_messages_sent = 0
        self.total_messages_received = 0

    async def connect(self, websocket: WebSocket, token: str) -> tuple[str, TokenPayload]:
        """
        Authenticate and register a new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance
            token: JWT token from query parameters

        Returns:
            Tuple of (connection_id, token_payload)

        Raises:
            HTTPException: If authentication fails
        """
        # Verify token
        token_payload = await verify_websocket_token(token)

        # Check connection limit
        if len(self.active_connections) >= settings.ws_max_connections_per_instance:
            logger.warning("Max connections reached, rejecting new connection")
            await websocket.close(code=1008, reason="Server at capacity")
            raise Exception("Max connections reached")

        # Accept WebSocket connection
        await websocket.accept()

        # Generate connection ID
        connection_id = str(uuid.uuid4())

        # Store connection
        self.active_connections[connection_id] = websocket

        # Store connection info
        now = datetime.utcnow()
        self.connection_info[connection_id] = WSConnectionInfo(
            user_id=token_payload.sub,
            tenant_id=token_payload.tenant_id,
            connection_id=connection_id,
            connected_at=now,
            last_activity=now,
            metadata=token_payload.metadata or {},
        )

        # Update user connections
        if token_payload.sub not in self.user_connections:
            self.user_connections[token_payload.sub] = set()
        self.user_connections[token_payload.sub].add(connection_id)

        # Update tenant connections
        if token_payload.tenant_id not in self.tenant_connections:
            self.tenant_connections[token_payload.tenant_id] = set()
        self.tenant_connections[token_payload.tenant_id].add(connection_id)

        # Subscribe to tenant channel if not already subscribed
        await self._subscribe_to_tenant(token_payload.tenant_id)

        # Subscribe to global channel if not already subscribed
        await self._subscribe_to_global_channel()

        logger.info(
            f"WebSocket connected: connection_id={connection_id}, "
            f"user={token_payload.sub}, tenant={token_payload.tenant_id}, "
            f"total_connections={len(self.active_connections)}"
        )

        return connection_id, token_payload

    async def disconnect(self, connection_id: str):
        """
        Disconnect and cleanup a WebSocket connection.

        Args:
            connection_id: Connection identifier
        """
        conn_info = self.connection_info.get(connection_id)
        if not conn_info:
            logger.warning(f"Connection {connection_id} not found")
            return

        # Remove from active connections
        websocket = self.active_connections.pop(connection_id, None)
        if websocket:
            try:
                await websocket.close()
            except Exception as e:
                logger.debug(f"Error closing websocket: {e}")

        # Remove from connection info
        self.connection_info.pop(connection_id, None)

        # Remove from user connections
        user_id = conn_info.user_id
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Remove from tenant connections
        tenant_id = conn_info.tenant_id
        if tenant_id in self.tenant_connections:
            self.tenant_connections[tenant_id].discard(connection_id)
            if not self.tenant_connections[tenant_id]:
                del self.tenant_connections[tenant_id]
                # Unsubscribe from tenant channel if no more connections
                await self._unsubscribe_from_tenant(tenant_id)

        logger.info(
            f"WebSocket disconnected: connection_id={connection_id}, "
            f"user={user_id}, tenant={tenant_id}, "
            f"total_connections={len(self.active_connections)}"
        )

    async def send_message(self, connection_id: str, message: WSMessage):
        """
        Send message to a specific connection.

        Args:
            connection_id: Target connection ID
            message: Message to send
        """
        websocket = self.active_connections.get(connection_id)
        if not websocket:
            logger.warning(f"Connection {connection_id} not found")
            return

        try:
            # Serialize message
            message_json = orjson.dumps(message.model_dump()).decode()

            # Send to WebSocket
            await websocket.send_text(message_json)

            # Update statistics
            self.total_messages_sent += 1

            # Update last activity
            if connection_id in self.connection_info:
                self.connection_info[connection_id].last_activity = datetime.utcnow()

        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            await self.disconnect(connection_id)

    async def broadcast_to_tenant(self, tenant_id: str, message: WSMessage):
        """
        Broadcast message to all connections in a tenant.
        Uses Redis Pub/Sub to reach connections on other instances.

        Args:
            tenant_id: Target tenant ID
            message: Message to broadcast
        """
        # Publish to Redis channel for cross-instance fanout
        channel = get_tenant_channel(tenant_id)
        message_dict = message.model_dump()

        await redis_client.publish(channel, message_dict)

    async def broadcast_to_user(self, user_id: str, message: WSMessage):
        """
        Broadcast message to all connections of a specific user.

        Args:
            user_id: Target user ID
            message: Message to send
        """
        connection_ids = self.user_connections.get(user_id, set())

        for connection_id in list(connection_ids):
            await self.send_message(connection_id, message)

    async def broadcast_global(self, message: WSMessage) -> int:
        """
        Broadcast message to ALL connected users across all tenants.
        Uses Redis Pub/Sub to reach connections on other instances.
        This is a system-level operation used for admin announcements.

        Args:
            message: Message to broadcast globally

        Returns:
            Number of Redis subscribers that received the message
        """
        # Publish to Redis global channel for cross-instance fanout
        channel = get_global_channel()
        message_dict = message.model_dump()

        subscribers = await redis_client.publish(channel, message_dict)
        return subscribers

    async def _subscribe_to_tenant(self, tenant_id: str):
        """
        Subscribe to Redis pub/sub channel for a tenant.

        Args:
            tenant_id: Tenant ID to subscribe to
        """
        if tenant_id in self.subscribed_tenants:
            return

        channel = get_tenant_channel(tenant_id)
        await redis_client.subscribe(channel, self._handle_redis_message)
        self.subscribed_tenants.add(tenant_id)

        logger.info(f"Subscribed to tenant channel: {channel}")

    async def _unsubscribe_from_tenant(self, tenant_id: str):
        """
        Unsubscribe from Redis pub/sub channel for a tenant.

        Args:
            tenant_id: Tenant ID to unsubscribe from
        """
        if tenant_id not in self.subscribed_tenants:
            return

        channel = get_tenant_channel(tenant_id)
        await redis_client.unsubscribe(channel)
        self.subscribed_tenants.discard(tenant_id)

        logger.info(f"Unsubscribed from tenant channel: {channel}")

    async def _subscribe_to_global_channel(self):
        """
        Subscribe to global Redis pub/sub channel for system-wide broadcasts.
        This channel is used by admins to send messages to all users.
        """
        if self.global_channel_subscribed:
            return

        channel = get_global_channel()
        await redis_client.subscribe(channel, self._handle_global_message)
        self.global_channel_subscribed = True

        logger.info(f"Subscribed to global broadcast channel: {channel}")

    async def _handle_redis_message(self, channel: str, message: dict):
        """
        Handle incoming message from Redis pub/sub.

        Args:
            channel: Redis channel name
            message: Message dictionary
        """
        try:
            # Parse message
            ws_message = WSMessage(**message)

            # Extract tenant_id from channel (format: "tenant:{tenant_id}")
            tenant_id = channel.split(":", 1)[1] if ":" in channel else None

            if not tenant_id:
                logger.warning(f"Invalid channel format: {channel}")
                return

            # Send to all local connections for this tenant
            connection_ids = self.tenant_connections.get(tenant_id, set())

            for connection_id in list(connection_ids):
                await self.send_message(connection_id, ws_message)

            logger.debug(
                f"Broadcasted Redis message to {len(connection_ids)} local connections "
                f"for tenant {tenant_id}"
            )

        except Exception as e:
            logger.error(f"Error handling Redis message from {channel}: {e}")

    async def _handle_global_message(self, channel: str, message: dict):
        """
        Handle incoming global broadcast message from Redis pub/sub.
        Sends message to ALL local connections regardless of tenant.

        Args:
            channel: Redis channel name (should be "global:broadcast")
            message: Message dictionary
        """
        try:
            # Parse message
            ws_message = WSMessage(**message)

            # Send to all local connections
            connection_ids = list(self.active_connections.keys())

            for connection_id in connection_ids:
                await self.send_message(connection_id, ws_message)

            logger.info(f"Broadcasted global message to {len(connection_ids)} local connections")

        except Exception as e:
            logger.error(f"Error handling global message from {channel}: {e}")

    async def handle_client_message(self, connection_id: str, message_text: str):
        """
        Process incoming message from WebSocket client.

        Args:
            connection_id: Source connection ID
            message_text: Raw message text from client
        """
        try:
            # Parse message
            message_data = orjson.loads(message_text)
            ws_message = WSMessage(**message_data)

            # Update statistics
            self.total_messages_received += 1

            # Update last activity
            if connection_id in self.connection_info:
                self.connection_info[connection_id].last_activity = datetime.utcnow()

            # Handle different message types
            if ws_message.type == WSMessageType.PING:
                # Respond with pong
                pong_message = WSMessage(
                    type=WSMessageType.PONG,
                    payload={"timestamp": datetime.utcnow().isoformat()},
                )
                await self.send_message(connection_id, pong_message)

            elif ws_message.type == WSMessageType.MESSAGE:
                # Handle regular message
                conn_info = self.connection_info.get(connection_id)
                if conn_info:
                    ws_message.from_user = conn_info.user_id
                    # Broadcast to tenant
                    await self.broadcast_to_tenant(conn_info.tenant_id, ws_message)

            elif ws_message.type == WSMessageType.BROADCAST:
                # Broadcast to entire tenant
                conn_info = self.connection_info.get(connection_id)
                if conn_info:
                    ws_message.from_user = conn_info.user_id
                    await self.broadcast_to_tenant(conn_info.tenant_id, ws_message)

            else:
                logger.warning(f"Unknown message type: {ws_message.type}")

        except Exception as e:
            logger.error(f"Error handling client message from {connection_id}: {e}")
            error_message = WSMessage(
                type=WSMessageType.ERROR,
                payload={"error": "Invalid message format", "detail": str(e)},
            )
            await self.send_message(connection_id, error_message)

    def get_stats(self) -> dict:
        """
        Get current connection statistics.

        Returns:
            Dictionary with connection stats
        """
        return {
            "active_connections": len(self.active_connections),
            "unique_users": len(self.user_connections),
            "unique_tenants": len(self.tenant_connections),
            "subscribed_channels": len(self.subscribed_tenants),
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
        }


# Global connection manager instance
connection_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    Main WebSocket endpoint handler.

    Args:
        websocket: FastAPI WebSocket connection
        token: JWT authentication token
    """
    connection_id = None

    try:
        # Authenticate and connect
        connection_id, token_payload = await connection_manager.connect(websocket, token)

        # Send welcome message
        welcome_message = WSMessage(
            type=WSMessageType.SYSTEM,
            payload={
                "message": "Connected successfully",
                "connection_id": connection_id,
                "user_id": token_payload.sub,
                "tenant_id": token_payload.tenant_id,
            },
        )
        await connection_manager.send_message(connection_id, welcome_message)

        # Message handling loop
        while True:
            try:
                # Receive message from client
                message_text = await websocket.receive_text()

                # Process message
                await connection_manager.handle_client_message(connection_id, message_text)

            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected: {connection_id}")
                break

    except Exception as e:
        logger.error(f"WebSocket error for connection {connection_id}: {e}")

    finally:
        # Cleanup connection
        if connection_id:
            await connection_manager.disconnect(connection_id)
