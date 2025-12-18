# Architecture Documentation

## System Overview

The LQ Real-time Service is a distributed, stateless WebSocket and Webhook handling system designed for high scalability and fault tolerance.

## Design Principles

1. **Stateless**: No persistent state on application servers
2. **Horizontal Scalability**: Add instances without code changes
3. **Fault Tolerant**: Instance failures don't affect other instances
4. **Message Broker**: Redis Pub/Sub for cross-instance communication
5. **Security First**: JWT authentication and HMAC signature verification

---

## Component Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Browser    │  │   Mobile     │  │  External    │      │
│  │  WebSocket   │  │     App      │  │  Webhooks    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                     Load Balancer                             │
│               (Nginx / ALB / Cloud LB)                       │
└──────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ WS Instance  │   │ WS Instance  │   │ WS Instance  │
│      #1      │   │      #2      │   │      #N      │
│              │   │              │   │              │
│ ┌──────────┐ │   │ ┌──────────┐ │   │ ┌──────────┐ │
│ │Connection│ │   │ │Connection│ │   │ │Connection│ │
│ │ Manager  │ │   │ │ Manager  │ │   │ │ Manager  │ │
│ └──────────┘ │   │ └──────────┘ │   │ └──────────┘ │
│ ┌──────────┐ │   │ ┌──────────┐ │   │ ┌──────────┐ │
│ │ Webhook  │ │   │ │ Webhook  │ │   │ │ Webhook  │ │
│ │ Handler  │ │   │ │ Handler  │   │ │ Handler  │ │
│ └──────────┘ │   │ └──────────┘ │   │ └──────────┘ │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
            ┌───────────────────────────────┐
            │       Redis Pub/Sub           │
            │   (Message Broker & Cache)    │
            │                               │
            │  Channels:                    │
            │  - tenant:{tenant_id}         │
            │  - user:{user_id}             │
            └───────────────────────────────┘
```

---

## Data Flow

### WebSocket Connection Flow

```
1. Client connects with JWT token
   └─> ws://api.example.com/ws?token=<JWT>

2. Server validates JWT
   ├─> Decode token
   ├─> Verify signature
   ├─> Check expiration
   └─> Validate scope (ws:connect)

3. Accept WebSocket connection
   ├─> Generate connection_id
   ├─> Store connection in memory
   └─> Subscribe to Redis channel: tenant:{tenant_id}

4. Send welcome message to client

5. Listen for messages
   ├─> From client (WebSocket)
   └─> From Redis (other instances)

6. On disconnect
   ├─> Remove from connection pool
   └─> Unsubscribe from Redis channel
```

### Message Broadcasting Flow

```
Instance 1:
  Client sends message
    ↓
  Connection Manager receives message
    ↓
  Publish to Redis channel: tenant:{tenant_id}
    ↓
  Redis broadcasts to all subscribers

Instance 1, 2, 3:
  Redis listener receives message
    ↓
  Connection Manager broadcasts to local connections
    ↓
  All clients in tenant receive message
```

### Webhook Flow

```
1. External service sends webhook
   └─> POST /webhooks/{provider}

2. Server receives webhook
   ├─> Verify HMAC signature (if configured)
   ├─> Extract tenant_id
   └─> Parse payload

3. Process webhook (async background task)
   ├─> Create WebhookEvent
   ├─> Convert to WSMessage
   └─> Publish to Redis channel: tenant:{tenant_id}

4. All WebSocket instances receive message
   └─> Broadcast to connected clients

5. Return 200 OK to webhook sender
```

---

## Scalability Architecture

### Single Instance (1k - 10k connections)

```
┌─────────────────────────┐
│   Load Balancer (LB)    │
└────────────┬────────────┘
             │
        ┌────▼────┐
        │Instance │
        │  10k    │
        │  conn   │
        └────┬────┘
             │
        ┌────▼────┐
        │  Redis  │
        └─────────┘

Configuration:
- 2 CPU, 2GB RAM
- 10k max connections
- 1 Redis instance
```

### Multiple Instances (10k - 50k connections)

```
┌─────────────────────────┐
│   Load Balancer (LB)    │
└───┬──────┬──────┬───────┘
    │      │      │
