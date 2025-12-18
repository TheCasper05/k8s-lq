"""
Email verification and resend views.
"""

from allauth.account.internal.flows.email_verification import (
    handle_verification_email_rate_limit,
)
from allauth.account.models import (
    EmailAddress,
    EmailConfirmation,
    EmailConfirmationHMAC,
)
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class JWTVerifyEmailView(APIView):
    """
    Verify email using the confirmation key.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        key = request.data.get("key") or request.headers.get(
            "x-email-verification-key", ""
        )
        if not key:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Verification key is required",
                            "code": "required",
                            "param": "key",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_confirmation = EmailConfirmation.from_key(key)
        if not email_confirmation:
            email_confirmation = EmailConfirmation.objects.filter(key=key).first()
        if not email_confirmation:
            email_confirmation = EmailConfirmationHMAC.from_key(key)
        if not email_confirmation:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Invalid or expired verification key",
                            "code": "invalid_key",
                            "param": "key",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_address = email_confirmation.confirm(request)
        if not email_address:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Verification failed",
                            "code": "verification_failed",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_verified = True
        user = email_address.user

        return Response(
            {
                "status": 200,
                "data": {"message": "Email verified", "email": email_address.email},
                "meta": {"email_verified": email_verified, "user_id": str(user.id)},
            }
        )


class JWTResendEmailVerificationView(APIView):
    """
    Resend email verification using the expired key.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        key = request.data.get("key")
        email = request.data.get("email")

        if not key and not email:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Verification key or email is required",
                            "code": "required",
                            "param": "key",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_address = None

        if key:
            # Try to find the confirmation (even if expired)
            email_confirmation = EmailConfirmation.objects.filter(key=key).first()

            if email_confirmation:
                email_address = email_confirmation.email_address
            else:
                # Try HMAC key
                try:
                    hmac_confirmation = EmailConfirmationHMAC.from_key(key)
                    if hmac_confirmation:
                        email_address = hmac_confirmation.email_address
                except (ValueError, TypeError, AttributeError):
                    pass
        elif email:
            email_address = EmailAddress.objects.filter(email__iexact=email).first()

        if not email_address:
            param = "key" if key else "email"
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Invalid verification key"
                            if key
                            else "Invalid verification request",
                            "code": "invalid_key",
                            "param": param,
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = email_address.user

        if email_address.verified:
            return Response(
                {
                    "status": 409,
                    "errors": [
                        {
                            "message": "Email already verified",
                            "code": "email_already_verified",
                        }
                    ],
                    "meta": {"email_verified": True},
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Rate limit verification emails using allauth helper
        if not handle_verification_email_rate_limit(
            request, email_address.email, raise_exception=False
        ):
            return Response(
                {
                    "status": 429,
                    "errors": [
                        {
                            "message": "Too many verification requests. Try again later.",
                            "code": "rate_limited",
                        }
                    ],
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Send new confirmation email
        email_address.send_confirmation(request, signup=False)

        return Response(
            {
                "status": 200,
                "data": {"message": "Verification email sent"},
                "meta": {"email_verified": False, "user_id": str(user.id)},
            }
        )


__all__ = [
    "JWTVerifyEmailView",
    "JWTResendEmailVerificationView",
    "handle_verification_email_rate_limit",
]
