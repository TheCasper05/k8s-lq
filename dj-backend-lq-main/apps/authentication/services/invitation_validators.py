"""
Invitation validation service.

This module contains all validation logic for Invitation model,
separated from the model to keep it clean and maintainable.

The validation is organized in three layers:
1. InvitationValidator: Coordinator that orchestrates all validations
2. GeneralInvitationValidator: Context-independent validations (always execute)
3. ContextualInvitationValidator: Context-dependent validations (user, old_object)
"""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_currentuser.middleware import get_current_user

from ..enums import PrimaryRole, InvitationStatus
from .license_service import get_license_service
from ..utils.authorization import has_workspace_admin_permission

# Services can import models directly - this is the natural Django way
# Models should NOT import services at module level to avoid circular dependencies
from ..models import Invitation, User, UserWorkspaceMembership


class GeneralInvitationValidator:
    """
    Handles context-independent validations.

    These validations always execute regardless of user or system context.
    They validate business rules that apply universally to all invitations.
    """

    def __init__(self, license_service=None):
        """
        Initialize the general validator.

        Args:
            license_service: Optional license service instance.
                           If None, will use get_license_service().
        """
        self.license_service = license_service or get_license_service()

    def validate(self, invitation: Invitation) -> None:
        """
        Execute all general validations.

        Args:
            invitation: The Invitation instance to validate

        Raises:
            ValidationError: If any validation fails
        """
        self._set_default_expiration(invitation)
        self._validate_expiration_date(invitation)
        self._validate_creator_permissions(invitation)
        self._validate_workspace_is_active(invitation)
        self._validate_no_duplicate_invitation(invitation)
        self._validate_classrooms_belong_to_workspace(invitation)
        self._validate_license_availability(invitation)

    def _set_default_expiration(self, invitation: Invitation) -> None:
        """Set default expiration date if not provided."""
        if invitation.expires_at is None:
            invitation.expires_at = timezone.now() + timedelta(days=7)

    def _validate_expiration_date(self, invitation: Invitation) -> None:
        """Validate that expiration date is in the future."""
        if invitation.expires_at and invitation.expires_at <= timezone.now():
            raise ValidationError(_("Expiration date must be in the future"))

    def _validate_creator_permissions(self, invitation: Invitation) -> None:
        """
        Validate that the creator has permission to create invitations.

        Business rule: Students cannot create invitations.
        """
        if invitation.created_by and hasattr(invitation.created_by, "profile"):
            if invitation.created_by.profile.primary_role == PrimaryRole.STUDENT:
                raise ValidationError(_("A student cannot create invitations"))

    def _validate_workspace_is_active(self, invitation: Invitation) -> None:
        """
        Validate that the workspace is active.

        Business rule: Cannot create invitations to inactive workspaces.
        """
        if not invitation.workspace.is_active:
            raise ValidationError(
                _("Cannot create invitation for an inactive workspace.")
            )

    def _validate_no_duplicate_invitation(self, invitation: Invitation) -> None:
        """
        Validate that there are no duplicate invitations or existing memberships.

        Business rules:
        1. Cannot invite the same email to a workspace if there's a PENDING invitation
        2. Cannot invite a user who is already a member of the workspace
        """

        # Only validate when creating new invitations
        if not invitation._state.adding:
            return

        # Check for existing PENDING invitation
        existing_pending = Invitation.objects.filter(
            email=invitation.email,
            workspace=invitation.workspace,
            status=InvitationStatus.PENDING,
        ).exists()

        if existing_pending:
            raise ValidationError(
                _(
                    "An active invitation already exists for this email in this workspace."
                )
            )

        # Check if user is already a member of the workspace
        try:
            user = User.objects.get(email=invitation.email)
            is_member = UserWorkspaceMembership.objects.filter(
                user=user,
                workspace=invitation.workspace,
                status="active",  # Using MembershipStatus.ACTIVE
            ).exists()

            if is_member:
                raise ValidationError(
                    _("This user is already a member of the workspace.")
                )
        except User.DoesNotExist:
            # User doesn't exist yet, which is fine for invitations
            pass

    def _validate_classrooms_belong_to_workspace(self, invitation: Invitation) -> None:
        """
        Validate that all assigned classrooms belong to the invitation's workspace.

        Business rule: If the invitation includes classrooms, they must all
        belong to the same workspace as the invitation.

        Note: This validation only runs if classrooms are already assigned.
        For new invitations, classrooms are typically assigned after save().
        """
        # Skip if invitation doesn't have a pk yet (not saved)
        if not invitation.pk:
            return

        # Check if there are any classrooms assigned
        if not invitation.classrooms.exists():
            return

        # Validate all classrooms belong to the invitation's workspace
        invalid_classrooms = invitation.classrooms.exclude(
            workspace=invitation.workspace
        )

        if invalid_classrooms.exists():
            classroom_names = ", ".join(
                invalid_classrooms.values_list("name", flat=True)
            )
            raise ValidationError(
                _(
                    f"The following classrooms do not belong to the invitation's workspace: {classroom_names}"
                )
            )

    def _validate_license_availability(self, invitation: Invitation) -> None:
        """
        Validate license availability before creating an invitation.

        This is an extension point that calls the license service
        to check if the creator has available licenses.

        Args:
            invitation: The Invitation instance being validated

        Raises:
            ValidationError: If license check fails
        """
        # Only validate licenses when creating a new invitation
        if not invitation._state.adding:
            return

        # Only validate if there's a creator
        if not invitation.created_by:
            return

        # Check license availability through the service
        try:
            can_invite = self.license_service.check_availability(
                user=invitation.created_by,
                workspace=invitation.workspace,
                role=invitation.role,
            )

            if not can_invite:
                raise ValidationError(
                    _(
                        "You do not have available licenses to invite more users to this workspace."
                    )
                )
        except Exception as e:
            # If license service raises an error, we log it but don't break
            # the invitation flow. This allows the system to work even if
            # license service is not fully implemented yet.
            # In production, you might want to log this properly.
            if isinstance(e, ValidationError):
                raise
            # For other exceptions, we silently pass (license service not ready)
            pass


