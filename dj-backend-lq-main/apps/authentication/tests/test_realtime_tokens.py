"""
Unit tests for realtime JWT token generation.

Tests cover:
- Token generation with RSA signing
- Endpoint authentication and authorization
- Workspace access validation
- Rate limiting
- Error handling
"""

import uuid
from datetime import datetime

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import (
    UserProfile,
    Workspace,
    UserWorkspaceMembership,
    WorkspaceType,
    WorkspaceRole,
    MembershipStatus,
    PrimaryRole,
)
from authentication.jwt_views.realtime_utils import (
    generate_realtime_token,
    decode_realtime_token,
    MissingRealtimeConfigError,
    get_realtime_jwt_config,
)
from django.contrib.auth import get_user_model

User = get_user_model()

# Test RSA key pair (for testing only - not for production use)
# These are real valid RSA keys generated for testing purposes
TEST_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC6zX5X2CKYdeg4
WoP/VkbjMeNIbEYSzC9/E/UAwul0xqBi6DbkIharrVKfhqJvAHNX7qh72leThXfB
8O9z12wtXROVx5w3gaLZKFOteq1VY5j4y0AQ2pjj7lsx9yUdH99ga03xZ/hPwjFN
J0QuXEGjoQjM8pKJTfcBufZ4Q4Iszq6XHw69eZTpVV7C59FbxCMrmoNyxo8/PnwA
7ilrkFQnGPEd+1fepS94+ZznjVgxtqwU0rqhUxAp/jJPvRx/7XoW/Pt7pyoX6VSk
DjEJKonu+AwppONgIcfgB7xaXl7ocOcqTjdh3KfwpxLYQKzP9iFkMDIkO0hNKiaP
wPwLgagBAgMBAAECggEADa4PPfpupic6uo3EzUX4BDSOExEWAwbMktjXGcqSwC65
MvHgiADUrWPdZ7m7Wx4RIScxukg5UgaPLtCPKJ0yp3ibS5FS2yz1Zd1lkcNb8daz
LpBSTVzebERZwPH7CzcsHtDpsO+CDsBttEG9seUNslPDsKAyPQRM139TEZsxnq6w
FtxGRWcbuG+l32nN5WHcSwMFbDWV27NHYIbhv4ZhE5qc3uwWD7vKAStddlwlK5mC
zGN6uiqhk1XWG577dleDFSVkaD018UIzhPyiuHmgIGyNHe0uWPRw1f0KLGIH8mMV
L3PdQh0JE22GRf5TYvIfxnoV2ejw7E29EF8oZnhLNQKBgQDdFQL51VHHcoSJqXLb
/NYILtMEGPWTZYvGUgJfFpQQfCwTX+e5GBQi9kEbA1sdMuZSufLIdwXwRNN2sekZ
xqlkMdVcicYoT2AVsZObyzT5E7CakO6lZUgRx6CRP/JpmHAT2w7cR2XMUu9VLhAy
UCqD+CBOBezaiajEob1Fvek5SwKBgQDYTnfEH+hVA8NXnoEKHDGDMwJiC1Idx91T
AQTS+72koUmLuD5Yr5MJUrdis8CetkyT+Get7iWJ6mIIkolfdDlaKtAU7mZ0Nxzp
3B8AzTOL/UNfKHf4E24dRlBk7Cz6ZnJ2YlG4YrP2+eOlHIdvOCSnfh6o0LJzPqHW
GS/N8SGAYwKBgAlrI71RATLmBg93UJVeqB+hHwxFo/CrmtDQHZm/dH9fSuFobI7O
H819gDiOZAtSZ82ObnFr4Kzjwb6ExdF7TSwfk19l3zNIbmd+MTOp7I/P7u4mzoPt
VKytPIHzn3gwLlYqNu/betLBlcCjPb1m/OiyYW3xgq2sv6vg2Bdoh88RAoGAC3nW
RtR+igwiEAL7y6KFSfWp2bPKDoRtDJtQOzVZ8WMRONV0kVX3UhZOXnE09fasB2m1
bnflC/UgcF395c+Pv2XoFkQzsVS/NvUTvAInCvVL3r+R5dp6DBmP6FrTZBGNXxSG
S2cJL0BAwKDL2q263BwH2mMAJLcc9PPvIlj5swsCgYATeJ4t38Z3rlwTk2k99ng7
YlyVRyPSZz8ggyxM5UoLmoinwJnkbguGVClQ4izJW4FfeH2TyqMmd+WvkO1h4oKz
KJGfHK1ni+eETZTIYfde4hpCafkhz0d+9clF3go0W8eepuJyd7ttF7HU3rvgs6tE
IyFuallERZWbJ6udWaxVfA==
-----END PRIVATE KEY-----"""

TEST_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAus1+V9gimHXoOFqD/1ZG
4zHjSGxGEswvfxP1AMLpdMagYug25CIWq61Sn4aibwBzV+6oe9pXk4V3wfDvc9ds
LV0TlcecN4Gi2ShTrXqtVWOY+MtAENqY4+5bMfclHR/fYGtN8Wf4T8IxTSdELlxB
o6EIzPKSiU33Abn2eEOCLM6ulx8OvXmU6VVewufRW8QjK5qDcsaPPz58AO4pa5BU
JxjxHftX3qUvePmc541YMbasFNK6oVMQKf4yT70cf+16Fvz7e6cqF+lUpA4xCSqJ
7vgMKaTjYCHH4Ae8Wl5e6HDnKk43Ydyn8KcS2ECsz/YhZDAyJDtITSomj8D8C4Go
AQIDAQAB
-----END PUBLIC KEY-----"""


