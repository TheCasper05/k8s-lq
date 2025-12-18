"""
Social login (Google/Microsoft) that issues JWT tokens.
"""

import logging

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def get_social_app(provider):
    """
    Get SocialApp from database for the given provider.
    Raises ValueError if not found.
    """
    from allauth.socialaccount.models import SocialApp

    try:
        social_app = SocialApp.objects.get(provider=provider)
        return social_app
    except SocialApp.DoesNotExist:
        raise ValueError(
            f"SocialApp for '{provider}' not found in database. "
            f"Run: python manage.py setup_social_apps"
        )
    except SocialApp.MultipleObjectsReturned:
        raise ValueError(
            f"Multiple SocialApps found for '{provider}'. "
            f"Please remove duplicates from database."
        )


class JWTSocialLoginView(APIView):
    """
    Social login (Google/Microsoft) that returns JWT tokens.
    Handles both signup and login scenarios.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        provider = request.data.get("provider")
        access_token = request.data.get("access_token")
        id_token = request.data.get("id_token")

        if not provider:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Provider is required (google or microsoft)",
                            "code": "required",
                            "param": "provider",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if provider not in ["google", "microsoft"]:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "Invalid provider. Must be 'google' or 'microsoft'",
                            "code": "invalid_provider",
                            "param": "provider",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not access_token and not id_token:
            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": "access_token or id_token is required",
                            "code": "required",
                            "param": "access_token",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from allauth.socialaccount.providers.google.provider import GoogleProvider
            from allauth.socialaccount.providers.microsoft.provider import MicrosoftGraphProvider

            # Get SocialApp from database
            social_app = get_social_app(provider)

            # Get the provider's adapter to fetch user info
            from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
            from allauth.socialaccount.providers.microsoft.views import MicrosoftGraphOAuth2Adapter

            if provider == "google":
                adapter = GoogleOAuth2Adapter(request)
            elif provider == "microsoft":
                adapter = MicrosoftGraphOAuth2Adapter(request)

            # Fetch user info from the provider using the access token
            import requests

            if provider == "google":
                # Get user info from Google
                user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
                headers = {"Authorization": f"Bearer {access_token or id_token}"}
                response = requests.get(user_info_url, headers=headers)
                response.raise_for_status()
                user_data = response.json()
            elif provider == "microsoft":
                # Get user info from Microsoft
                user_info_url = "https://graph.microsoft.com/v1.0/me"
                headers = {"Authorization": f"Bearer {access_token}"}
                response = requests.get(user_info_url, headers=headers)
                response.raise_for_status()
                user_data = response.json()

            # Get the provider class
            if provider == "google":
                provider_class = GoogleProvider
            elif provider == "microsoft":
                provider_class = MicrosoftGraphProvider

            # Get the provider instance
            provider_instance = provider_class(request, app=social_app)

            # Get SocialLogin from the provider's token and user data
            login = provider_instance.sociallogin_from_response(request, user_data)

            # Check if this is a new user (signup) or existing (login)
            is_new_user = not login.is_existing

            # Complete the social login process
            login.lookup()
            login.save(request, connect=True)

            user = login.account.user

            # Verify/create email address
            email_address, _ = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={
                    "primary": True,
                    "verified": True,
                },  # Social logins are pre-verified
            )

            # Update verified status if not already verified
            if not email_address.verified:
                email_address.verified = True
                email_address.save()

            # Get all authentication methods for this user
            from allauth.socialaccount.models import SocialAccount

            auth_methods = []

            # Check if user has password
            if user.has_usable_password():
                auth_methods.append({
                    "method": "password",
                    "email": user.email
                })

            # Get all connected social accounts
            social_accounts = SocialAccount.objects.filter(user=user)
            for account in social_accounts:
                auth_methods.append({
                    "method": account.provider,
                    "email": account.extra_data.get("email", user.email),
                    "uid": account.uid
                })

            # Check if this was an account connection
            # True if: user existed before AND had other auth methods
            was_connected = not is_new_user and len(auth_methods) > 1

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
                            "email_verified": True,
                        },
                        "methods": auth_methods,
                        "is_new_user": is_new_user,
                        "account_connected": was_connected,  # True si se conectó una cuenta existente
                    },
                    "meta": {
                        "is_authenticated": True,
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh),
                        "email_verified": True,
                        "onboarding_completed": not is_new_user
                        and user.onboarding_completed,
                    },
                },
                status=status.HTTP_201_CREATED if is_new_user else status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {
                    "status": 500,
                    "errors": [
                        {
                            "message": str(e),
                            "code": "provider_not_configured",
                        }
                    ],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:  # pragma: no cover - unexpected errors
            logger = logging.getLogger(__name__)
            logger.error(f"Social login error: {str(e)}", exc_info=True)

            # In debug mode, return detailed error for easier debugging
            if settings.DEBUG:
                error_message = f"Social login failed: {type(e).__name__}: {str(e)}"
            else:
                error_message = "Social login failed. Please try again."

            return Response(
                {
                    "status": 400,
                    "errors": [
                        {
                            "message": error_message,
                            "code": "social_login_failed",
                        }
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


__all__ = ["JWTSocialLoginView"]
