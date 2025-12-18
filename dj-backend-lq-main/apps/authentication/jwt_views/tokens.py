"""
Token-related views: refresh and session introspection/logout.
"""

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import _is_email_verified

User = get_user_model()


class JWTRefreshView(APIView):
    """
    Refresh JWT access token.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {"message": "Refresh token is required", "code": "required"}
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)

            # Get user info for email verification status
            user_id = refresh.get("user_id")
            email_verified = False
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    email_verified = _is_email_verified(user)
                except User.DoesNotExist:
                    pass

            response_data = {
                "status": 200,
                "meta": {
                    "access_token": str(refresh.access_token),
                    "email_verified": email_verified,
                },
            }

            if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
                # Blacklist the old token if configured
                if settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False):
                    try:
                        refresh.blacklist()
                    except AttributeError:
                        # Blacklist not installed
                        pass

                # Return new refresh token
                refresh.set_jti()
                refresh.set_exp()
                response_data["meta"]["refresh_token"] = str(refresh)

            return Response(response_data)

        except TokenError:
            return Response(
                {
                    "status": 401,
                    "errors": [
                        {
                            "message": "Invalid or expired refresh token",
                            "code": "token_error",
                        }
                    ],
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:  # pragma: no cover - unexpected errors
            logger = logging.getLogger(__name__)
            logger.error(
                f"Unexpected error during token refresh: {str(e)}", exc_info=True
            )

            return Response(
                {
                    "status": 401,
                    "errors": [
                        {
                            "message": "Token refresh failed",
                            "code": "refresh_failed",
                        }
                    ],
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class JWTSessionView(APIView):
    """
    Session introspection for JWT tokens and logout handler.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        # Optional JWT introspection; return anonymous 200 when no/invalid token
        auth_result = None
        if request.META.get("HTTP_AUTHORIZATION"):
            auth = JWTAuthentication()
            try:
                auth_result = auth.authenticate(request)
            except InvalidToken:
                auth_result = None

        if not auth_result:
            return Response(
                {
                    "status": 200,
                    "data": {},
                    "meta": {"is_authenticated": False},
                }
            )

        user, token = auth_result
        email_verified = _is_email_verified(user)

        # Generate new access token (rotate)
        refresh = RefreshToken.for_user(user)
        new_access_token = str(refresh.access_token)

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
                        "email_verified": email_verified,
                    },
                    "methods": [{"method": "password", "email": user.email}],
                },
                "meta": {
                    "is_authenticated": True,
                    "email_verified": email_verified,
                    "access_token": new_access_token,
                    "refresh_token": str(refresh),
                    "token_payload": dict(getattr(token, "payload", {})),
                },
            }
        )

    def delete(self, request):
        """
        Logout by blacklisting the refresh token.
        Client must send refresh token in request body.
        """
        refresh_token = request.data.get("refresh")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                # Blacklist the refresh token
                try:
                    token.blacklist()
                except AttributeError:
                    # Blacklist not installed, token will expire naturally
                    pass
            except (TokenError, Exception):
                # Token is invalid or expired, but we still return success
                # to avoid leaking token validity information
                pass

        return Response(
            {
                "status": 200,
                "data": {"message": "Logged out successfully"},
                "meta": {"is_authenticated": False},
            }
        )


__all__ = ["JWTRefreshView", "JWTSessionView"]
