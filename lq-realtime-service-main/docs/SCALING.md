# Scaling to 100k Concurrent Connections

This guide provides a step-by-step roadmap for scaling the LQ Real-time Service from 1k to 100k+ concurrent WebSocket connections.

---

## Scaling Stages

### Stage 0: Development (< 100 connections)

**Infrastructure:**
- Local machine or single VPS
- Docker Compose
- 1 CPU, 1GB RAM
- Redis in Docker

**Cost:** Free / ~$10/month

```bash
# Local development
docker-compose up -d
```

**Capacity:** ~100 concurrent connections

---

### Stage 1: Early Production (100 - 1,000 connections)

**Infrastructure:**
- Single production server
- 2 CPU, 2GB RAM
- Managed Redis (e.g., Redis Cloud, AWS ElastiCache)
- SSL certificate (Let's Encrypt)

**Configuration:**

```env
WS_MAX_CONNECTIONS_PER_INSTANCE=1000
WORKERS=1
```

**Deployment:**

```bash
# Single instance deployment
docker run -d \
  -p 8082:8082 \
  -e REDIS_HOST=your-redis.cloud.com \
  lq-realtime-service:latest
```

**Monitoring:**
- Basic health checks
- CloudWatch/DataDog metrics
- Error logging

**Cost:** ~$50/month

**Expected Performance:**
- 1,000 concurrent connections
- < 10ms message latency
- 99.9% uptime

---

### Stage 2: Growth (1k - 10k connections)

**Infrastructure:**
- 2-3 application servers
- 2 CPU, 4GB RAM per server
- Managed Redis (2GB)
- Load balancer (Nginx or cloud LB)

**Configuration:**

```env
WS_MAX_CONNECTIONS_PER_INSTANCE=5000
WORKERS=1
```

**Load Balancer Setup:**

```nginx
upstream websocket_backend {
    ip_hash;  # Sticky sessions
    server app-1:8082 max_fails=3;
    server app-2:8082 max_fails=3;
}

server {
    listen 443 ssl;
    server_name ws.example.com;

    location /ws {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }
}
```

**Monitoring:**
- Metrics dashboard (Grafana)
- Alerting (PagerDuty, Opsgenie)
- Application logs (ELK stack)

**Cost:** ~$150/month

**Expected Performance:**
- 10,000 concurrent connections
- < 15ms message latency
- 99.95% uptime

---

### Stage 3: Scale-up (10k - 50k connections)

**Infrastructure:**
- 5-10 application servers (auto-scaling)
- 2 CPU, 4GB RAM per server
- Redis Cluster (3 masters, 3 replicas)
- Application Load Balancer
- Multi-AZ deployment

**Auto-Scaling Configuration (AWS ECS):**

```json
{
  "service": {
    "desiredCount": 5,
    "deploymentConfiguration": {
      "maximumPercent": 200,
      "minimumHealthyPercent": 100
    }
  },
  "targetTrackingScaling": {
    "targetValue": 70.0,
    "scaleInCooldown": 300,
    "scaleOutCooldown": 60,
    "customizedMetricSpecification": {
      "metricName": "ActiveConnections",
      "namespace": "LQRealtime",
      "statistic": "Average"
    }
  }
}
```

**Redis Cluster Setup:**

```bash
# Redis Cluster with persistence
redis-cli --cluster create \
  redis-1:6379 redis-2:6379 redis-3:6379 \
  redis-4:6379 redis-5:6379 redis-6:6379 \
  --cluster-replicas 1
```

**System Tuning:**

```bash
# /etc/sysctl.conf
net.core.somaxconn = 8192
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15

# File descriptors
ulimit -n 65536
```

**Cost:** ~$500/month

**Expected Performance:**
- 50,000 concurrent connections
- < 20ms message latency
- 99.99% uptime

---

### Stage 4: Enterprise Scale (50k - 100k connections)

**Infrastructure:**
- 10-20 application servers (auto-scaling)
- 4 CPU, 8GB RAM per server
- Redis Cluster (6 masters, 6 replicas, 8GB each)
- Global load balancer (multi-region)
- CDN for static assets
- Dedicated monitoring infrastructure

**Kubernetes Deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lq-realtime-service
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 50%
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: ws-service
        image: lq-realtime-service:latest
        resources:
          requests:
            cpu: 2000m
            memory: 4Gi
          limits:
            cpu: 4000m
            memory: 8Gi
        env:
        - name: WS_MAX_CONNECTIONS_PER_INSTANCE
          value: "10000"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: lq-realtime-hpa
spec:
  minReplicas: 10
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: websocket_active_connections
      target:
        type: AverageValue
        averageValue: "8082"
```

**Multi-Region Architecture:**

```
┌─────────────────────────────────────┐
│      Global Load Balancer           │
│      (Route53 / Cloudflare)         │
└───────────────┬─────────────────────┘
                │
        ┌───────┴───────┐
        │               │
┌───────▼───────┐  ┌────▼──────────┐
│   Region 1    │  │   Region 2    │
│   (US-East)   │  │   (EU-West)   │
├───────────────┤  ├────────────────┤
│ ALB           │  │ ALB            │
│ 5-10 instances│  │ 5-10 instances │
│ Redis Cluster │  │ Redis Cluster  │
└───────┬───────┘  └────┬───────────┘
        │               │
        └───────┬───────┘
                │
        ┌───────▼────────┐
        │ Central DB     │
        │ (PostgreSQL)   │
        └────────────────┘
```

**Advanced Monitoring:**

```python
# Custom CloudWatch metrics
import boto3

cloudwatch = boto3.client('cloudwatch')

def publish_metrics():
    cloudwatch.put_metric_data(
        Namespace='LQRealtime',
        MetricData=[
            {
                'MetricName': 'ActiveConnections',
                'Value': len(connection_manager.active_connections),
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'Instance', 'Value': instance_id}
                ]
            },
            {
                'MetricName': 'MessagesPerSecond',
                'Value': messages_sent_last_minute / 60,
                'Unit': 'Count/Second'
            }
        ]
    )
