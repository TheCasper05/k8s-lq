"""
Email service for sending invitation-related emails.

This service handles all email sending logic for the invitation system,
including invitation emails, acceptance notifications, revocation notifications,
and expiry reminders.
"""

import logging
from typing import Optional, Dict, Any, List

from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..models import User, Invitation
from ..enums import InvitationStatus
from ..utils.authorization import has_workspace_admin_permission

logger = logging.getLogger(__name__)

# Email configuration constants
SENDER_NAME = "LingoQuesto"
DEFAULT_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", "support@lingoquesto.com")
DEFAULT_FRONTEND_URL = getattr(
    settings, "ENDPOINT_URL_FRONTEND_ST", "http://localhost:3000"
)


def _get_inviter_name(invitation) -> str:
    """Helper function to get inviter name from invitation."""
    inviter = invitation.created_by
    if not inviter:
        return "Un administrador"

    if hasattr(inviter, "profile") and inviter.profile:
        name = f"{inviter.profile.first_name} {inviter.profile.last_name}".strip()
        if name:
            return name

    if inviter.first_name or inviter.last_name:
        name = f"{inviter.first_name} {inviter.last_name}".strip()
        if name:
            return name

    return inviter.username or "Un administrador"


def _get_user_name(user: Optional[User]) -> str:
    """Helper function to get user name from User instance."""
    if not user:
        return ""

    profile = getattr(user, "profile", None)
    if profile and (profile.first_name or profile.last_name):
        name = f"{profile.first_name} {profile.last_name}".strip()
        if name:
            return name

    if user.first_name or user.last_name:
        name = f"{user.first_name} {user.last_name}".strip()
        if name:
            return name

    return user.username or (user.email if hasattr(user, "email") else "")


def _get_email_config() -> Dict[str, str]:
    """Get email configuration (sender name, from email, reply-to)."""
    return {
        "sender_name": SENDER_NAME,
        "from_email": f"{SENDER_NAME} <{DEFAULT_FROM_EMAIL}>",
        "reply_to": DEFAULT_FROM_EMAIL,
    }


def _send_email(
    subject: str,
    to_emails: List[str],
    html_template: str,
    text_template: str,
    context: Dict[str, Any],
    error_context: str = "",
) -> Dict[str, Any]:
    """
    Generic function to send an email with HTML and text templates.

    Args:
        subject: Email subject
        to_emails: List of recipient email addresses
        html_template: Path to HTML template
        text_template: Path to text template
        context: Template context dictionary
        error_context: Additional context for error logging

    Returns:
        Dict with email sending result
    """
    try:
        config = _get_email_config()

        # Render templates
        html_content = render_to_string(html_template, context)
        text_content = render_to_string(text_template, context)

        # Create and send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=config["from_email"],
            to=to_emails,
            reply_to=[config["reply_to"]] if config["reply_to"] else None,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        return {
            "success": True,
            "email_sent_at": timezone.now(),
            "email_provider_id": None,
            "error": None,
        }

    except Exception as e:
        error_msg = f"Error sending email {error_context}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "email_sent_at": None,
            "email_provider_id": None,
            "error": str(e),
        }


