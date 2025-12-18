import pytest
from django.core import mail
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache


User = get_user_model()


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_jwt_signup_creates_email_address_and_sends_email(client):
    payload = {
        "email": "new@example.com",
        "username": "newuser",
        "password": "ExtreMegeousAAA",
        "password2": "ExtreMegeousAAA",
    }

    url = "/_allauth/browser/v1/auth/signup"
    response = client.post(url, payload, content_type="application/json")

    assert response.status_code == 201
    data = response.json()
    assert data["data"]["user"]["email"] == payload["email"]
    assert data["data"]["user"]["email_verified"] is False
    assert data["meta"]["email_verified"] is False

    email_address = EmailAddress.objects.get(email=payload["email"])
    assert email_address.primary is True
    assert email_address.verified is False
    # Confirmation email should be queued
    assert len(mail.outbox) == 1
    assert payload["email"] in mail.outbox[0].to


@pytest.mark.django_db
def test_jwt_signup_blocks_existing_verified_email(client):
    user = User.objects.create_user(
        username="existing", email="existing@example.com", password="pass1234"
    )
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=True
    )

    url = "/_allauth/browser/v1/auth/signup"
    response = client.post(
        url,
        {
            "email": user.email,
            "password": "ExtreMegeousAAA",
            "password2": "ExtreMegeousAAA",
        },
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["errors"][0]["code"] == "email_taken"


@pytest.mark.django_db
def test_jwt_login_requires_verified_email(client):
    user = User.objects.create_user(
        username="noverify", email="noverify@example.com", password="pass1234"
    )
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=False
    )

    url = "/_allauth/browser/v1/auth/login"
    response = client.post(
        url,
        {"email": user.email, "password": "pass1234"},
        content_type="application/json",
    )

    assert response.status_code == 403
    data = response.json()
    assert data["meta"]["is_authenticated"] is False
    assert data["errors"][0]["code"] == "email_not_verified"


@pytest.mark.django_db
def test_jwt_login_returns_tokens_when_email_verified(client):
    user = User.objects.create_user(
        username="verify", email="verify@example.com", password="pass1234"
    )
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=True
    )

    url = "/_allauth/browser/v1/auth/login"
    response = client.post(
        url,
        {"email": user.email, "password": "pass1234"},
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["is_authenticated"] is True
    assert data["meta"]["email_verified"] is True
    assert data["data"]["user"]["email_verified"] is True
    assert "access_token" in data["meta"]
    assert "refresh_token" in data["meta"]


@pytest.mark.django_db
def test_jwt_login_rate_limited(client, monkeypatch):
    def fake_ratelimit(request, action, key):
        return False

    monkeypatch.setattr("authentication.jwt_views.login._ratelimit", fake_ratelimit)

    url = "/_allauth/browser/v1/auth/login"
    response = client.post(
        url,
        {"email": "rl@example.com", "password": "pass"},
        content_type="application/json",
    )

    assert response.status_code == 429
    data = response.json()
    assert data["errors"][0]["code"] == "rate_limited"


@pytest.mark.skip(reason="JWT refresh endpoint disabled by default")
@pytest.mark.django_db
def test_jwt_refresh_includes_email_verified(client):
    user = User.objects.create_user(
        username="refresh", email="refresh@example.com", password="pass1234"
    )
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=True
    )
    refresh = RefreshToken.for_user(user)

    url = "/_allauth/browser/v1/auth/token/refresh"
    response = client.post(
        url, {"refresh": str(refresh)}, content_type="application/json"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["email_verified"] is True
    assert "access_token" in data["meta"]


@pytest.mark.django_db
def test_resend_verification_sends_mail(client):
    user = User.objects.create_user(
        username="resend", email="resend@example.com", password="ExtreMegeousAAA"
    )
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=False
    )

    url = "/_allauth/browser/v1/auth/resend-verification"
    response = client.post(url, {"email": user.email}, content_type="application/json")

    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["email_verified"] is False
    assert data["data"]["message"] == "Verification email sent"
    assert len(mail.outbox) == 1
    assert user.email in mail.outbox[0].to


@pytest.mark.django_db
def test_resend_verification_for_verified_email(client):
    user = User.objects.create_user(
        username="verified", email="verifiedss@example.com", password="ExtreMegeousAAA"
    )
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=True
    )

    url = "/_allauth/browser/v1/auth/resend-verification"
    response = client.post(url, {"email": user.email}, content_type="application/json")

    assert response.status_code == 409
    data = response.json()
    assert data["meta"]["email_verified"] is True
    assert data["errors"][0]["message"] == "Email already verified"


@pytest.mark.django_db
def test_resend_verification_rate_limited(client, monkeypatch):
    user = User.objects.create_user(
        username="rlresend", email="rlresend@example.com", password="pass1234"
    )
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=False
    )

    def fake_handle(request, email, raise_exception=False):
        return False

    monkeypatch.setattr(
        "authentication.jwt_views.email_verification.handle_verification_email_rate_limit",
        fake_handle,
    )

    url = "/_allauth/browser/v1/auth/resend-verification"
    response = client.post(url, {"email": user.email}, content_type="application/json")

    assert response.status_code == 429
    data = response.json()
    assert data["errors"][0]["code"] == "rate_limited"


@pytest.mark.django_db
def test_verify_email_with_valid_key(client):
    user = User.objects.create_user(
        username="verifykey", email="verifykey@example.com", password="pass1234"
    )
    email_address = EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=False
    )
    confirmation = email_address.send_confirmation(request=None, signup=False)

    url = "/_allauth/browser/v1/auth/email/verify"
    response = client.post(
        url, {"key": confirmation.key}, content_type="application/json"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["email_verified"] is True
    email_address.refresh_from_db()
    assert email_address.verified is True


@pytest.mark.django_db
def test_verify_email_invalid_key(client):
    url = "/_allauth/browser/v1/auth/email/verify"
    response = client.post(url, {"key": "invalid"}, content_type="application/json")

    assert response.status_code == 400
    data = response.json()
    assert data["errors"][0]["code"] == "invalid_key"