class ContextualInvitationValidator:
    """
    Handles context-dependent validations.

    These validations depend on the current user, old object state,
    and other contextual information. They only execute when updating
    existing invitations.
    """

    def validate(
        self, invitation: Invitation, current_user: Optional[User] = None
    ) -> None:
        """
        Execute all contextual validations.

        Args:
            invitation: The Invitation instance to validate
            current_user: The current user performing the action.
                         If None, will use get_current_user()

        Raises:
            ValidationError: If any validation fails
        """
        if current_user is None:
            current_user = get_current_user()

        # Validations that run on creation
        if invitation._state.adding:
            self._validate_creator_membership_in_workspace(invitation, current_user)
            self._validate_creator_membership_in_classroom_workspaces(
                invitation, current_user
            )
        else:
            # Validations that run on updates
            self._validate_update_permissions(invitation, current_user)
            self._update_status_timestamps(invitation, current_user)

    def _validate_creator_membership_in_workspace(
        self, invitation: Invitation, current_user: Optional[User]
    ) -> None:
        """
        Validate that the creator is a member of the workspace with appropriate role.

        Business rule: Can only invite to workspaces where the creator is a member
        with one of these roles: ADMIN_INSTITUCIONAL, COORDINATOR, ADMIN_SEDE, or TEACHER.

        Args:
            invitation: The invitation being created
            current_user: The user creating the invitation
        """

        # Skip if no current user
        if not current_user:
            return

        # Check if creator is a member with appropriate role (including TEACHER)
        has_permission = has_workspace_admin_permission(
            current_user, invitation.workspace, include_teacher=True
        )

        if not has_permission:
            raise ValidationError(
                _(
                    "You can only invite users to workspaces where you are a member "
                    "with Admin, Coordinator, or Teacher role."
                )
            )

    def _validate_creator_membership_in_classroom_workspaces(
        self, invitation: Invitation, current_user: Optional[User]
    ) -> None:
        """
        Validate creator permissions for classroom-based invitations.

        Business rules:
        1. If invitation has classrooms, creator must have appropriate role in
           the workspace of each classroom
        2. All classrooms must belong to the invitation's workspace

        Args:
            invitation: The invitation being created
            current_user: The user creating the invitation

        Note: This validation only runs if classrooms are already assigned.
        For new invitations created via API, classrooms might be provided upfront.
        """
        # Skip if no current user
        if not current_user:
            return

        # For new invitations, we can't check classrooms via the relation
        # since they haven't been saved yet. This validation will be
        # handled by _validate_classrooms_belong_to_workspace in GeneralValidator
        # after the invitation is saved and classrooms are assigned.
        if not invitation.pk:
            return

        # Check if there are any classrooms assigned
        if not invitation.classrooms.exists():
            return

        # Get all unique workspaces from the assigned classrooms
        classroom_workspaces = set(
            invitation.classrooms.values_list("workspace", flat=True)
        )

        # Verify all classrooms belong to the invitation's workspace
        if len(classroom_workspaces) > 1 or (
            classroom_workspaces and invitation.workspace.pk not in classroom_workspaces
        ):
            raise ValidationError(
                _("All classrooms must belong to the invitation's workspace.")
            )

        # Verify creator has appropriate role in the workspace (including TEACHER)
        has_permission = has_workspace_admin_permission(
            current_user, invitation.workspace, include_teacher=True
        )

        if not has_permission:
            raise ValidationError(
                _(
                    "You can only invite users to classrooms in workspaces where you "
                    "have Admin, Coordinator, or Teacher role."
                )
            )

    def _validate_update_permissions(
        self, invitation: Invitation, current_user: Optional[User]
    ) -> None:
        """
        Validate that the current user has permission to update the invitation.

        This includes:
        - Checking if invitation is expired (cannot be modified)
        - Validating user permissions based on their role
        - Ensuring only allowed status changes

        Args:
            invitation: The invitation being updated
            current_user: The user attempting the update
        """

        try:
            old = Invitation.objects.get(pk=invitation.pk)
            old_status = old.status

            # Expired invitations cannot be modified
            if old_status == InvitationStatus.EXPIRED:
                raise ValidationError(_("An expired invitation cannot be modified."))

            # If no current user, skip permission checks
            if not current_user:
                return

            is_creator = current_user == invitation.created_by
            is_invited_user = (
                hasattr(current_user, "email")
                and current_user.email == invitation.email
            )

            # Check for field changes
            changed_fields = self._get_changed_fields(invitation, old)
            status_changed = invitation.status != old_status
            allowed_status = [InvitationStatus.ACCEPTED, InvitationStatus.DECLINED]

            # Invited user can only accept or decline
            if is_invited_user and status_changed:
                if invitation.status not in allowed_status:
                    raise ValidationError(
                        _("You can only accept or decline the invitation.")
                    )
                if changed_fields:
                    raise ValidationError(
                        _(
                            "You can only accept or decline the invitation; no other fields can be changed."
                        )
                    )

            # Creator cannot accept or decline (only invited user can)
            elif is_creator:
                if status_changed and invitation.status in allowed_status:
                    raise ValidationError(
                        _("Only the invited user can accept or decline the invitation.")
                    )

            # Other users don't have permission
            elif not is_creator and not is_invited_user:
                raise ValidationError(
                    _("You do not have permission to update this invitation.")
                )

        except Invitation.DoesNotExist:
            # New instance, no old version to compare
            pass

    def _get_changed_fields(self, invitation: Invitation, old: Invitation) -> list[str]:
        """
        Get list of fields that have changed.

        Args:
            invitation: The new invitation state
            old: The old invitation state

        Returns:
            List of field names that have changed
        """
        changed_fields = []
        for field in ["workspace", "role", "expires_at", "welcome_message", "metadata"]:
            if getattr(invitation, field) != getattr(old, field):
                changed_fields.append(field)
        return changed_fields

    def _update_status_timestamps(
        self, invitation: Invitation, current_user: Optional[User]
    ) -> None:
        """
        Update timestamp fields based on status changes.

        This method automatically sets accepted_at, declined_at, revoked_at
        and revoked_by fields when the status changes.

        Args:
            invitation: The invitation being updated
            current_user: The user performing the update
        """

        try:
            old = Invitation.objects.get(pk=invitation.pk)
            old_status = old.status

            if invitation.status != old_status:
                current_time = timezone.now()

                if invitation.status == InvitationStatus.ACCEPTED:
                    invitation.accepted_at = current_time
                    invitation.declined_at = None
                    invitation.revoked_at = None
                    invitation.revoked_by = None

                elif invitation.status == InvitationStatus.DECLINED:
                    invitation.declined_at = current_time
                    invitation.accepted_at = None
                    invitation.revoked_at = None
                    invitation.revoked_by = None

                elif invitation.status == InvitationStatus.REVOKED:
                    invitation.revoked_at = current_time
                    invitation.revoked_by = current_user
                    invitation.accepted_at = None
                    invitation.declined_at = None

                elif invitation.status in [
                    InvitationStatus.PENDING,
                    InvitationStatus.EXPIRED,
                ]:
                    invitation.accepted_at = None
                    invitation.declined_at = None
                    invitation.revoked_at = None
                    invitation.revoked_by = None

        except Exception as e:
            if isinstance(e, Invitation.DoesNotExist):
                # New instance, no timestamps to update
                pass
            else:
                raise


class InvitationValidator:
    """
    Main coordinator for invitation validation.

    This class orchestrates both general and contextual validations,
    providing a single entry point for validating invitations.
    """

    def __init__(self, license_service=None):
        """
        Initialize the validator with its sub-validators.

        Args:
            license_service: Optional license service instance.
                           If None, will use get_license_service().
        """
        self.general_validator = GeneralInvitationValidator(license_service)
        self.contextual_validator = ContextualInvitationValidator()

    def validate(self, invitation: Invitation) -> None:
        """
        Validate an invitation instance.

        This method coordinates all validation checks through the
        specialized validators and raises ValidationError if any validation fails.

        Args:
            invitation: The Invitation instance to validate

        Raises:
            ValidationError: If any validation fails
        """
        # Execute general validations (always run)
        self.general_validator.validate(invitation)

        # Execute contextual validations (only for updates)
        self.contextual_validator.validate(invitation)
