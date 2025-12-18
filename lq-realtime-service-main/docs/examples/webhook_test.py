#!/usr/bin/env python3
"""
Test webhook endpoint with signature verification.

Usage:
    python webhook_test.py --provider stripe --tenant-id TENANT_ID
"""

import argparse
import hashlib
import hmac
import json

import httpx


def send_webhook(
    provider: str,
    tenant_id: str,
    payload: dict,
    secret: str | None = None,
    base_url: str = "http://localhost:8082",
):
    """Send a test webhook request."""

    url = f"{base_url}/webhooks/{provider}"

    # Serialize payload
    payload_bytes = json.dumps(payload).encode()

    # Generate signature if secret provided
    headers = {"x-tenant-id": tenant_id}

    if secret:
        signature = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
        headers["x-signature"] = f"sha256={signature}"

    # Send request
    response = httpx.post(url, json=payload, headers=headers)

    return response


def main():
    parser = argparse.ArgumentParser(description="Test webhook endpoint")
    parser.add_argument(
        "--provider",
        required=True,
        choices=["stripe", "github", "slack", "twilio", "sendgrid", "custom"],
        help="Webhook provider",
    )
    parser.add_argument("--tenant-id", required=True, help="Tenant ID")
    parser.add_argument("--secret", help="Webhook signing secret (optional)")
    parser.add_argument("--url", default="http://localhost:8082", help="Base URL")

    args = parser.parse_args()

    # Sample payloads for different providers
    sample_payloads = {
        "stripe": {
            "type": "charge.succeeded",
            "data": {
                "object": {
                    "id": "ch_test_123",
                    "amount": 1000,
                    "currency": "usd",
                }
            },
        },
        "github": {
            "action": "opened",
            "pull_request": {
                "id": 123,
                "title": "Test PR",
            },
        },
        "slack": {
            "type": "message",
            "event": {
                "type": "message",
                "text": "Hello from Slack",
            },
        },
        "custom": {
            "event_type": "test.event",
            "data": {
                "message": "Test webhook event",
            },
        },
    }

    payload = sample_payloads.get(args.provider, sample_payloads["custom"])
    payload["tenant_id"] = args.tenant_id

    print("=" * 80)
    print(f"Sending Webhook: {args.provider}")
    print("=" * 80)
    print(f"Tenant ID: {args.tenant_id}")
    print(f"URL: {args.url}/webhooks/{args.provider}")
    print(f"Payload:\n{json.dumps(payload, indent=2)}")
    print("=" * 80)

    try:
        response = send_webhook(
            provider=args.provider,
            tenant_id=args.tenant_id,
            payload=payload,
            secret=args.secret,
            base_url=args.url,
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body:\n{json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✓ Webhook sent successfully!")
        else:
            print("\n✗ Webhook failed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