def send_invitation_email(
    invitation,
    frontend_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send invitation email to the invited user.

    Args:
        invitation: Invitation instance
        frontend_url: Frontend URL for invitation links

    Returns:
        Dict with email sending result
    """
    frontend_url = frontend_url or DEFAULT_FRONTEND_URL

    # Prepare context
    inviter_name = _get_inviter_name(invitation)
    workspace_name = invitation.workspace.name
    role_display = invitation.get_role_display()
    classroom_names = [classroom.name for classroom in invitation.classrooms.all()]

    expires_at = invitation.expires_at
    days_remaining = None
    if expires_at:
        days_remaining = (expires_at - timezone.now()).days

    token = invitation.token
    context = {
        "inviter_name": inviter_name,
        "workspace_name": workspace_name,
        "role_display": role_display,
        "classroom_names": classroom_names,
        "welcome_message": invitation.welcome_message,
        "accept_url": f"{frontend_url}/invite/{token}",
        "decline_url": f"{frontend_url}/invite/{token}/decline",
        "expires_at": expires_at,
        "days_remaining": days_remaining,
    }

    subject = f"{inviter_name} te invita a {workspace_name}"

    return _send_email(
        subject=subject,
        to_emails=[invitation.email],
        html_template="authentication/emails/invitation_email.html",
        text_template="authentication/emails/invitation_email.txt",
        context=context,
        error_context=f"to {invitation.email}",
    )


def send_invitation_accepted_email(
    invitation,
    frontend_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send notification email to the inviter when an invitation is accepted.

    Args:
        invitation: Invitation instance (with status=ACCEPTED)
        frontend_url: Frontend URL for links

    Returns:
        Dict with email sending result
    """
    frontend_url = frontend_url or DEFAULT_FRONTEND_URL

    # Get inviter email
    inviter = invitation.created_by
    inviter_email = getattr(inviter, "email", None) if inviter else None

    if not inviter_email:
        return {
            "success": False,
            "email_sent_at": None,
            "email_provider_id": None,
            "error": "Inviter has no email",
        }

    # Get invited user name
    invited_email = invitation.email
    invited_name = invited_email

    try:
        invited_user = User.objects.get(email=invited_email)
        invited_name = _get_user_name(invited_user) or invited_email
    except User.DoesNotExist:
        pass

    # Prepare context
    workspace = invitation.workspace
    context = {
        "inviter_name": _get_inviter_name(invitation),
        "invited_name": invited_name,
        "invited_email": invited_email,
        "workspace_name": workspace.name,
        "role_display": invitation.get_role_display(),
        "accepted_at": invitation.accepted_at or timezone.now(),
        "members_url": f"{frontend_url}/workspace/{workspace.slug}/members",
    }

    subject = f"{invited_name} aceptó tu invitación"

    return _send_email(
        subject=subject,
        to_emails=[inviter_email],
        html_template="authentication/emails/invitation_accepted_email.html",
        text_template="authentication/emails/invitation_accepted_email.txt",
        context=context,
        error_context=f"for invitation {invitation.email}",
    )


def send_invitation_revoked_email(
    invitation,
    frontend_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send notification email to the invited user when an invitation is revoked.

    Args:
        invitation: Invitation instance (with status=REVOKED)
        frontend_url: Frontend URL for links

    Returns:
        Dict with email sending result
    """
    frontend_url = frontend_url or DEFAULT_FRONTEND_URL

    workspace_name = invitation.workspace.name
    context = {
        "workspace_name": workspace_name,
    }

    subject = f"Invitación a {workspace_name} cancelada"

    return _send_email(
        subject=subject,
        to_emails=[invitation.email],
        html_template="authentication/emails/invitation_revoked_email.html",
        text_template="authentication/emails/invitation_revoked_email.txt",
        context=context,
        error_context=f"to {invitation.email}",
    )


def resend_invitation_email(
    invitation_id: int,
    current_user: User,
    frontend_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Resend invitation email with proper validations.

    This function validates:
    1. User authentication
    2. User has admin permissions for the invitation's workspace
    3. Invitation exists and is in a valid state (PENDING, not expired)
    4. Sends the email and updates metadata with resend history

    Args:
        invitation_id: ID of the invitation to resend
        current_user: Current authenticated user performing the action
        frontend_url: Optional frontend URL for invitation links

    Returns:
        Dict with email sending result and invitation data

    Raises:
        ValidationError: If invitation doesn't exist or is in invalid state
        PermissionDenied: If user doesn't have permission to resend
    """
    # Validate invitation exists
    try:
        invitation = (
            Invitation.objects.select_related("workspace", "created_by")
            .prefetch_related("classrooms")
            .get(pk=invitation_id)
        )
    except Invitation.DoesNotExist:
        raise ValidationError(_("Invitation not found"))

    # Validate user has admin permissions for the workspace
    if not has_workspace_admin_permission(current_user, invitation.workspace):
        raise PermissionDenied(
            _("You do not have permission to resend this invitation")
        )

    # Validate invitation status - can only resend PENDING invitations
    if invitation.status != InvitationStatus.PENDING:
        raise ValidationError(
            _(
                f"Cannot resend invitation with status '{invitation.get_status_display()}'. "
                "Only pending invitations can be resent."
            )
        )

    # Validate invitation is not expired
    if invitation.expires_at and invitation.expires_at <= timezone.now():
        raise ValidationError(_("Cannot resend an expired invitation"))

    # Validate workspace is active
    if not invitation.workspace.is_active:
        raise ValidationError(_("Cannot resend invitation for an inactive workspace"))

    # Send the invitation email
    result = send_invitation_email(invitation, frontend_url)

    # Update metadata with resend information
    if not invitation.metadata:
        invitation.metadata = {}

    # Initialize resend history if it doesn't exist
    if "resend_history" not in invitation.metadata:
        invitation.metadata["resend_history"] = []

    # Add resend record to history
    resend_record = {
        "resend_at": timezone.now().isoformat(),
        "resend_by": str(current_user.id),
        "resend_by_username": current_user.username or str(current_user.id),
        "email_sent": result["success"],
        "email_sent_at": result["email_sent_at"].isoformat()
        if result["email_sent_at"]
        else None,
        "error": result["error"],
    }
    invitation.metadata["resend_history"].append(resend_record)

    # Update the original email_sent fields (for backward compatibility)
    invitation.metadata.update(
        {
            "email_sent": result["success"],
            "email_sent_at": result["email_sent_at"].isoformat()
            if result["email_sent_at"]
            else None,
            "email_provider_id": result["email_provider_id"],
            "email_error": result["error"],
            "last_resend_at": timezone.now().isoformat(),
        }
    )

    # Save metadata without triggering signals
    Invitation.objects.filter(pk=invitation.pk).update(metadata=invitation.metadata)

    return {
        "success": result["success"],
        "invitation": invitation,
        "email_result": result,
    }