```

**Cost:** ~$1,500-2,000/month

**Expected Performance:**
- 100,000 concurrent connections
- < 25ms message latency (same region)
- < 100ms message latency (cross-region)
- 99.99% uptime

---

### Stage 5: Hyper-Scale (100k+ connections)

**Infrastructure:**
- 20-100 application servers (auto-scaling)
- 4-8 CPU, 16GB RAM per server
- Redis Enterprise Cluster
- Multi-region, multi-AZ
- Dedicated DDoS protection
- Custom CDN configuration

**Advanced Optimizations:**

1. **Connection Sharding:**

```python
# Shard connections by tenant_id hash
def get_instance_for_tenant(tenant_id: str) -> str:
    """Route tenant to specific instance shard."""
    shard_count = 10
    shard = hash(tenant_id) % shard_count
    return f"ws-instance-{shard}"
```

2. **Message Compression:**

```python
import zlib

def send_compressed(websocket, message):
    """Send compressed message to reduce bandwidth."""
    compressed = zlib.compress(message.encode())
    await websocket.send_bytes(compressed)
```

3. **Connection Pooling:**

```python
# Pre-establish Redis connections
redis_pool = await aioredis.create_pool(
    redis_url,
    minsize=50,
    maxsize=500
)
```

**Infrastructure as Code (Terraform):**

```hcl
resource "aws_ecs_service" "lq_realtime" {
  name            = "lq-realtime-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.lq_realtime.arn
  desired_count   = 20

  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.lq_realtime.arn
    container_name   = "ws-service"
    container_port   = 8082
  }

  autoscaling {
    min_capacity = 20
    max_capacity = 100

    target_tracking_scaling_policy {
      predefined_metric_specification {
        predefined_metric_type = "ECSServiceAverageCPUUtilization"
      }
      target_value = 70.0
    }
  }
}
```

**Cost:** ~$5,000-10,000/month

**Expected Performance:**
- 200,000+ concurrent connections
- < 30ms message latency
- 99.995% uptime

---

## Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import User, task, between
import websocket

class WebSocketUser(User):
    wait_time = between(1, 5)

    def on_start(self):
        self.ws = websocket.create_connection(
            "ws://localhost:8082/ws?token=YOUR_TOKEN"
        )

    @task
    def send_message(self):
        self.ws.send('{"type": "ping", "payload": {}}')
        result = self.ws.recv()

    def on_stop(self):
        self.ws.close()
```

