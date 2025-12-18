"""
Login view that issues JWT tokens for allauth compatibility.
"""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import _is_email_verified, _ratelimit

User = get_user_model()


class JWTLoginView(APIView):
    """
    Login view that returns JWT tokens instead of sessions.
    Compatible with allauth data format.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Email and password are required",
                            "code": "required",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Rate limit login attempts
        if not _ratelimit(request, "login", email):
            return Response(
                {
                    "status": 429,
                    "errors": [
                        {
                            "message": "Too many login attempts. Try again later.",
                            "code": "rate_limited",
                            "param": "email",
                        }
                    ],
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Authenticate user
        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {
                    "status": 401,
                    "errors": [
                        {
                            "message": "Invalid credentials",
                            "code": "invalid_credentials",
                        }
                    ],
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Require verified email before issuing tokens
        email_verified = _is_email_verified(user)
        if not email_verified:
            return Response(
                {
                    "status": 403,
                    "errors": [
                        {
                            "message": "Email not verified",
                            "code": "email_not_verified",
                            "param": "email",
                        }
                    ],
                    "meta": {"is_authenticated": False},
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

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
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "email_verified": email_verified,
                },
            }
        )


__all__ = ["JWTLoginView"]
