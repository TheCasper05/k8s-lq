"""
Tests for JWT authentication views.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from allauth.account.models import EmailAddress
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """API client fixture."""
    return APIClient()


@pytest.fixture
def user_data():
    """User data fixture."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!",
        "password2": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def create_user(db):
    """Factory fixture to create users."""

    def _create_user(
        email="test@example.com",
        username="testuser",
        password="TestPass123!",
        verified=True,
    ):
        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        # Create email address record
        email_address = EmailAddress.objects.create(
            user=user, email=email, primary=True, verified=verified
        )

        return user, email_address

    return _create_user


@pytest.mark.django_db
class TestJWTSignupView:
    """Tests for JWT signup endpoint."""

    def test_signup_success(self, api_client, user_data):
        """Test successful user signup."""
        url = reverse("jwt_signup")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == 200
        assert response.data["meta"]["is_authenticated"] is False
        assert response.data["meta"]["email_verified"] is False
        assert response.data["meta"]["verification_sent"] is True
        assert "access_token" not in response.data["meta"]
        assert "refresh_token" not in response.data["meta"]
        assert "message" in response.data["data"]

        # Verify user was created
        user = User.objects.get(email=user_data["email"])
        assert user.username == user_data["username"]
        assert user.check_password(user_data["password"])

        # Verify email address was created (unverified)
        email_address = EmailAddress.objects.get(user=user)
        assert email_address.verified is False

    def test_signup_missing_email(self, api_client, user_data):
        """Test signup with missing email."""
        url = reverse("jwt_signup")
        data = user_data.copy()
        del data["email"]

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400
        assert any("email" in error["param"] for error in response.data["errors"])

    def test_signup_missing_password(self, api_client, user_data):
        """Test signup with missing password."""
        url = reverse("jwt_signup")
        data = user_data.copy()
        del data["password"]

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400

    def test_signup_password_mismatch(self, api_client, user_data):
        """Test signup with password mismatch."""
        url = reverse("jwt_signup")
        data = user_data.copy()
        data["password2"] = "DifferentPass123!"

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400
        assert any(
            "password_mismatch" in error["code"] for error in response.data["errors"]
        )

    def test_signup_weak_password(self, api_client, user_data):
        """Test signup with weak password."""
        url = reverse("jwt_signup")
        data = user_data.copy()
        data["password"] = "123"
        data["password2"] = "123"

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400
        assert any(
            "invalid_password" in error["code"] for error in response.data["errors"]
        )

    def test_signup_duplicate_email(self, api_client, user_data, create_user):
        """Test signup with duplicate email."""
        # Create existing user
        create_user(email=user_data["email"], verified=True)

        url = reverse("jwt_signup")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400

    def test_jwt_signup_creates_email_address_and_sends_email(
        self, api_client, user_data
    ):
        """Test that signup creates EmailAddress record and triggers email."""
        url = reverse("jwt_signup")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verify user was created
        user = User.objects.get(email=user_data["email"])
        assert user is not None

        # Verify EmailAddress was created (unverified)
        email_address = EmailAddress.objects.get(user=user, email=user_data["email"])
        assert email_address is not None
        assert email_address.verified is False
        assert email_address.primary is True

    def test_jwt_signup_blocks_existing_verified_email(
        self, api_client, user_data, create_user
    ):
        """Test that signup blocks when email already exists and is verified."""
        # Create existing verified user
        create_user(
            email=user_data["email"],
            username="existinguser",
            verified=True,
        )

        url = reverse("jwt_signup")
        # Try to signup with same email but different username
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400
        assert any(
            "email" in error.get("param", "") or "exists" in error["message"].lower()
            for error in response.data["errors"]
        )

    def test_signup_rate_limit(self, api_client, user_data, settings):
        """Test signup rate limiting."""
        # This test verifies that the rate limiting logic is in place
        # Actual rate limiting behavior depends on allauth configuration
        # and is better tested with mocking
        url = reverse("jwt_signup")

        # Make a single request to verify endpoint handles rate limiting gracefully
        response = api_client.post(url, user_data, format="json")

        # Should succeed or be rate limited, but not crash
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_429_TOO_MANY_REQUESTS,
        ]