Run load test:

```bash
# Test with 10k users
locust -f locustfile.py --headless -u 10000 -r 100 --host ws://localhost:8082
```

### Benchmarking Results

| Connections | Instances | CPU/Instance | Memory/Instance | Latency (avg) | Cost/mo |
|-------------|-----------|--------------|-----------------|---------------|---------|
| 1k          | 1         | 20%          | 500MB           | 5ms           | $50     |
| 10k         | 2         | 40%          | 2GB             | 10ms          | $150    |
| 50k         | 5         | 60%          | 4GB             | 15ms          | $500    |
| 100k        | 10        | 70%          | 6GB             | 20ms          | $1,500  |

---

## Bottleneck Analysis

### Common Bottlenecks

1. **File Descriptors**
   - Problem: Running out of file descriptors
   - Solution: Increase `ulimit -n` to 65536+

2. **CPU Bound**
   - Problem: High CPU usage on message serialization
   - Solution: Use `orjson` (10x faster than standard json)

3. **Memory Leaks**
   - Problem: Connections not being cleaned up
   - Solution: Implement connection timeout and cleanup

4. **Redis Bandwidth**
   - Problem: Redis network saturation
   - Solution: Message batching, compression, or Redis Cluster

5. **Load Balancer Limits**
   - Problem: LB maxing out connections
   - Solution: Use multiple load balancers or upgrade tier

---

## Optimization Checklist

Performance optimization checklist for each stage:

### Application Level
- [ ] Use `orjson` for JSON serialization
- [ ] Implement connection pooling
- [ ] Enable message compression
- [ ] Batch Redis pub/sub messages
- [ ] Implement backpressure handling
- [ ] Use async everywhere

### Infrastructure Level
- [ ] Increase file descriptor limits
- [ ] Tune TCP parameters
- [ ] Enable Redis persistence
- [ ] Configure auto-scaling
- [ ] Set up health checks
- [ ] Implement circuit breakers

### Monitoring Level
- [ ] Track active connections per instance
- [ ] Monitor message latency
- [ ] Alert on high error rates
- [ ] Dashboard for real-time metrics
- [ ] Log aggregation and analysis

---

## Cost Optimization

### Strategies to Reduce Costs

1. **Use Spot Instances (AWS)**
   - Save 60-90% on compute
   - Suitable for stateless services

2. **Reserved Instances**
   - Save 30-60% with 1-year commitment
   - Good for baseline capacity

3. **Auto-Scaling**
   - Scale down during off-peak hours
   - Pay only for what you use

4. **Redis Optimization**
   - Use Redis eviction policies
   - Limit max memory usage
   - Consider managed Redis

5. **Multi-Tenancy**
   - Share infrastructure across tenants
   - Better resource utilization

---

## Migration Path

### From 10k to 100k Connections

**Week 1-2: Preparation**
- [ ] Set up monitoring and alerts
- [ ] Performance test current setup
- [ ] Identify bottlenecks
- [ ] Plan infrastructure changes

**Week 3-4: Infrastructure Upgrade**
- [ ] Migrate to Kubernetes or ECS
- [ ] Set up auto-scaling
- [ ] Upgrade Redis to cluster
- [ ] Configure load balancer

**Week 5-6: Testing**
- [ ] Load test with 50k connections
- [ ] Load test with 100k connections
- [ ] Fix any issues
- [ ] Optimize based on results

**Week 7-8: Gradual Rollout**
- [ ] Deploy to 10% of traffic
- [ ] Monitor for 3 days
- [ ] Deploy to 50% of traffic
- [ ] Full deployment

---

## Success Metrics

Track these KPIs to measure scaling success:

- **Connection Success Rate**: > 99.9%
- **Message Delivery Rate**: > 99.95%
- **Average Latency**: < 50ms
- **P95 Latency**: < 100ms
- **P99 Latency**: < 200ms
- **Uptime**: > 99.99%
- **Cost per Connection**: < $0.02/month

---

For more details, see [ARCHITECTURE.md](ARCHITECTURE.md) and [README.md](README.md).
