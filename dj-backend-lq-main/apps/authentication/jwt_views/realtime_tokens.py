"""
Realtime JWT token generation endpoint.

This module provides an endpoint for generating short-lived JWT tokens
specifically for authenticating frontend connections to lq-realtime-service.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle

from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from authentication.models import UserWorkspaceMembership, MembershipStatus
from authentication.jwt_views.realtime_utils import (
    generate_realtime_token,
    RealtimeJWTError,
    MissingRealtimeConfigError,
)


class RealtimeTokenRateThrottle(UserRateThrottle):
    """Custom throttle for realtime token generation (20 per minute)."""

    rate = "20/min"


class RealtimeTokenView(APIView):
    """
    Generate a short-lived JWT token for realtime service authentication.

    POST /api/realtime/token

    This endpoint creates a temporary JWT token (5-10 minutes) that allows
    the authenticated frontend to connect to lq-realtime-service. This token
    is NOT a replacement for the main session JWT - it's a scoped access token
    with "realtime" scope only.

    **Authentication:** Required (JWT)

    **Request Body:**
    ```json
    {
        "workspace_id": "uuid-string"  // Required: The workspace/tenant ID
    }
    ```

    **Response (200 OK):**
    ```json
    {
        "realtime_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "expires_in": 600,  // seconds until expiration
        "token_type": "Bearer"
    }
    ```

    **Error Responses:**
    - 400 Bad Request: Missing or invalid workspace_id
    - 401 Unauthorized: User not authenticated
    - 403 Forbidden: User doesn't have access to the workspace
    - 500 Internal Server Error: Token generation failed (config issue)
    - 429 Too Many Requests: Rate limit exceeded
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [RealtimeTokenRateThrottle]

    def post(self, request):
        """Generate and return a realtime JWT token."""
        user = request.user

        # Extract workspace_id from request body
        workspace_id = request.data.get("workspace_id")

        if not workspace_id:
            return Response(
                {
                    "error": "workspace_id_required",
                    "detail": _("workspace_id is required in the request body."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that the user has access to this workspace
        try:
            membership = (
                UserWorkspaceMembership.objects.filter(
                    Q(user=user)
                    & Q(workspace__id=workspace_id)
                    & Q(status=MembershipStatus.ACTIVE)
                )
                .select_related("workspace")
                .first()
            )

            if not membership:
                return Response(
                    {
                        "error": "workspace_access_denied",
                        "detail": _(
                            "You don't have access to this workspace or it doesn't exist."
                        ),
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Exception:
            return Response(
                {
                    "error": "workspace_validation_failed",
                    "detail": _("Failed to validate workspace access."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract session_id if available (optional)
        session_id = None
        if hasattr(request, "session") and request.session.session_key:
            session_id = request.session.session_key

        # Generate the realtime JWT token
        try:
            realtime_token = generate_realtime_token(
                user_id=str(user.id), tenant_id=str(workspace_id), session_id=session_id
            )

            # Get expiration time from settings (default 10 minutes = 600 seconds)
            from django.conf import settings

            expiration_minutes = getattr(
                settings, "REALTIME_JWT_EXPIRATION_MINUTES", 10
            )
            expires_in = expiration_minutes * 60

            return Response(
                {
                    "realtime_token": realtime_token,
                    "expires_in": expires_in,
                    "token_type": "Bearer",
                },
                status=status.HTTP_200_OK,
            )

        except MissingRealtimeConfigError:
            # Configuration error - this should be logged and alerted
            return Response(
                {
                    "error": "configuration_error",
                    "detail": _(
                        "Realtime token service is not properly configured. Please contact support."
                    ),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except RealtimeJWTError:
            # Token generation error
            return Response(
                {
                    "error": "token_generation_failed",
                    "detail": _("Failed to generate realtime token. Please try again."),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception:
            # Unexpected error - log it
            return Response(
                {
                    "error": "internal_error",
                    "detail": _("An unexpected error occurred. Please try again."),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
