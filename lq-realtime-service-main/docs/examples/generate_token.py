#!/usr/bin/env python3
"""
Generate a test JWT token for WebSocket authentication.

Usage:
    python generate_token.py --user-id USER_ID --tenant-id TENANT_ID
"""

import argparse
from datetime import datetime, timedelta

import jwt


def generate_token(
    user_id: str,
    tenant_id: str,
    secret_key: str = "your-super-secret-jwt-key-change-in-production-min-32-chars",
    algorithm: str = "HS256",
    expire_minutes: int = 60,
):
    """Generate a JWT token for testing."""

    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)

    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "scope": "ws:connect",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "user_role": "user",
    }

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def main():
    parser = argparse.ArgumentParser(description="Generate JWT token for testing")
    parser.add_argument("--user-id", required=True, help="User ID")
    parser.add_argument("--tenant-id", required=True, help="Tenant ID")
    parser.add_argument(
        "--secret",
        default="your-super-secret-jwt-key-change-in-production-min-32-chars",
        help="JWT secret key",
    )
    parser.add_argument("--expire", type=int, default=60, help="Token expiration in minutes")

    args = parser.parse_args()

    token = generate_token(
        user_id=args.user_id,
        tenant_id=args.tenant_id,
        secret_key=args.secret,
        expire_minutes=args.expire,
    )

    print("=" * 80)
    print("JWT Token Generated Successfully")
    print("=" * 80)
    print(f"User ID:    {args.user_id}")
    print(f"Tenant ID:  {args.tenant_id}")
    print(f"Expires:    {args.expire} minutes")
    print("=" * 80)
    print("\nToken:")
    print(token)
    print("\n" + "=" * 80)
    print("\nUse this token to connect to WebSocket:")
    print(f"ws://localhost:8082/ws?token={token}")
    print("=" * 80)


if __name__ == "__main__":
    main()
