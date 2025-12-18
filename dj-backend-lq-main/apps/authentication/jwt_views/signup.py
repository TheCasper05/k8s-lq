"""
Signup view that creates users and triggers email verification.
"""

import logging

from allauth.account import app_settings as allauth_app_settings
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import _ratelimit

User = get_user_model()


class JWTSignupView(APIView):
    """
    Signup view that creates a user and returns JWT tokens.
    Compatible with allauth data format.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")
        password2 = request.data.get("password2")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")

        # Rate limit signup attempts
        if email and not _ratelimit(request, "signup", email):
            return Response(
                {
                    "status": 429,
                    "errors": [
                        {
                            "message": "Too many signup attempts. Try again later.",
                            "code": "rate_limited",
                            "param": "email",
                        }
                    ],
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Validate required fields
        if not email or not password:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Email and password are required",
                            "code": "required",
                            "param": "email" if not email else "password",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate password confirmation
        if password != password2:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Passwords do not match",
                            "code": "password_mismatch",
                            "param": "password2",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "; ".join(e.messages),
                            "code": "invalid_password",
                            "param": "password",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use email as username if username not provided
        if not username:
            username = email

        # Enforce unique email if configured in allauth
        if (
            allauth_app_settings.UNIQUE_EMAIL
            and EmailAddress.objects.filter(email__iexact=email, verified=True).exists()
        ):
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "A user with this email already exists",
                            "code": "email_taken",
                            "param": "email",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            # Register email with allauth and trigger verification email
            email_address, _ = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={"primary": True, "verified": False},
            )
            email_address.send_confirmation(request, signup=True)

            # Return success without tokens - user must verify email first
            return Response(
                {
                    "status": 200,
                    "data": {
                        "user": {
                            "id": str(user.id),
                            "display": user.username,
                            "email": user.email,
                            "has_usable_password": user.has_usable_password(),
                            "username": user.username,
                            "onboarding_completed": user.onboarding_completed,
                            "email_verified": False,
                        },
                        "message": "Account created. Please verify your email to login.",
                    },
                    "meta": {
                        "is_authenticated": False,
                        "email_verified": False,
                        "verification_sent": True,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except IntegrityError as e:
            # Handle unique constraint violations
            error_message = "A user with this email or username already exists"
            if "email" in str(e).lower():
                param = "email"
            elif "username" in str(e).lower():
                param = "username"
            else:
                param = "email"

            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": error_message,
                            "code": "unique_constraint",
                            "param": param,
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            # Handle Django validation errors
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "; ".join(e.messages)
                            if hasattr(e, "messages")
                            else str(e),
                            "code": "validation_error",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:  # pragma: no cover - unexpected errors
            # Log unexpected errors but don't expose details to user
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error during signup: {str(e)}", exc_info=True)

            return Response(
                {
                    "status": 500,
                    "errors": [
                        {
                            "message": "An unexpected error occurred during signup. Please try again.",
                            "code": "server_error",
                        }
                    ],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = ["JWTSignupView"]
