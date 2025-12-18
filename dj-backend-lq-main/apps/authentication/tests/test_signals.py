import pytest
from django.contrib.auth import get_user_model
from authentication.models import UserProfile, Workspace, UserWorkspaceMembership
from authentication.enums import PrimaryRole

User = get_user_model()


@pytest.mark.django_db
class TestUserProfileSignal:
    """Tests for UserProfile post_save signal that creates workspace and membership."""

    def test_signal_creates_workspace_and_membership_on_profile_creation(self):
        """Test that creating a UserProfile triggers signal to create Workspace and Membership."""
        # Create user first
        user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123",
            onboarding_completed=False,
        )

        # Verify no workspace or membership exists yet
        assert Workspace.objects.filter(owner_user=user).count() == 0
        assert UserWorkspaceMembership.objects.filter(user=user).count() == 0
        assert user.onboarding_completed is False

        # Create UserProfile - this should trigger the signal
        UserProfile.objects.create(
            user=user,
            primary_role=PrimaryRole.STUDENT,
            first_name="John",
            last_name="Doe",
            created_by=user,
        )

        # Refresh user from database
        user.refresh_from_db()

        # Verify signal created workspace
        workspace = Workspace.objects.filter(owner_user=user, type="personal").first()
        assert workspace is not None
        assert workspace.name == "Personal - John Doe"
        assert workspace.type == "personal"

        # Verify signal created membership
        membership = UserWorkspaceMembership.objects.filter(user=user).first()
        assert membership is not None
        assert membership.workspace == workspace
        assert membership.role == PrimaryRole.STUDENT
        assert membership.status == "active"

        # Verify signal marked onboarding as completed
        assert user.onboarding_completed is True
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_signal_does_not_run_on_profile_update(self):
        """Test that updating a UserProfile does not trigger workspace creation again."""
        # Create user and profile
        user = User.objects.create_user(
            username="update@example.com",
            email="update@example.com",
            password="testpass123",
        )

        profile = UserProfile.objects.create(
            user=user,
            primary_role=PrimaryRole.STUDENT,
            first_name="Jane",
            last_name="Smith",
            created_by=user,
        )

        # Count workspaces and memberships
        workspace_count = Workspace.objects.filter(owner_user=user).count()
        membership_count = UserWorkspaceMembership.objects.filter(user=user).count()

        assert workspace_count == 1
        assert membership_count == 1

        # Update profile
        profile.bio = "Updated bio"
        profile.save()

        # Verify counts haven't changed
        assert Workspace.objects.filter(owner_user=user).count() == workspace_count
        assert (
            UserWorkspaceMembership.objects.filter(user=user).count()
            == membership_count
        )

    def test_signal_does_not_run_if_onboarding_already_completed(self):
        """Test that signal doesn't run if user already completed onboarding."""
        # Create user with onboarding already completed
        user = User.objects.create_user(
            username="completed@example.com",
            email="completed@example.com",
            password="testpass123",
            onboarding_completed=True,
        )

        # Create workspace manually
        Workspace.objects.create(
            owner_user=user,
            type="personal",
            name="Existing Workspace",
            slug=f"existing-{user.id}",
            created_by=user,
        )

        # Create profile - signal should NOT create new workspace
        UserProfile.objects.create(
            user=user,
            primary_role=PrimaryRole.TEACHER,
            first_name="Already",
            last_name="Onboarded",
            created_by=user,
        )

        # Verify only one workspace exists (the manually created one)
        workspaces = Workspace.objects.filter(owner_user=user)
        assert workspaces.count() == 1
        assert workspaces.first().name == "Existing Workspace"