@override_settings(
    REALTIME_JWT_PRIVATE_KEY=TEST_PRIVATE_KEY,
    REALTIME_JWT_PUBLIC_KEY=TEST_PUBLIC_KEY,
    REALTIME_JWT_ALGORITHM="RS256",
    REALTIME_JWT_EXPIRATION_MINUTES=10,
)
class RealtimeTokenUtilsTestCase(TestCase):
    """Test realtime JWT utility functions."""

    def test_generate_token_basic(self):
        """Test basic token generation."""
        user_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())

        token = generate_realtime_token(user_id=user_id, tenant_id=tenant_id)

        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_generate_token_with_session_id(self):
        """Test token generation with session ID."""
        user_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())
        session_id = "test-session-123"

        token = generate_realtime_token(
            user_id=user_id, tenant_id=tenant_id, session_id=session_id
        )

        # Decode without verification to check payload
        payload = decode_realtime_token(token, verify=False)

        self.assertEqual(payload["sub"], user_id)
        self.assertEqual(payload["tenant_id"], tenant_id)
        self.assertEqual(payload["session_id"], session_id)
        self.assertEqual(payload["scope"], "realtime")
        self.assertIn("jti", payload)
        self.assertIn("exp", payload)
        self.assertIn("iat", payload)

    def test_token_expiration_custom(self):
        """Test token with custom expiration."""
        user_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())

        token = generate_realtime_token(
            user_id=user_id, tenant_id=tenant_id, expiration_minutes=5
        )

        payload = decode_realtime_token(token, verify=False)
        exp_time = datetime.utcfromtimestamp(payload["exp"])
        iat_time = datetime.utcfromtimestamp(payload["iat"])

        # Check that expiration is approximately 5 minutes from issue time
        diff = exp_time - iat_time
        self.assertAlmostEqual(diff.total_seconds(), 5 * 60, delta=2)

    # def test_decode_token_with_verification(self):
    #     """Test token decoding with signature verification."""
    #     user_id = str(uuid.uuid4())
    #     tenant_id = str(uuid.uuid4())

    #     token = generate_realtime_token(user_id=user_id, tenant_id=tenant_id)

    #     # This should work with the matching public key
    #     payload = decode_realtime_token(token, verify=True)
    #     self.assertEqual(payload["sub"], user_id)
    #     self.assertEqual(payload["tenant_id"], tenant_id)

    @override_settings(REALTIME_JWT_PRIVATE_KEY=None)
    def test_missing_private_key(self):
        """Test error when private key is missing."""
        with self.assertRaises(MissingRealtimeConfigError):
            generate_realtime_token(
                user_id=str(uuid.uuid4()), tenant_id=str(uuid.uuid4())
            )

    def test_get_config(self):
        """Test getting JWT configuration."""
        private_key, algorithm, expiration = get_realtime_jwt_config()

        self.assertEqual(private_key, TEST_PRIVATE_KEY)
        self.assertEqual(algorithm, "RS256")
        self.assertEqual(expiration, 10)


