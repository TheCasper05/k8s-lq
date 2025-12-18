from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from .models import (
    User,
    UserProfile,
    Language,
    Institution,
    Workspace,
    UserWorkspaceMembership,
    Classroom,
    ClassroomMembership,
    Invitation,
    InvitationClassroom,
)


DEFAULT_READ_ONLY_FIELDS = [
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
]

DEFAULT_SOFT_DELETE_FIELDS = [
    "deleted_at",
    "deleted_by",
]


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Custom User admin with UUID primary key support."""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "date_joined", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("-date_joined",)
    filter_horizontal = ("groups", "user_permissions")
    readonly_fields = ["id", "last_login", "date_joined"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal Information"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important Dates (Read Only)"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("System Information (Read Only)"),
            {
                "fields": ("id",),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


@admin.register(Language)
class LanguageAdmin(ModelAdmin):
    """Language admin interface."""

    list_display = (
        "code",
        "name",
        "native_name",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("code", "name", "native_name")
    ordering = ("code",)

    fieldsets = (
        (
            _("Language Information"),
            {
                "fields": (
                    "code",
                    "name",
                    "native_name",
                )
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
        (
            _("Audit Information"),
            {
                "fields": DEFAULT_READ_ONLY_FIELDS,
                "classes": ("collapse",),
            },
        ),
        (
            _("Soft Delete"),
            {
                "fields": DEFAULT_SOFT_DELETE_FIELDS,
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = DEFAULT_READ_ONLY_FIELDS


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    """UserProfile admin interface."""

    list_display = (
        "user",
        "primary_role",
        "phone",
        "timezone",
        "is_active",
        "created_at",
    )
    list_filter = ("primary_role", "timezone", "is_active", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone",
        "first_name",
        "last_name",
    )
    ordering = ("-created_at",)

    fieldsets = (
        (
            _("User Information"),
            {
                "fields": (
                    "user",
                    "primary_role",
                )
            },
        ),
        (
            _("Personal Information"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "birthday",
                    "phone",
                    "photo",
                    "bio",
                )
            },
        ),
        (
            _("Preferences"),
            {
                "fields": (
                    "timezone",
                    "language_preference",
                    "country",
                )
            },
        ),
        (
            _("Document Information"),
            {
                "fields": (
                    "document_type",
                    "document_number",
                    "document_type_other",
                ),
                "classes": ("collapse",),
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
        (
            _("Audit Information"),
            {
                "fields": DEFAULT_READ_ONLY_FIELDS,
                "classes": ("collapse",),
            },
        ),
        (
            _("Soft Delete"),
            {
                "fields": DEFAULT_SOFT_DELETE_FIELDS,
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = DEFAULT_READ_ONLY_FIELDS

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(Institution)
class InstitutionAdmin(ModelAdmin):
    """Institution admin interface."""

    list_display = (
        "name",
        "slug",
        "contact_email",
        "city",
        "country",
        "is_active",
        "created_at",
    )
    list_filter = ("country", "timezone", "is_active", "created_at")
    search_fields = ("name", "slug", "contact_email", "city", "description")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                )
            },
        ),
        (
            _("Branding"),
            {
                "fields": (
                    "logo",
                    "website",
                )
            },
        ),
        (
            _("Contact Information"),
            {
                "fields": (
                    "contact_email",
                    "contact_phone",
                    "address",
                    "city",
                    "country",
                    "timezone",
                )
            },
        ),
        (
            _("Settings"),
            {
                "fields": ("settings",),
                "classes": ("collapse",),
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
        (
            _("Audit Information"),
            {
                "fields": DEFAULT_READ_ONLY_FIELDS,
                "classes": ("collapse",),
            },
        ),
        (
            _("Soft Delete"),
            {
                "fields": DEFAULT_SOFT_DELETE_FIELDS,
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = DEFAULT_READ_ONLY_FIELDS


@admin.register(Workspace)
class WorkspaceAdmin(ModelAdmin):
    """Workspace admin interface."""

    list_display = (
        "name",
        "type",
        "slug",
        "owner_user",
        "institution",
        "is_active",
        "created_at",
    )
    list_filter = ("type", "is_active", "created_at", "institution")
    search_fields = (
        "name",
        "slug",
        "description",
        "owner_user__username",
        "owner_user__email",
        "institution__name",
    )
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "name",
                    "type",
                    "slug",
                    "description",
                )
            },
        ),
        (
            _("Ownership"),
            {
                "fields": (
                    "owner_user",
                    "institution",
                    "parent_workspace",
                )
            },
        ),
        (
            _("Settings"),
            {
                "fields": ("settings",),
                "classes": ("collapse",),
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
        (
            _("Audit Information"),
            {
                "fields": DEFAULT_READ_ONLY_FIELDS,
                "classes": ("collapse",),
            },
        ),
        (
            _("Soft Delete"),
            {
                "fields": DEFAULT_SOFT_DELETE_FIELDS,
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = DEFAULT_READ_ONLY_FIELDS

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "owner_user",
                "institution",
                "parent_workspace",
                "created_by",
                "updated_by",
            )
        )


@admin.register(UserWorkspaceMembership)
class UserWorkspaceMembershipAdmin(ModelAdmin):
    """UserWorkspaceMembership admin interface."""

    list_display = (
        "user",
        "workspace",
        "role",
        "status",
        "joined_at",
        "left_at",
        "is_active",
    )
    list_filter = (
        "role",
        "status",
        "is_active",
        "joined_at",
        "workspace__type",
    )
    search_fields = (
        "user__username",
        "user__email",
        "workspace__name",
        "workspace__slug",
    )
    ordering = ("-joined_at",)

    fieldsets = (
        (
            _("Membership Details"),
            {
                "fields": (
                    "user",
                    "workspace",
                    "role",
                    "status",
                )
            },
        ),
        (
            _("Membership Lifecycle"),
            {
                "fields": (
                    "invited_by",
                    "joined_at",
                    "left_at",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": ("permissions",),
                "classes": ("collapse",),
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
        (
            _("Audit Information"),
            {
                "fields": DEFAULT_READ_ONLY_FIELDS,
                "classes": ("collapse",),
            },
        ),
        (
            _("Soft Delete"),
            {
                "fields": DEFAULT_SOFT_DELETE_FIELDS,
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = DEFAULT_READ_ONLY_FIELDS

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "user", "workspace", "invited_by", "created_by", "updated_by"
            )
        )


@admin.register(Classroom)
class ClassroomAdmin(ModelAdmin):
    """Classroom admin interface."""

    list_display = (
        "name",
        "workspace",
        "unique_code",
        "subject",
        "grade_level",
        "language",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "created_at",
        "workspace__type",
        "language",
        "subject",
    )
    search_fields = (
        "name",
        "unique_code",
        "description",
        "workspace__name",
        "workspace__slug",
        "subject",
    )
    ordering = ("-created_at",)

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "name",
                    "workspace",
                    "unique_code",
                    "description",
                )
            },
        ),
        (
            _("Classroom Details"),
            {
                "fields": (
                    "subject",
                    "grade_level",
                    "language",
                )
            },
        ),
        (
            _("Settings"),
            {
                "fields": ("settings",),
                "classes": ("collapse",),
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
        (
            _("Audit Information"),
            {
                "fields": DEFAULT_READ_ONLY_FIELDS,
                "classes": ("collapse",),
            },
        ),
        (
            _("Soft Delete"),
            {
                "fields": DEFAULT_SOFT_DELETE_FIELDS,
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = DEFAULT_READ_ONLY_FIELDS + ["unique_code"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("workspace", "language", "created_by", "updated_by")
        )


@admin.register(ClassroomMembership)
class ClassroomMembershipAdmin(ModelAdmin):
    """ClassroomMembership admin interface."""

    list_display = (
        "classroom",
        "user",
        "role",
        "joined_at",
        "left_at",
        "is_active",
    )
    list_filter = (
        "role",
        "is_active",
        "joined_at",
        "classroom__workspace__type",
    )
    search_fields = (
        "user__username",
        "user__email",
        "classroom__name",
        "classroom__unique_code",
    )
    ordering = ("-joined_at",)

    fieldsets = (
        (
            _("Membership Details"),
            {
                "fields": (
                    "classroom",
                    "user",
                    "role",
                )
            },
        ),
        (
            _("Membership Lifecycle"),
            {
                "fields": (
                    "joined_at",
                    "left_at",
                )
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
        (
            _("Audit Information"),
            {
                "fields": DEFAULT_READ_ONLY_FIELDS,
                "classes": ("collapse",),
            },
        ),
        (
            _("Soft Delete"),
            {
                "fields": DEFAULT_SOFT_DELETE_FIELDS,
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = DEFAULT_READ_ONLY_FIELDS

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "classroom",
                "classroom__workspace",
                "user",
                "created_by",
                "updated_by",
            )
        )


class InvitationClassroomInline(admin.TabularInline):
    """Inline admin for InvitationClassroom."""

    model = InvitationClassroom
    extra = 1
    fields = ("classroom",)
    autocomplete_fields = ["classroom"]


@admin.register(Invitation)
class InvitationAdmin(ModelAdmin):
    """Invitation admin interface."""

    list_display = (
        "email",
        "workspace",
        "role",
        "status",
        "expires_at",
        "accepted_at",
        "declined_at",
        "revoked_at",
        "is_active",
        "created_at",
    )
    list_filter = (
        "status",
        "role",
        "is_active",
        "created_at",
        "expires_at",
        "workspace__type",
    )
    search_fields = (
        "email",
        "workspace__name",
        "workspace__slug",
        "token",
    )
    ordering = ("-created_at",)
    readonly_fields = DEFAULT_READ_ONLY_FIELDS + [
        "accepted_at",
        "declined_at",
        "revoked_at",
        "revoked_by",
        "token",
    ]
    inlines = [InvitationClassroomInline]

    fieldsets = (
        (
            _("Invitation Details"),
            {
                "fields": (
                    "email",
                    "workspace",
                    "role",
                    "status",
                    "token",
                )
            },
        ),
        (
            _("Invitation Content"),
            {
                "fields": (
                    "welcome_message",
                    "metadata",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Expiration"),
            {"fields": ("expires_at",)},
        ),
        (
            _("Status Tracking (Read Only)"),
            {
                "fields": (
                    "accepted_at",
                    "declined_at",
                    "revoked_at",
                    "revoked_by",
                ),
                "classes": ("collapse",),
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
        (
            _("Audit Information"),
            {
                "fields": DEFAULT_READ_ONLY_FIELDS,
                "classes": ("collapse",),
            },
        ),
        (
            _("Soft Delete"),
            {
                "fields": DEFAULT_SOFT_DELETE_FIELDS,
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "workspace",
                "revoked_by",
                "created_by",
                "updated_by",
            )
            .prefetch_related("classrooms")
        )