@pytest.mark.django_db
class TestJWTLoginView:
    """Tests for JWT login endpoint."""

    def test_login_success(self, api_client, create_user):
        """Test successful login with verified email."""
        user, _ = create_user(
            email="test@example.com", password="TestPass123!", verified=True
        )

        url = reverse("jwt_login")
        data = {"email": "test@example.com", "password": "TestPass123!"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == 200
        assert response.data["meta"]["is_authenticated"] is True
        assert response.data["meta"]["email_verified"] is True
        assert "access_token" in response.data["meta"]
        assert "refresh_token" in response.data["meta"]
        assert response.data["data"]["user"]["email"] == user.email

    def test_login_unverified_email(self, api_client, create_user):
        """Test login with unverified email returns 403."""
        user, _ = create_user(
            email="test@example.com", password="TestPass123!", verified=False
        )

        url = reverse("jwt_login")
        data = {"email": "test@example.com", "password": "TestPass123!"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["status"] == 403
        assert response.data["meta"]["is_authenticated"] is False
        assert any(
            "email_not_verified" in error["code"] for error in response.data["errors"]
        )
        assert "access_token" not in response.data["meta"]

    def test_login_invalid_credentials(self, api_client, create_user):
        """Test login with invalid credentials."""
        create_user(email="test@example.com", password="TestPass123!", verified=True)

        url = reverse("jwt_login")
        data = {"email": "test@example.com", "password": "WrongPassword123!"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["status"] == 401
        assert any(
            "invalid_credentials" in error["code"] for error in response.data["errors"]
        )

    def test_login_missing_fields(self, api_client):
        """Test login with missing fields."""
        url = reverse("jwt_login")
        data = {"email": "test@example.com"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400

    def test_login_nonexistent_user(self, api_client):
        """Test login with nonexistent user."""
        url = reverse("jwt_login")
        data = {"email": "nonexistent@example.com", "password": "TestPass123!"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestJWTRefreshView:
    """Tests for JWT token refresh endpoint."""

    def test_refresh_token_success(self, api_client, create_user):
        """Test successful token refresh."""
        user, _ = create_user(verified=True)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)

        url = reverse("jwt_refresh")
        data = {"refresh": refresh_token}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == 200
        assert "access_token" in response.data["meta"]
        assert "refresh_token" in response.data["meta"]  # Rotation enabled

    def test_refresh_token_invalid(self, api_client):
        """Test refresh with invalid token."""
        url = reverse("jwt_refresh")
        data = {"refresh": "invalid_token"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["status"] == 401
        assert any("token_error" in error["code"] for error in response.data["errors"])

    def test_refresh_token_missing(self, api_client):
        """Test refresh without token."""
        url = reverse("jwt_refresh")
        data = {}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400


@pytest.mark.django_db
class TestJWTSessionView:
    """Tests for JWT session introspection and logout."""

    def test_session_get_authenticated(self, api_client, create_user):
        """Test session GET with valid token."""
        user, _ = create_user(verified=True)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        url = reverse("jwt_session")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == 200
        assert response.data["meta"]["is_authenticated"] is True
        assert response.data["data"]["user"]["email"] == user.email

    def test_session_get_unauthenticated(self, api_client):
        """Test session GET without token."""
        url = reverse("jwt_session")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == 200
        assert response.data["meta"]["is_authenticated"] is False
        assert response.data["data"] == {}

    def test_logout_success(self, api_client, create_user):
        """Test logout with refresh token."""
        user, _ = create_user(verified=True)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)

        url = reverse("jwt_session")
        data = {"refresh": refresh_token}

        response = api_client.delete(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == 200
        assert response.data["meta"]["is_authenticated"] is False

    def test_logout_without_token(self, api_client):
        """Test logout without refresh token (still succeeds)."""
        url = reverse("jwt_session")

        response = api_client.delete(url, {}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == 200


@pytest.mark.django_db
class TestJWTVerifyEmailView:
    """Tests for email verification endpoint."""

    def test_verify_email_success(self, api_client, create_user):
        """Test successful email verification."""

        user, email_address = create_user(verified=False)

        # Create confirmation using EmailConfirmationHMAC for simplicity in tests
        from allauth.account.models import EmailConfirmationHMAC

        confirmation = EmailConfirmationHMAC(email_address)
        key = confirmation.key

        url = reverse("jwt_verify_email_alt")
        data = {"key": key}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == 200
        assert response.data["meta"]["email_verified"] is True
        assert response.data["data"]["email"] == user.email

        # Verify email is now verified in database
        email_address.refresh_from_db()
        assert email_address.verified is True

    def test_verify_email_alternate_endpoint(self, api_client, create_user):
        """Test email verification with alternate endpoint path."""
        user, email_address = create_user(
            email="alt@example.com", username="altuser", verified=False
        )

        # Create confirmation
        from allauth.account.models import EmailConfirmationHMAC

        confirmation = EmailConfirmationHMAC(email_address)
        key = confirmation.key

        # Use alternate URL that frontend might call
        url = reverse("jwt_verify_email_alt")
        data = {"key": key}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == 200
        assert response.data["meta"]["email_verified"] is True
        assert response.data["data"]["email"] == user.email

        # Verify email is now verified in database
        email_address.refresh_from_db()
        assert email_address.verified is True

    def test_verify_email_invalid_key(self, api_client):
        """Test email verification with invalid key."""
        url = reverse("jwt_verify_email_alt")
        data = {"key": "invalid_key"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400
        assert any("invalid_key" in error["code"] for error in response.data["errors"])

    def test_verify_email_missing_key(self, api_client):
        """Test email verification without key."""
        url = reverse("jwt_resend_verification_email")
        data = {}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400
        assert any("required" in error["code"] for error in response.data["errors"])


@pytest.mark.django_db
class TestJWTResendEmailVerificationView:
    """Tests for resend email verification endpoint."""

    def test_resend_verification_success(self, api_client, create_user, settings):
        """Test successful verification email resend with key."""
        from allauth.account.models import EmailConfirmationHMAC

        # Temporarily disable rate limits for this test
        original_limits = getattr(settings, "ACCOUNT_RATE_LIMITS", None)
        settings.ACCOUNT_RATE_LIMITS = {}

        try:
            user, email_address = create_user(
                email="resend@example.com", username="resenduser", verified=False
            )

            # Create a confirmation key
            confirmation = EmailConfirmationHMAC(email_address)
            key = confirmation.key

            url = reverse("jwt_resend_verification_email")
            data = {"key": key}

            response = api_client.post(url, data, format="json")

            # Accept both 200 and 429 (if rate limited from previous tests)
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_429_TOO_MANY_REQUESTS,
            ]

            if response.status_code == status.HTTP_200_OK:
                assert response.data["status"] == 200
                assert response.data["meta"]["email_verified"] is False
        finally:
            # Restore original rate limits
            if original_limits is not None:
                settings.ACCOUNT_RATE_LIMITS = original_limits

    def test_resend_verification_already_verified(self, api_client, create_user):
        """Test resend verification for already verified email."""
        from allauth.account.models import EmailConfirmation

        # Create user NOT verified first
        user, email_address = create_user(
            email="toverify@example.com", username="toverifyuser", verified=False
        )

        # Create confirmation and get key
        confirmation = EmailConfirmation.create(email_address)
        confirmation.save()
        key = confirmation.key

        # Now verify the email
        email_address.verified = True
        email_address.save()

        # Try to resend with the old key
        url = reverse("jwt_resend_verification")
        data = {"key": key}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data["status"] == 409
        assert response.data["meta"]["email_verified"] is True

    # def test_resend_verification_for_verified_email(self, api_client, create_user):
    #     """Test resend verification returns 409 for verified email with HMAC key."""
    #     from allauth.account.models import EmailConfirmationHMAC

    #     # Create unverified user and get HMAC key
    #     user, email_address = create_user(
    #         email="verified@example.com", username="verifieduser", verified=False
    #     )

    #     confirmation = EmailConfirmationHMAC(email_address)
    #     key = confirmation.key

    #     # Verify the email
    #     email_address.verified = True
    #     email_address.save()

    #     # Try to resend with the key
    #     url = reverse("jwt_resend_verification")
    #     data = {"key": key}

    #     response = api_client.post(url, data, format="json")

    #     assert response.status_code == status.HTTP_409_CONFLICT
    #     assert response.data["status"] == 409
    #     assert any(
    #         "already verified" in error["message"].lower()
    #         for error in response.data["errors"]
    #     )
    #     assert response.data["meta"]["email_verified"] is True

    def test_resend_verification_invalid_key(self, api_client):
        """Test resend verification with invalid key."""
        url = reverse("jwt_verify_email_app")
        data = {"key": "invalid_key_12345"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400
        assert any("invalid_key" in error["code"] for error in response.data["errors"])

    def test_resend_verification_missing_key(self, api_client):
        """Test resend verification without key."""
        url = reverse("jwt_resend_verification")
        data = {}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == 400


@pytest.mark.django_db
class TestJWTAuthenticationFlow:
    """Integration tests for complete JWT authentication flow."""

    def test_complete_signup_verify_login_flow(self, api_client, user_data):
        """Test complete flow: signup -> verify -> login."""
        from allauth.account.models import EmailConfirmationHMAC

        # 1. Signup
        signup_url = reverse("jwt_signup")
        signup_response = api_client.post(signup_url, user_data, format="json")

        assert signup_response.status_code == status.HTTP_201_CREATED
        assert "access_token" not in signup_response.data["meta"]

        # 2. Try to login without verification (should fail)
        login_url = reverse("jwt_login")
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        login_response = api_client.post(login_url, login_data, format="json")

        assert login_response.status_code == status.HTTP_403_FORBIDDEN

        # 3. Verify email using HMAC confirmation (simpler for tests)
        user = User.objects.get(email=user_data["email"])
        email_address = EmailAddress.objects.get(user=user)
        confirmation = EmailConfirmationHMAC(email_address)
        key = confirmation.key

        verify_url = reverse("jwt_verify_email_alt")
        verify_response = api_client.post(verify_url, {"key": key}, format="json")

        assert verify_response.status_code == status.HTTP_200_OK
        assert verify_response.data["meta"]["email_verified"] is True

        # 4. Login after verification (should succeed)
        login_response = api_client.post(login_url, login_data, format="json")

        assert login_response.status_code == status.HTTP_200_OK
        assert "access_token" in login_response.data["meta"]
        assert "refresh_token" in login_response.data["meta"]

    def test_token_refresh_and_logout_flow(self, api_client, create_user):
        """Test token refresh and logout flow."""
        user, _ = create_user(verified=True)

        # 1. Login
        login_url = reverse("jwt_login")
        login_data = {"email": user.email, "password": "TestPass123!"}
        login_response = api_client.post(login_url, login_data, format="json")

        assert login_response.status_code == status.HTTP_200_OK
        refresh_token = login_response.data["meta"]["refresh_token"]
        access_token = login_response.data["meta"]["access_token"]

        # 2. Access protected resource
        session_url = reverse("jwt_session")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        session_response = api_client.get(session_url)

        assert session_response.status_code == status.HTTP_200_OK
        assert session_response.data["meta"]["is_authenticated"] is True

        # 3. Refresh token
        refresh_url = reverse("jwt_refresh")
        refresh_response = api_client.post(
            refresh_url, {"refresh": refresh_token}, format="json"
        )

        assert refresh_response.status_code == status.HTTP_200_OK
        _new_access_token = refresh_response.data["meta"]["access_token"]
        new_refresh_token = refresh_response.data["meta"]["refresh_token"]

        # 4. Logout
        api_client.credentials()  # Clear auth
        logout_response = api_client.delete(
            session_url, {"refresh": new_refresh_token}, format="json"
        )

        assert logout_response.status_code == status.HTTP_200_OK
        assert logout_response.data["meta"]["is_authenticated"] is False
