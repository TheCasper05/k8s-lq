import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import AuditModel
from .enums import (
    PrimaryRole,
    WorkspaceType,
    WorkspaceRole,
    MembershipStatus,
    DocumentType,
    InvitationStatus,
    ClassroomRole,
)
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model with UUID as primary key.
    Extends Django's AbstractUser to add UUID primary key.
    This model is designed to work with django-allauth for authentication.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("User ID")
    )
    onboarding_completed = models.BooleanField(
        default=False,
        verbose_name=_("Onboarding Completed"),
        help_text=_("Indicates whether the user has completed the onboarding process"),
    )

    class Meta:
        db_table = "user"


class Language(AuditModel):
    """
    Language model for reference data.
    Based on languages table from the schema.
    """

    code = models.CharField(
        max_length=10,
        unique=True,
        help_text=_("Language code (e.g., 'en', 'es', 'fr')"),
    )
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    native_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "language"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"], name="idx_languages_code"),
            models.Index(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="idx_languages_active",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class UserProfile(AuditModel):
    """
    Extended profile for users with additional information.
    Based on user_profiles table from the schema.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name=_("User")
    )
    primary_role = models.CharField(
        max_length=20, choices=PrimaryRole.choices, verbose_name=_("Primary Role")
    )

    # Profile data
    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name=_("Phone")
    )
    photo = models.TextField(blank=True, null=True, verbose_name=_("Photo URL"))
    bio = models.TextField(blank=True, null=True, verbose_name=_("Bio"))
    timezone = models.CharField(
        max_length=50, default="UTC", verbose_name=_("Timezone")
    )
    language_preference = models.CharField(
        max_length=10, default="en", verbose_name=_("Language Preference")
    )
    first_name = models.CharField(max_length=30, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=30, verbose_name=_("Last Name"))
    birthday = models.DateField(blank=True, null=True, verbose_name=_("Birthday"))
    country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text=_("ISO 3166-1 alpha-2 country code (2 uppercase letters)"),
        verbose_name=_("Country"),
    )

    # Document info (optional)
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        blank=True,
        null=True,
        verbose_name=_("Document Type"),
    )
    document_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_("Document Number")
    )
    document_type_other = models.TextField(
        blank=True,
        null=True,
        help_text=_("Only used if document_type is OTHER"),
        verbose_name=_("Document Type Other"),
    )

    class Meta:
        db_table = "user_profile"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(country__regex=r"^[A-Z]{2}$")
                | models.Q(country__isnull=True),
                name="chk_user_profile_country_format",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_primary_role_display()}"


class Institution(AuditModel):
    """
    Institution model for educational organizations.
    Based on institutions table from the schema.
    """

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    # Branding
    logo = models.TextField(blank=True, null=True, verbose_name=_("Logo URL"))
    website = models.URLField(blank=True, null=True, verbose_name=_("Website"))

    # Contact
    contact_email = models.EmailField(
        blank=True, null=True, verbose_name=_("Contact Email")
    )
    contact_phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name=_("Contact Phone")
    )
    address = models.TextField(blank=True, null=True, verbose_name=_("Address"))
    city = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("City")
    )
    country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text=_("ISO 3166-1 alpha-2 country code"),
        verbose_name=_("Country"),
    )
    timezone = models.CharField(
        max_length=50, default="UTC", verbose_name=_("Timezone")
    )

    settings = models.JSONField(default=dict, blank=True, verbose_name=_("Settings"))

    class Meta:
        db_table = "institution"

    def __str__(self):
        return self.name


class Workspace(AuditModel):
    """
    Workspace model - central entity for organizing users and content.
    Based on workspaces table from the schema.
    """

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    type = models.CharField(
        max_length=20, choices=WorkspaceType.choices, verbose_name=_("Type")
    )
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    # Ownership
    owner_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="owned_workspaces",
        verbose_name=_("Owner User"),
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="workspaces",
        verbose_name=_("Institution"),
    )
    parent_workspace = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_workspaces",
        verbose_name=_("Parent Workspace"),
    )

    settings = models.JSONField(default=dict, blank=True, verbose_name=_("Settings"))

    class Meta:
        db_table = "workspace"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        type=WorkspaceType.PERSONAL,
                        owner_user__isnull=False,
                        institution__isnull=True,
                    )
                    | models.Q(
                        type=WorkspaceType.INSTITUTION_SEDE, institution__isnull=False
                    )
                    | models.Q(type=WorkspaceType.SHARED)
                ),
                name="chk_workspace_owner",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class UserWorkspaceMembership(AuditModel):
    """
    User membership in workspaces with roles and permissions.
    Based on user_workspace_memberships table from the schema.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
        verbose_name=_("User"),
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name=_("Workspace"),
    )
    role = models.CharField(
        max_length=20, choices=WorkspaceRole.choices, verbose_name=_("Role")
    )
    status = models.CharField(
        max_length=20,
        choices=MembershipStatus.choices,
        default=MembershipStatus.ACTIVE,
        verbose_name=_("Status"),
    )

    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workspace_membership_invitations",
        verbose_name=_("Invited By"),
    )
    joined_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Joined At"))
    left_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Left At"))

    permissions = models.JSONField(
        default=dict, blank=True, verbose_name=_("Permissions")
    )

    class Meta:
        db_table = "user_workspace_membership"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "workspace", "role"], name="uniq_user_workspace_role"
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} - {self.workspace.name} ({self.get_role_display()})"
        )


