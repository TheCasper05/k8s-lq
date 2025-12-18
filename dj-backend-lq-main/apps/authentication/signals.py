from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_currentuser.middleware import get_current_user
from django.contrib.auth.signals import user_logged_in
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    User,
    UserProfile,
    Workspace,
    UserWorkspaceMembership,
    Institution,
    Invitation,
)
from .enums import WorkspaceType, MembershipStatus, WorkspaceRole, InvitationStatus
from .services.email_service import (
    send_invitation_email,
    send_invitation_accepted_email,
    send_invitation_revoked_email,
)
import hashlib


@receiver(post_save, sender=UserProfile)
def on_user_profile_created(sender, instance, created, **kwargs):
    """
    Signal handler for UserProfile creation.
    When a UserProfile is created (onboarding completion), automatically create:
    - Personal Workspace
    - UserWorkspaceMembership
    - Mark user.onboarding_completed = True
    """
    if not created:
        return

    user = instance.user

    # Only proceed if onboarding is not yet completed
    if user.onboarding_completed:
        return

    # Create personal workspace with user's full name
    full_name = f"{instance.first_name} {instance.last_name}".strip()
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
    UserWorkspaceMembership.objects.get_or_create(
        user=user,
        workspace=workspace,
        defaults={
            "role": instance.primary_role,
            "status": MembershipStatus.ACTIVE,
            "created_by": user,
        },
    )

    # Mark onboarding as completed and update user's name
    # Using update to avoid triggering post_save signal on User
    update_fields = {"onboarding_completed": True}

    if instance.first_name:
        update_fields["first_name"] = instance.first_name
    if instance.last_name:
        update_fields["last_name"] = instance.last_name

    User.objects.filter(pk=user.pk).update(**update_fields)


@receiver(post_save, sender=Institution)
def on_institution_created(sender, instance, created, **kwargs):
    """
    Signal handler for Institution creation.
    When an Institution is created, automatically create:
    - Workspace of type INSTITUTION_SEDE
    - UserWorkspaceMembership for the current user with ADMIN_INSTITUCIONAL role
    """
    if not created:
        return

    # Get the current user who created the institution
    current_user = get_current_user()

    # If no current user, skip (shouldn't happen in normal flow)
    if not current_user:
        return

    # Create workspace slug based on institution slug
    workspace_slug = f"institution-{instance.slug}-{hashlib.md5(str(instance.id).encode()).hexdigest()[:8]}"
    workspace_name = f"{instance.name} - Sede Principal"

    # Create workspace of type INSTITUTION_SEDE
    workspace, _ = Workspace.objects.get_or_create(
        institution=instance,
        type=WorkspaceType.INSTITUTION_SEDE,
        defaults={
            "name": workspace_name,
            "slug": workspace_slug,
            "description": f"Workspace principal para {instance.name}",
            "created_by": current_user,
        },
    )

    # Create user workspace membership with ADMIN_INSTITUCIONAL role
    UserWorkspaceMembership.objects.get_or_create(
        user=current_user,
        workspace=workspace,
        defaults={
            "role": WorkspaceRole.ADMIN_INSTITUCIONAL,
            "status": MembershipStatus.ACTIVE,
            "created_by": current_user,
        },
    )


@receiver(post_save, sender=Invitation)
def on_invitation_created(sender, instance, created, **kwargs):
    """
    Signal handler for Invitation creation.
    When an Invitation is created, automatically send an email to the invited user with the invitation token
    """
    if not created:
        return

    # Only send email if invitation status is PENDING
    if instance.status != InvitationStatus.PENDING:
        return

    # Send invitation email
    result = send_invitation_email(instance)

    # Update invitation metadata with email sending result
    if not instance.metadata:
        instance.metadata = {}

    instance.metadata.update(
        {
            "email_sent": result["success"],
            "email_sent_at": result["email_sent_at"].isoformat()
            if result["email_sent_at"]
            else None,
            "email_provider_id": result["email_provider_id"],
            "email_error": result["error"],
        }
    )

    # Save metadata without triggering signals again
    Invitation.objects.filter(pk=instance.pk).update(metadata=instance.metadata)


@receiver(pre_save, sender=Invitation)
def on_invitation_pre_save(sender, instance, **kwargs):
    """
    Signal handler to store old status before save.
    This allows us to detect status changes in post_save.
    """
    if instance.pk:
        try:
            old_instance = Invitation.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Invitation.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Invitation)
def on_invitation_status_changed(sender, instance, created, **kwargs):
    """
    Signal handler for Invitation status changes.
    Sends emails when invitation is accepted or revoked.
    """
    if created:
        return  # Only handle updates, not creation

    # Get old status from pre_save signal
    old_status = getattr(instance, "_old_status", None)

    # Only process if status actually changed
    if old_status is None or instance.status == old_status:
        return

    # Initialize metadata if needed
    if not instance.metadata:
        instance.metadata = {}

    # Handle ACCEPTED status
    if instance.status == InvitationStatus.ACCEPTED:
        # Check if we already sent the accepted email
        if instance.metadata.get("accepted_email_sent"):
            return

        result = send_invitation_accepted_email(instance)

        instance.metadata.update(
            {
                "accepted_email_sent": result["success"],
                "accepted_email_sent_at": result["email_sent_at"].isoformat()
                if result["email_sent_at"]
                else None,
                "accepted_email_error": result["error"],
            }
        )

    # Handle REVOKED status
    elif instance.status == InvitationStatus.REVOKED:
        # Check if we already sent the revoked email
        if instance.metadata.get("revoked_email_sent"):
            return

        result = send_invitation_revoked_email(instance)

        instance.metadata.update(
            {
                "revoked_email_sent": result["success"],
                "revoked_email_sent_at": result["email_sent_at"].isoformat()
                if result["email_sent_at"]
                else None,
                "revoked_email_error": result["error"],
            }
        )

    # Save metadata without triggering signals again
    Invitation.objects.filter(pk=instance.pk).update(metadata=instance.metadata)


@receiver(user_logged_in)
def attach_jwt_on_login(sender, request, user, **kwargs):
    """
    When a user logs in via allauth (session-based), issue JWT tokens and
    store them in the session so the frontend can fetch and migrate to JWT.
    """
    if not request:
        return

    refresh = RefreshToken.for_user(user)
    request.session["jwt_tokens"] = {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }
