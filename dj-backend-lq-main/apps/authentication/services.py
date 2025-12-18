"""
Authentication services for user creation and onboarding.

This module provides helper functions for the complete user lifecycle:
1. User registration (email/password only)
2. Onboarding completion (profile, workspace creation)
"""

from django.db import transaction
from django.contrib.auth import get_user_model
from .models import UserProfile, Workspace, UserWorkspaceMembership
from .enums import PrimaryRole, WorkspaceType, MembershipStatus
import hashlib

User = get_user_model()


def complete_user_onboarding(
    user, first_name: str, last_name: str, primary_role: str, **profile_data
):
    """
    Complete user onboarding in a transactional manner.
    """
    if user.onboarding_completed:
        raise ValueError(f"User {user.username} has already completed onboarding")

    with transaction.atomic():
        # Create or update UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "primary_role": primary_role,
                "first_name": first_name,
                "last_name": last_name,
                "created_by": user,
                **profile_data,
            },
        )

        if not created:
            # Update existing profile
            profile.primary_role = primary_role
            profile.first_name = first_name
            profile.last_name = last_name
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.save()

        # Create personal workspace with user's full name
        full_name = f"{first_name} {last_name}".strip()
        workspace_name = f"Personal - {full_name}"
        workspace_slug = (
            f"personal-{user.id}-{hashlib.md5(str(user.id).encode()).hexdigest()[:8]}"
        )

        workspace, _ = Workspace.objects.get_or_create(
            owner_user=user,
            type=WorkspaceType.PERSONAL,
            defaults={
                "name": workspace_name,
                "slug": workspace_slug,
                "description": f"Personal workspace for {full_name}",
                "created_by": user,
            },
        )

        # Create user workspace membership
        membership, _ = UserWorkspaceMembership.objects.get_or_create(
            user=user,
            workspace=workspace,
            defaults={
                "role": primary_role,
                "status": MembershipStatus.ACTIVE,
                "created_by": user,
            },
        )

        # Mark onboarding as completed
        user.onboarding_completed = True
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        return user, profile, workspace, membership


def create_user_for_signup(email: str, password: str, username: str = None):
    """
    Create a user for initial signup (registration only).
    """
    with transaction.atomic():
        user = User.objects.create_user(
            username=username or email,
            email=email,
            password=password,
            onboarding_completed=False,
        )
        return user


def get_social_auth_data(user):
    """
    Get pre-filled data from social authentication provider (Google, Microsoft, etc.).

    """
    social_data = {}

    try:
        from allauth.socialaccount.models import SocialAccount

        social_account = SocialAccount.objects.filter(user=user).first()

        if social_account:
            extra_data = social_account.extra_data

            if "given_name" in extra_data:
                social_data["first_name"] = extra_data["given_name"]
            elif "first_name" in extra_data:
                social_data["first_name"] = extra_data["first_name"]

            if "family_name" in extra_data:
                social_data["last_name"] = extra_data["family_name"]
            elif "last_name" in extra_data:
                social_data["last_name"] = extra_data["last_name"]

            if "picture" in extra_data:
                social_data["photo"] = extra_data["picture"]
            elif "avatar_url" in extra_data:
                social_data["photo"] = extra_data["avatar_url"]

    except ImportError:
        pass

    if not social_data.get("first_name") and user.first_name:
        social_data["first_name"] = user.first_name

    if not social_data.get("last_name") and user.last_name:
        social_data["last_name"] = user.last_name

    return social_data


def create_superuser_atomically(
    username: str, email: str, password: str = None, **extra_fields
):
    """
    Create a superuser with all related objects in an atomic transaction.
    """
    with transaction.atomic():
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            onboarding_completed=False,
            **extra_fields,
        )

        complete_user_onboarding(
            user=user,
            first_name=extra_fields.get("first_name", "Admin"),
            last_name=extra_fields.get("last_name", "User"),
            primary_role=PrimaryRole.TEACHER,
        )

        return user
