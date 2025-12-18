"""
Token validation endpoint for external services (e.g., realtime-service).

This endpoint allows external microservices to validate JWT tokens
and get user information without sharing the JWT secret.
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from .utils import _is_email_verified

User = get_user_model()


class JWTValidateView(APIView):
    """
    Validate JWT token and return user information.

    This is intended for use by other microservices (like realtime-service)
    that need to validate tokens without direct database access.

    POST /auth/jwt/validate/
    {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }

    Returns:
    - 200 with user data if token is valid
    - 401 if token is invalid/expired
    """

    permission_classes = [AllowAny]

    def post(self, request):
        token_string = request.data.get("token")

        if not token_string:
            return Response(
                {
                    "status": 400,
                    "errors": [{"message": "Token is required", "code": "required"}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Validate and decode the token
            access_token = AccessToken(token_string)
            user_id = access_token.get("user_id")

            # Get user from database
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {
                        "status": 401,
                        "errors": [
                            {"message": "User not found", "code": "user_not_found"}
                        ],
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Check if user is active
            if not user.is_active:
                return Response(
                    {
                        "status": 401,
                        "errors": [
                            {"message": "User is inactive", "code": "user_inactive"}
                        ],
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            email_verified = _is_email_verified(user)

            # Return user information
            return Response(
                {
                    "status": 200,
                    "data": {
                        "valid": True,
                        "user": {
                            "id": str(user.id),
                            "username": user.username,
                            "email": user.email,
                            "is_active": user.is_active,
                            "is_staff": user.is_staff,
                            "onboarding_completed": user.onboarding_completed,
                            "email_verified": email_verified,
                        },
                        "token_payload": {
                            "user_id": str(user_id),
                            "exp": access_token.get("exp"),
                            "iat": access_token.get("iat"),
                            "jti": access_token.get("jti"),
                        },
                    },
                }
            )

        except (TokenError, InvalidToken) as e:
            return Response(
                {
                    "status": 401,
                    "errors": [
                        {
                            "message": "Invalid or expired token",
                            "code": "token_invalid",
                            "detail": str(e),
                        }
                    ],
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


__all__ = ["JWTValidateView"]
