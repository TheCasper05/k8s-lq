"""
Password reset request and confirmation views.
"""

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import _ratelimit

User = get_user_model()


class JWTPasswordResetRequestView(APIView):
    """
    Request password reset - sends email with reset key.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Email is required",
                            "code": "required",
                            "param": "email",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Rate limit password reset attempts
        if not _ratelimit(request, "reset_password", email):
            return Response(
                {
                    "status": 429,
                    "errors": [
                        {
                            "message": "Too many password reset attempts. Try again later.",
                            "code": "rate_limited",
                        }
                    ],
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            _ = User.objects.get(email__iexact=email)

            # Use allauth's password reset functionality
            from allauth.account.forms import ResetPasswordForm

            form = ResetPasswordForm({"email": email})
            if form.is_valid():
                form.save(request)

        except User.DoesNotExist:
            pass  # Don't leak whether user exists

        # Always return success to avoid email enumeration
        return Response(
            {
                "status": 200,
                "data": {
                    "message": "If an account exists with this email, a password reset link has been sent."
                },
            }
        )


class JWTPasswordResetConfirmView(APIView):
    """
    Confirm password reset with key and new password.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        key = request.data.get("key")
        password = request.data.get("password")
        password2 = request.data.get("password2")

        # Validate inputs
        if not key:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Reset key is required",
                            "code": "required",
                            "param": "key",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not password or not password2:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Password and confirmation are required",
                            "code": "required",
                            "param": "password",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        # Use allauth's password reset confirmation
        from allauth.account.forms import ResetPasswordKeyForm

        try:
            # Try to get user from key
            form = ResetPasswordKeyForm(
                data={
                    "password1": password,
                    "password2": password2,
                },
                temp_key=key,
            )

            if form.is_valid():
                form.save()

                # Get the user from the form
                user = form.user

                return Response(
                    {
                        "status": 200,
                        "data": {
                            "message": "Password reset successfully",
                            "user_id": str(user.id),
                        },
                    }
                )
            else:
                # Form validation failed
                return Response(
                    {
                        "status": 400,
                        "errors": [
                            {
                                "message": "Invalid or expired reset key",
                                "code": "invalid_key",
                                "param": "key",
                            }
                        ],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:  # pragma: no cover - unexpected errors
            logger = logging.getLogger(__name__)
            logger.error(f"Password reset error: {str(e)}", exc_info=True)

            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Invalid or expired reset key",
                            "code": "invalid_key",
                            "param": "key",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


__all__ = ["JWTPasswordResetRequestView", "JWTPasswordResetConfirmView"]