┌───▼──┐┌──▼──┐┌──▼──┐
│Inst 1││Inst2││Inst3│
│ 10k  ││ 10k ││ 10k │
└───┬──┘└──┬──┘└──┬──┘
    │      │      │
    └──────┼──────┘
           │
      ┌────▼────┐
      │  Redis  │
      │Cluster  │
      └─────────┘

Configuration:
- 3-5 instances
- 2 CPU, 2GB RAM each
- Redis with persistence
```

### High Scale (50k - 100k+ connections)

```
┌────────────────────────────────┐
│   Global Load Balancer         │
└────┬──────────────────┬────────┘
     │                  │
┌────▼────────┐  ┌──────▼───────┐
│   Region 1  │  │   Region 2   │
│     ALB     │  │     ALB      │
└────┬────────┘  └──────┬───────┘
     │                  │
┌────▼────────────────────────┐
│ Auto-scaling Group (3-20)   │
│ Instances with 10k conn each│
└────┬────────────────────────┘
     │
┌────▼──────────────────┐
│  Redis Cluster        │
│  - Master + Replicas  │
│  - Persistence ON     │
│  - Sentinel/Cluster   │
└───────────────────────┘

Configuration:
- Auto-scaling: 3-20 instances
- 2 CPU, 4GB RAM per instance
- Redis Cluster (3 masters, 3 replicas)
```

---

## Connection Management

### In-Memory Data Structures

```python
# Connection Manager state
{
    # Active WebSocket connections
    "active_connections": {
        "conn-123": <WebSocket>,
        "conn-456": <WebSocket>,
    },

    # Connection metadata
    "connection_info": {
        "conn-123": {
            "user_id": "user-abc",
            "tenant_id": "tenant-xyz",
            "connected_at": "2025-01-01T00:00:00Z",
            "last_activity": "2025-01-01T00:05:00Z",
        },
    },

    # User to connections mapping
    "user_connections": {
        "user-abc": {"conn-123", "conn-789"},
    },

    # Tenant to connections mapping
    "tenant_connections": {
        "tenant-xyz": {"conn-123", "conn-456", "conn-789"},
    },

    # Subscribed Redis channels
    "subscribed_tenants": {"tenant-xyz", "tenant-abc"},
}
```

### Memory Estimation

Per connection overhead:
- WebSocket object: ~50 KB
- Connection info: ~1 KB
- Mappings: ~0.5 KB
- **Total: ~51.5 KB per connection**

For 10,000 connections:
- Memory: ~500 MB
- CPU: ~30-40% (message processing)
- Network: Depends on message rate

---

## Redis Channel Design

### Channel Naming Convention

```
tenant:{tenant_id}       - Broadcast to all users in tenant
user:{user_id}           - Send to specific user across instances
global:broadcast         - Send to all connected clients
system:events            - System-level events
```

### Message Format in Redis

```json
{
  "type": "message",
  "payload": {
    "text": "Hello, world!"
  },
  "timestamp": "2025-01-01T00:00:00Z",
  "from_user": "user-123",
  "message_id": "msg-abc-123"
}
```

---

## Security Architecture

### Authentication Flow

```
1. Client requests JWT from auth service
   └─> POST /auth/login
   └─> Response: {access_token: "eyJ..."}

2. Client connects to WebSocket with token
   └─> ws://api.example.com/ws?token=eyJ...

3. Server validates token
   ├─> Decode JWT
   ├─> Verify signature with JWT_SECRET_KEY
   ├─> Check expiration (exp claim)
   ├─> Verify scope (ws:connect)
   └─> Extract user_id and tenant_id

4. If valid: Accept connection
   If invalid: Close with 401 Unauthorized
```

### Webhook Security

```
1. External service sends webhook with signature
   └─> POST /webhooks/stripe
   └─> Headers:
       - x-signature: sha256=abc123...
       - x-tenant-id: tenant-xyz

2. Server verifies signature
   ├─> Get webhook secret for tenant
   ├─> Compute HMAC SHA256
   ├─> Compare signatures (constant-time)
   └─> Accept if valid

