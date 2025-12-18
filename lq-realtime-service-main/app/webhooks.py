"""
Webhook handler module.
Receives, validates, and processes webhooks from external providers.
"""

import asyncio
import logging
from datetime import datetime

from fastapi import BackgroundTasks, Header, HTTPException, Request, status

from app.auth import verify_webhook_signature
from app.config import get_settings
from app.redis_client import get_tenant_channel, redis_client
from app.schemas import (
    WebhookEvent,
    WebhookProvider,
    WebhookRegistration,
    WSMessage,
    WSMessageType,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class WebhookRegistry:
    """
    Registry for managing webhook configurations.
    In production, this should be backed by a database.
    """

    def __init__(self):
        # In-memory registry: {provider: {tenant_id: WebhookRegistration}}
        self._registrations: dict[str, dict[str, WebhookRegistration]] = {}
        self._processing_stats = {"total_processed": 0, "total_failed": 0}

    def register(self, registration: WebhookRegistration):
        """
        Register a webhook configuration.

        Args:
            registration: Webhook registration details
        """
        provider = registration.provider.value

        if provider not in self._registrations:
            self._registrations[provider] = {}

        self._registrations[provider][registration.tenant_id] = registration

        logger.info(f"Webhook registered: provider={provider}, tenant={registration.tenant_id}")

    def get_registration(
        self, provider: WebhookProvider, tenant_id: str
    ) -> WebhookRegistration | None:
        """
        Get webhook registration for a provider and tenant.

        Args:
            provider: Webhook provider
            tenant_id: Tenant ID

        Returns:
            WebhookRegistration if found, None otherwise
        """
        provider_key = provider.value
        return self._registrations.get(provider_key, {}).get(tenant_id)

    def get_stats(self) -> dict:
        """Get webhook processing statistics."""
        return {
            "registered_webhooks": sum(len(tenants) for tenants in self._registrations.values()),
            **self._processing_stats,
        }

    def increment_processed(self):
        """Increment processed webhook counter."""
        self._processing_stats["total_processed"] += 1

    def increment_failed(self):
        """Increment failed webhook counter."""
        self._processing_stats["total_failed"] += 1


# Global webhook registry
webhook_registry = WebhookRegistry()


class WebhookProcessor:
    """Processes incoming webhooks and publishes events."""

    def __init__(self):
        self.retry_queue: asyncio.Queue = asyncio.Queue()

    async def process_webhook(
        self,
        provider: WebhookProvider,
        event_type: str,
        payload: dict,
        signature: str | None = None,
        tenant_id: str | None = None,
    ):
        """
        Process incoming webhook event.

        Args:
            provider: Webhook provider
            event_type: Event type from provider
            payload: Event payload
            signature: Webhook signature for verification
            tenant_id: Optional tenant ID (can be extracted from payload)
        """
        try:
            # Create webhook event
            webhook_event = WebhookEvent(
                provider=provider,
                event_type=event_type,
                payload=payload,
                signature=signature,
                tenant_id=tenant_id,
            )

            # Extract tenant_id from payload if not provided
            if not tenant_id:
                tenant_id = self._extract_tenant_id(provider, payload)
                webhook_event.tenant_id = tenant_id

            if not tenant_id:
                logger.warning(f"Cannot determine tenant_id for webhook: {provider.value}")
                webhook_registry.increment_failed()
                return

            # Convert webhook to WebSocket message
            ws_message = self._webhook_to_ws_message(webhook_event)

            # Publish to tenant channel
            channel = get_tenant_channel(tenant_id)
            await redis_client.publish(channel, ws_message.model_dump())

            # Update statistics
            webhook_registry.increment_processed()

            logger.info(
                f"Webhook processed: provider={provider.value}, "
                f"event={event_type}, tenant={tenant_id}"
            )

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            webhook_registry.increment_failed()
            raise

    def _extract_tenant_id(self, provider: WebhookProvider, payload: dict) -> str | None:
        """
        Extract tenant_id from webhook payload.
        Provider-specific logic.

        Args:
            provider: Webhook provider
            payload: Webhook payload

        Returns:
            Tenant ID if found, None otherwise
        """
        # Provider-specific extraction logic
        extractors = {
            WebhookProvider.STRIPE: lambda p: p.get("account"),
            WebhookProvider.GITHUB: lambda p: p.get("organization", {}).get("id"),
            WebhookProvider.SLACK: lambda p: p.get("team_id"),
            WebhookProvider.TWILIO: lambda p: p.get("AccountSid"),
            WebhookProvider.SENDGRID: lambda p: p.get("tenant_id"),  # Custom field
            WebhookProvider.CUSTOM: lambda p: p.get("tenant_id"),
        }

        extractor = extractors.get(provider)
        if extractor:
            tenant_id = extractor(payload)
            if tenant_id:
                return str(tenant_id)

        # Fallback: look for common tenant identifier fields
        for field in ["tenant_id", "organization_id", "account_id", "team_id"]:
            if field in payload:
                return str(payload[field])

        return None

    def _webhook_to_ws_message(self, webhook_event: WebhookEvent) -> WSMessage:
        """
        Convert webhook event to WebSocket message.

        Args:
            webhook_event: Webhook event

        Returns:
            WebSocket message
        """
        return WSMessage(
            type=WSMessageType.NOTIFICATION,
            payload={
                "source": "webhook",
                "provider": webhook_event.provider.value,
                "event_type": webhook_event.event_type,
                "event_id": webhook_event.event_id,
                "data": webhook_event.payload,
                "received_at": webhook_event.received_at.isoformat(),
            },
            timestamp=webhook_event.received_at,
        )


# Global webhook processor
webhook_processor = WebhookProcessor()


async def handle_webhook(
    provider: WebhookProvider,
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: str | None = Header(None, alias="x-signature"),
    x_tenant_id: str | None = Header(None, alias="x-tenant-id"),
):
    """
    Generic webhook handler endpoint.

    Args:
        provider: Webhook provider from path parameter
        request: FastAPI request object
        background_tasks: FastAPI background tasks
        x_signature: Webhook signature header
        x_tenant_id: Optional tenant ID header

    Returns:
        Success response

    Raises:
        HTTPException: If validation fails
    """
    try:
        # Read raw body
        body = await request.body()

        # Parse JSON payload
        try:
            payload = await request.json()
        except Exception as e:
            logger.error(f"Invalid JSON payload: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload",
            ) from e

        # Extract tenant_id (from header or payload)
        tenant_id = x_tenant_id or webhook_processor._extract_tenant_id(provider, payload)

        # Verify signature if provided and registration exists
        if tenant_id:
            registration = webhook_registry.get_registration(provider, tenant_id)

            if registration and registration.enabled:
                if x_signature and registration.secret:
                    # Verify signature
                    try:
                        await verify_webhook_signature(body, x_signature, registration.secret)
                    except Exception as e:
                        logger.warning(f"Webhook signature verification failed: {e}")
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid webhook signature",
                        ) from e
            elif not registration:
                logger.warning(f"No webhook registration found for {provider.value}/{tenant_id}")

        # Extract event type (provider-specific)
        event_type = _extract_event_type(provider, payload)

        # Process webhook asynchronously
        background_tasks.add_task(
            webhook_processor.process_webhook,
            provider=provider,
            event_type=event_type,
            payload=payload,
            signature=x_signature,
            tenant_id=tenant_id,
        )

        return {
            "status": "accepted",
            "provider": provider.value,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook handler error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


def _extract_event_type(provider: WebhookProvider, payload: dict) -> str:
    """
    Extract event type from webhook payload.
    Provider-specific logic.

    Args:
        provider: Webhook provider
        payload: Webhook payload

    Returns:
        Event type string
    """
    # Provider-specific event type extraction
    event_type_fields = {
        WebhookProvider.STRIPE: "type",
        WebhookProvider.GITHUB: "action",
        WebhookProvider.SLACK: "type",
        WebhookProvider.TWILIO: "MessageStatus",
        WebhookProvider.SENDGRID: "event",
        WebhookProvider.CUSTOM: "event_type",
    }

    field = event_type_fields.get(provider, "type")
    return payload.get(field, "unknown")


# Convenience function to register webhooks programmatically
def register_webhook(
    provider: WebhookProvider,
    tenant_id: str,
    secret: str,
    enabled: bool = True,
    retry_policy: dict | None = None,
) -> WebhookRegistration:
    """
    Register a new webhook configuration.

    Args:
        provider: Webhook provider
        tenant_id: Tenant ID
        secret: Webhook signing secret
        enabled: Whether webhook is active
        retry_policy: Optional retry policy configuration

    Returns:
        WebhookRegistration instance
    """
    registration = WebhookRegistration(
        provider=provider,
        tenant_id=tenant_id,
        secret=secret,
        enabled=enabled,
        retry_policy=retry_policy
        or {
            "max_retries": settings.webhook_max_retries,
            "retry_delay": settings.webhook_retry_delay,
        },
    )

    webhook_registry.register(registration)
    return registration
