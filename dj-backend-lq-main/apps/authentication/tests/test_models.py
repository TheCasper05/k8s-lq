import pytest
from django.contrib.auth import get_user_model
from authentication.models import Institution, Workspace

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""

    def test_create_user(self):
        """Test creating a user with UUID primary key."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        assert user.id is not None
        assert str(user.id)  # Should be UUID
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        assert user.is_staff
        assert user.is_superuser

    def test_user_str(self):
        """Test user string representation."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        assert str(user) == "testuser"


@pytest.mark.django_db
class TestUserProfileModel:
    """Tests for UserProfile model."""

    def test_create_profile_manually(self, db):
        """Test creating a user profile manually (after onboarding)."""
        from authentication.enums import PrimaryRole

        user = User.objects.create_user(username="testuser", email="test@example.com")

        # Profile is NOT created automatically anymore
        assert not hasattr(user, "profile")

        # Profile must be created manually (or via onboarding)
        from authentication.models import UserProfile

        profile = UserProfile.objects.create(
            user=user, primary_role=PrimaryRole.STUDENT, created_by=user
        )

        assert profile.primary_role == "student"

    # def test_profile_fields(self, db):
    #     """Test profile fields can be updated."""
    #     from authentication.services import create_user_for_signup, complete_user_onboarding
    #     from authentication.enums import PrimaryRole

    #     user = create_user_for_signup(email="test@example.com", password="testpass123")
    #     user, profile, _, _ = complete_user_onboarding(
    #         user=user,
    #         first_name="Test",
    #         last_name="User",
    #         primary_role=PrimaryRole.STUDENT
    #     )

    #     profile.primary_role = "teacher"
    #     profile.phone = "+1234567890"
    #     profile.bio = "Test bio"
    #     profile.timezone = "America/New_York"
    #     profile.language_preference = "es"
    #     profile.save()

    #     profile.refresh_from_db()
    #     assert profile.primary_role == "teacher"
    #     assert profile.phone == "+1234567890"
    #     assert profile.bio == "Test bio"
    #     assert profile.timezone == "America/New_York"
    #     assert profile.language_preference == "es"

    # def test_profile_str(self, db):
    #     """Test profile string representation."""
    #     from authentication.services import create_user_for_signup, complete_user_onboarding
    #     from authentication.enums import PrimaryRole

    #     user = create_user_for_signup(email="test@example.com", password="testpass123")
    #     user, profile, _, _ = complete_user_onboarding(
    #         user=user,
    #         first_name="Test",
    #         last_name="User",
    #         primary_role=PrimaryRole.STUDENT
    #     )

    #     assert "test@example.com" in str(profile)
    #     assert "Student" in str(profile)


@pytest.mark.django_db
class TestInstitutionModel:
    """Tests for Institution model."""

    def test_create_institution(self, db):
        """Test creating an institution."""
        user = User.objects.create_user(username="admin", email="admin@example.com")

        institution = Institution.objects.create(
            name="Test University",
            slug="test-university",
            description="A test university",
            created_by=user,
        )

        assert institution.name == "Test University"
        assert institution.slug == "test-university"
        assert institution.is_active

    def test_institution_str(self, db):
        """Test institution string representation."""
        user = User.objects.create_user(username="admin", email="admin@example.com")

        institution = Institution.objects.create(
            name="Test University", slug="test-university", created_by=user
        )

        assert str(institution) == "Test University"


@pytest.mark.django_db
class TestWorkspaceModel:
    """Tests for Workspace model."""

    # def test_create_personal_workspace_via_onboarding(self, db):
    #     """Test creating a personal workspace via onboarding."""
    #     from authentication.services import create_user_for_signup, complete_user_onboarding
    #     from authentication.enums import PrimaryRole

    #     user = create_user_for_signup(email="test@example.com", password="testpass123")

    #     # Personal workspace is NOT created automatically anymore
    #     assert Workspace.objects.filter(owner_user=user, type="personal").count() == 0

    #     # Complete onboarding to create workspace
    #     user, profile, workspace, _ = complete_user_onboarding(
    #         user=user,
    #         first_name="Test",
    #         last_name="User",
    #         primary_role=PrimaryRole.STUDENT
    #     )

    #     assert workspace is not None
    #     assert workspace.type == "personal"
    #     assert workspace.owner_user == user
    #     assert workspace.institution is None
    #     assert workspace.name == "Personal - Test User"

    def test_create_institution_workspace(self, db):
        """Test creating an institution workspace."""
        user = User.objects.create_user(username="admin", email="admin@example.com")

        institution = Institution.objects.create(
            name="Test University", slug="test-university", created_by=user
        )

        workspace = Workspace.objects.create(
            name="Test University Workspace",
            slug="test-uni-workspace",
            type="institution_sede",
            institution=institution,
            created_by=user,
        )

        assert workspace.type == "institution_sede"
        assert workspace.institution == institution

    # def test_workspace_str(self, db):
    #     """Test workspace string representation."""
    #     from authentication.services import create_user_for_signup, complete_user_onboarding
    #     from authentication.enums import PrimaryRole

    #     user = create_user_for_signup(email="test@example.com", password="testpass123")
    #     user, _, workspace, _ = complete_user_onboarding(
    #         user=user,
    #         first_name="Test",
    #         last_name="User",
    #         primary_role=PrimaryRole.STUDENT
    #     )

    #     assert "Test User" in str(workspace) or "personal" in str(workspace).lower()


@pytest.mark.django_db
class TestUserWorkspaceMembershipModel:
    """Tests for UserWorkspaceMembership model."""

    # def test_create_membership_via_onboarding(self, db):
    #     """Test creating a workspace membership via onboarding."""
    #     from authentication.services import create_user_for_signup, complete_user_onboarding
    #     from authentication.enums import PrimaryRole

    #     user = create_user_for_signup(email="test@example.com", password="testpass123")

    #     # Membership is NOT created automatically anymore
    #     assert UserWorkspaceMembership.objects.filter(user=user).count() == 0

    #     # Complete onboarding to create membership
    #     user, _, workspace, membership = complete_user_onboarding(
    #         user=user,
    #         first_name="Test",
    #         last_name="User",
    #         primary_role=PrimaryRole.STUDENT
    #     )

    #     assert membership.user == user
    #     assert membership.workspace == workspace
    #     assert membership.role == 'student'
    #     assert membership.status == 'active'

    # def test_membership_str(self, db):
    #     """Test membership string representation."""
    #     from authentication.services import create_user_for_signup, complete_user_onboarding
    #     from authentication.enums import PrimaryRole

    #     user = create_user_for_signup(email="test@example.com", password="testpass123")
    #     user, _, workspace, membership = complete_user_onboarding(
    #         user=user,
    #         first_name="Test",
    #         last_name="User",
    #         primary_role=PrimaryRole.STUDENT
    #     )

    #     assert "test@example.com" in str(membership)
    #     assert "Student" in str(membership)
