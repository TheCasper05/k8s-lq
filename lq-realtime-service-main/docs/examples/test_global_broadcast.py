#!/usr/bin/env python3
"""
Test script for global broadcast functionality.

This script sends a global broadcast message to all connected users.
Requires the system API key for authentication.

Usage:
    python test_global_broadcast.py --api-key YOUR_SYSTEM_API_KEY
"""

import argparse
import sys

import httpx


def send_global_broadcast(
    api_key: str,
    message_title: str,
    message_text: str,
    priority: str = "normal",
    base_url: str = "http://localhost:8082",
):
    """Send a global broadcast message to all connected users."""

    url = f"{base_url}/api/broadcast/global"

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }

    payload = {
        "message_type": "system",
        "payload": {
            "title": message_title,
            "message": message_text,
            "priority": priority,
        },
        "from_user": "system",
    }

    try:
        print(f"Sending global broadcast to {base_url}...")
        print(f"Message: {message_title}")
        print("-" * 80)

        response = httpx.post(url, json=payload, headers=headers, timeout=10.0)

        if response.status_code == 200:
            result = response.json()
            print("✓ Broadcast sent successfully!")
            print(f"  Subscribers reached: {result['subscribers_reached']}")
            print(f"  Timestamp: {result['timestamp']}")
            print(f"  Message: {result['message']}")
            print("-" * 80)
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"  Response: {response.text}")
            return False

    except httpx.RequestError as e:
        print(f"✗ Request failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send global broadcast message")
    parser.add_argument(
        "--api-key",
        default="change-me-system-api-key-min-32-chars",
        help="System API key",
    )
    parser.add_argument(
        "--title",
        default="System Announcement",
        help="Message title",
    )
    parser.add_argument(
        "--message",
        default="This is a test global broadcast to all users!",
        help="Message text",
    )
    parser.add_argument(
        "--priority",
        choices=["low", "normal", "high", "urgent"],
        default="normal",
        help="Message priority",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8082",
        help="Base URL of the service",
    )

    args = parser.parse_args()

    success = send_global_broadcast(
        api_key=args.api_key,
        message_title=args.title,
        message_text=args.message,
        priority=args.priority,
        base_url=args.base_url,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