3. Process webhook if signature valid
   Otherwise: Return 401 Unauthorized
```

---

## Fault Tolerance

### Instance Failure Handling

```
Normal Operation:
┌────────┐ ┌────────┐ ┌────────┐
│Instance│ │Instance│ │Instance│
│   1    │ │   2    │ │   3    │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    └──────────┼──────────┘
               │
          ┌────▼────┐
          │  Redis  │
          └─────────┘

Instance 2 Fails:
┌────────┐  ✗✗✗✗✗  ┌────────┐
│Instance│           │Instance│
│   1    │           │   3    │
└───┬────┘           └───┬────┘
    │                    │
    └────────┬───────────┘
             │
        ┌────▼────┐
        │  Redis  │
        └─────────┘

Result:
- Connections on Instance 2: Disconnected
- Clients automatically reconnect to Instance 1 or 3
- No data loss (Redis persists messages)
```

### Redis Failure Handling

```
Redis Master Fails:
┌────────┐ ┌────────┐ ┌────────┐
│Instance│ │Instance│ │Instance│
│   1    │ │   2    │ │   3    │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    └──────────┼──────────┘
               │
          ┌────▼────┐
          │  Redis  │
          │ Sentinel│ ← Promotes replica to master
          └─────────┘

Auto-recovery:
1. Redis Sentinel detects master failure
2. Promotes replica to new master
3. Applications reconnect to new master
4. Service restored in < 30 seconds
```

---

## Performance Optimization

### Connection Pooling

```python
# Redis connection pool
redis_client = aioredis.from_url(
    redis_url,
    max_connections=200,  # Pool size
    encoding="utf-8",
)
```

### Message Batching (Future Enhancement)

```python
# Batch messages for efficiency
async def send_batch(messages: List[WSMessage]):
    """Send multiple messages in one operation."""
    serialized = [msg.json() for msg in messages]
    await websocket.send_text(json.dumps(serialized))
```

### Memory Management

```python
# Limit message history per connection
MAX_MESSAGE_HISTORY = 100

# Periodic cleanup of inactive connections
async def cleanup_inactive():
    """Remove connections inactive for > 1 hour."""
    cutoff = datetime.utcnow() - timedelta(hours=1)
    for conn_id, info in connection_info.items():
        if info.last_activity < cutoff:
            await disconnect(conn_id)
```

---

## Monitoring Points

### Application Metrics

```python
# Key metrics to track
- active_websocket_connections
- messages_sent_per_second
- messages_received_per_second
- redis_pubsub_lag
- connection_duration_avg
- authentication_failures
- webhook_processing_time
```

### Infrastructure Metrics

```
- CPU utilization per instance
- Memory usage per instance
- Network throughput (in/out)
- Redis memory usage
- Redis command latency
- Load balancer request count
```

---

## Design Trade-offs

### 1. Redis Pub/Sub vs Message Queue

**Chosen: Redis Pub/Sub**

Pros:
- Low latency (< 1ms)
- Simple setup
- Widely available

Cons:
- No message persistence (fire-and-forget)
- No delivery guarantees

Alternative: RabbitMQ/Kafka for guaranteed delivery

### 2. Stateless vs Stateful

**Chosen: Stateless**

Pros:
- Easy horizontal scaling
- No session affinity required
- Fault tolerant

Cons:
- Higher Redis load
- Slight latency overhead

### 3. Single Worker vs Multiple Workers

**Chosen: Single Worker per Instance**

Pros:
- Simple connection management
- No inter-worker communication
- Predictable scaling

Cons:
- Must scale by adding instances
- No multi-core utilization per instance

Solution: Run multiple single-worker containers

---

## Future Enhancements

1. **Message Persistence**: Add PostgreSQL for message history
2. **Presence System**: Track online/offline users
3. **Direct Messaging**: User-to-user private messages
4. **Rate Limiting**: Per-user message rate limits
5. **Analytics**: Real-time analytics dashboard
6. **Edge Deployment**: Deploy to edge locations (Cloudflare Workers, etc.)

---

For implementation details, see the codebase in [app/](app/) directory.