@override_settings(
    REALTIME_JWT_PRIVATE_KEY=TEST_PRIVATE_KEY,
    REALTIME_JWT_PUBLIC_KEY=TEST_PUBLIC_KEY,
    REALTIME_JWT_ALGORITHM="RS256",
    REALTIME_JWT_EXPIRATION_MINUTES=10,
)
class RealtimeTokenViewTestCase(TestCase):
    """Test realtime token endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create user profile
        self.profile = UserProfile.objects.create(
            user=self.user,
            primary_role=PrimaryRole.TEACHER,
            first_name="Test",
            last_name="User",
        )

        # Create workspace
        self.workspace = Workspace.objects.create(
            name="Test Workspace",
            type=WorkspaceType.PERSONAL,
            slug="test-workspace",
            owner_user=self.user,
        )

        # Create membership
        self.membership = UserWorkspaceMembership.objects.create(
            user=self.user,
            workspace=self.workspace,
            role=WorkspaceRole.ADMIN_INSTITUCIONAL,
            status=MembershipStatus.ACTIVE,
        )

        self.url = reverse("realtime_token")

    def test_unauthenticated_request(self):
        """Test that unauthenticated requests are rejected."""
        response = self.client.post(
            self.url, {"workspace_id": str(self.workspace.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_request_success(self):
        """Test successful token generation for authenticated user."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, {"workspace_id": str(self.workspace.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("realtime_token", response.data)
        self.assertIn("expires_in", response.data)
        self.assertIn("token_type", response.data)

        # Verify token structure
        token = response.data["realtime_token"]
        payload = decode_realtime_token(token, verify=False)

        self.assertEqual(payload["sub"], str(self.user.id))
        self.assertEqual(payload["tenant_id"], str(self.workspace.id))
        self.assertEqual(payload["scope"], "realtime")

    def test_missing_workspace_id(self):
        """Test error when workspace_id is not provided."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "workspace_id_required")

    def test_workspace_access_denied(self):
        """Test error when user doesn't have access to workspace."""
        # Create another workspace that the user doesn't have access to
        other_workspace = Workspace.objects.create(
            name="Other Workspace", type=WorkspaceType.SHARED, slug="other-workspace"
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, {"workspace_id": str(other_workspace.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "workspace_access_denied")

    def test_inactive_membership(self):
        """Test error when user's membership is not active."""
        # Update membership status to inactive
        self.membership.status = MembershipStatus.INVITED
        self.membership.save()

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, {"workspace_id": str(self.workspace.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_nonexistent_workspace(self):
    #     """Test error when workspace doesn't exist."""
    #     self.client.force_authenticate(user=self.user)

    #     fake_workspace_id = str(uuid.uuid4())
    #     response = self.client.post(self.url, {"workspace_id": fake_workspace_id}, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(REALTIME_JWT_PRIVATE_KEY=None)
    def test_missing_configuration(self):
        """Test error when JWT configuration is missing."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, {"workspace_id": str(self.workspace.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "configuration_error")

    def test_token_expiration_value(self):
        """Test that expires_in value is correct."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, {"workspace_id": str(self.workspace.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Default is 10 minutes = 600 seconds
        self.assertEqual(response.data["expires_in"], 600)

    def test_token_type(self):
        """Test that token type is Bearer."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, {"workspace_id": str(self.workspace.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["token_type"], "Bearer")

    # def test_multiple_workspaces(self):
    #     """Test user can get tokens for different workspaces."""
    #     # Create second workspace with membership
    #     workspace2 = Workspace.objects.create(
    #         name="Second Workspace", type=WorkspaceType.SHARED, slug="second-workspace"
    #     )
    #     UserWorkspaceMembership.objects.create(
    #         user=self.user,
    #         workspace=workspace2,
    #         role=WorkspaceRole.TEACHER,
    #         status=MembershipStatus.ACTIVE,
    #     )

    #     self.client.force_authenticate(user=self.user)

    #     # Get token for first workspace
    #     response1 = self.client.post(self.url, {"workspace_id": str(self.workspace.id)}, format='json')
    #     self.assertEqual(response1.status_code, status.HTTP_200_OK)
    #     token1 = response1.data["realtime_token"]

    #     # Get token for second workspace
    #     response2 = self.client.post(self.url, {"workspace_id": str(workspace2.id)}, format='json')
    #     self.assertEqual(response2.status_code, status.HTTP_200_OK)
    #     token2 = response2.data["realtime_token"]

    #     # Tokens should be different
    #     self.assertNotEqual(token1, token2)

    #     # Verify tenant_ids are different
    #     payload1 = decode_realtime_token(token1, verify=False)
    #     payload2 = decode_realtime_token(token2, verify=False)

    #     self.assertEqual(payload1["tenant_id"], str(self.workspace.id))
    #     self.assertEqual(payload2["tenant_id"], str(workspace2.id))