class Classroom(AuditModel):
    """
    Classroom model - Aulas dentro de workspaces donde se agrupan students y teachers.
    Based on classrooms table from the schema.
    """

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="classrooms",
        verbose_name=_("Workspace"),
    )
    unique_code = models.CharField(
        max_length=8,
        unique=True,
        verbose_name=_("Unique Code"),
        help_text=_(
            "8-character uppercase alphanumeric code for auto-enrollment (e.g., 'ABC12345')"
        ),
    )
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    subject = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Subject")
    )
    grade_level = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_("Grade Level")
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classrooms",
        verbose_name=_("Language"),
    )
    settings = models.JSONField(default=dict, blank=True, verbose_name=_("Settings"))

    class Meta:
        db_table = "classroom"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"


class ClassroomMembership(AuditModel):
    """
    Classroom membership model - M:N relationship between users and classrooms with roles.
    Based on classroom_memberships table from the schema.
    """

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name=_("Classroom"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="classroom_memberships",
        verbose_name=_("User"),
    )
    role = models.CharField(
        max_length=20,
        choices=ClassroomRole.choices,
        default=ClassroomRole.STUDENT,
        verbose_name=_("Role"),
    )
    joined_at = models.DateTimeField(default=timezone.now, verbose_name=_("Joined At"))
    left_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Left At"),
        help_text=_("When the user left the classroom (NULL if still active)"),
    )

    class Meta:
        db_table = "classroom_membership"
        constraints = [
            models.UniqueConstraint(
                fields=["classroom", "user"], name="uniq_classroom_user"
            )
        ]
        indexes = [
            models.Index(
                fields=["classroom", "user"],
                condition=models.Q(is_active=True),
                name="idx_classroom_memb_active",
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} - {self.classroom.name} ({self.get_role_display()})"
        )


class InvitationClassroom(models.Model):
    """
    Explicit through model for invitation-classroom relationship.
    This gives us full control over the table structure.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("ID")
    )
    invitation = models.ForeignKey(
        "Invitation",
        on_delete=models.CASCADE,
        related_name="invitation_classrooms",
        verbose_name=_("Invitation"),
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="invitation_classrooms",
        verbose_name=_("Classroom"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        db_table = "invitation_classroom"
        constraints = [
            models.UniqueConstraint(
                fields=["invitation", "classroom"],
                name="uniq_invitation_classroom",
            )
        ]
        indexes = [
            models.Index(fields=["invitation"], name="idx_inv_classroom_inv"),
            models.Index(fields=["classroom"], name="idx_inv_classroom_class"),
        ]

    def __str__(self):
        return f"{self.invitation.email} - {self.classroom.name}"


class Invitation(AuditModel):
    """
    Invitation model for inviting users to workspaces.
    Based on invitations table from the schema.
    """

    email = models.EmailField()
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="invitations"
    )
    role = models.CharField(max_length=20, choices=WorkspaceRole.choices)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=20,
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDING,
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True, editable=False)
    declined_at = models.DateTimeField(null=True, blank=True, editable=False)
    revoked_at = models.DateTimeField(null=True, blank=True, editable=False)
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="revoked_invitations",
        null=True,
        blank=True,
        editable=False,
    )
    welcome_message = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, null=True, blank=True)
    classrooms = models.ManyToManyField(
        Classroom,
        through="InvitationClassroom",
        blank=True,
        related_name="invitations",
    )

    class Meta:
        db_table = "invitation"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(expires_at__gt=models.F("created_at")),
                name="chk_invitation_expiry",
            )
        ]

    def clean(self):
        """
        Validate the invitation using the InvitationValidator service.

        All validation logic has been moved to services/invitation_validators.py
        to keep the model clean and maintainable.

        Note: Import is done lazily here to avoid circular import issues.
        Services should be imported at the module level, but models should
        only import services lazily (inside methods) to maintain proper
        architectural boundaries.
        """
        # Lazy import to avoid circular dependency
        from .services import InvitationValidator

        validator = InvitationValidator()
        validator.validate(self)

    def save(self, *args, **kwargs):
        """
        Save the invitation instance.

        This method ensures validation is performed before saving,
        and handles license reservation after successful creation.
        """
        self.full_clean()
        was_creating = self._state.adding

        super().save(*args, **kwargs)

        # Reserve license seat after successful creation
        if was_creating:
            self._reserve_license_seat()

    def _reserve_license_seat(self):
        """
        Reserve a license seat after invitation creation.

        This is called automatically after a new invitation is saved.
        If license service is not implemented, this will silently pass.

        Note: Import is done lazily here to avoid circular import issues.
        """
        if not self.created_by:
            return

        try:
            # Lazy import to avoid circular dependency
            from .services import get_license_service

            license_service = get_license_service()
            license_service.reserve_seat(
                user=self.created_by,
                workspace=self.workspace,
                role=self.role,
                invitation_id=str(self.pk),
            )
        except Exception:
            # If license service fails, log but don't break the invitation
            # In production, you might want to log this properly
            pass

    def __str__(self):
        return f"{self.email} - {self.role} - {self.workspace.name} - ({self.status})"
