from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.sessions.models import Session
from nested_admin.nested import NestedModelAdmin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount


from django.db import models
from core.forms.widgets import AutoResizingTextarea
from core.inlines.main import BaseTabularInline


class BaseAdmin(ModelAdmin, NestedModelAdmin):
    formfield_overrides: dict = {  # type: ignore
        models.TextField: {"widget": AutoResizingTextarea},
    }

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Hook for specifying the form Field instance for a given database Field
        instance. If kwargs are given, they're passed to the form Field's constructor.
        """
        try:
            return super().formfield_for_dbfield(db_field, request, **kwargs)
        except Exception:
            return db_field.formfield(**kwargs)

    def render_change_form(self, request, context, obj=None, *args, **kwargs):
        return super().render_change_form(request, context, obj, *args, **kwargs)


DEFAULT_READ_ONLY_FIELDS = [
    "id",
    "created_at",
    "created_by",
    "updated_at",
    "updated_by",
]

DEFAULT_METADATA_FIELDS = (
    "Meta data",
    {
        "fields": (
            "is_active",
            ("created_at", "created_by"),
            ("updated_at", "updated_by"),
        )
    },
)

# admin.site.unregister(User)  # Using custom User model now
# admin.site.unregister(Group)


class EmailAddressInline(BaseTabularInline):
    model = EmailAddress
    extra = 0


class SocialAccountInline(BaseTabularInline):
    model = SocialAccount
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin, BaseAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    inlines = [
        EmailAddressInline,
        SocialAccountInline,
    ]
    list_display = (
        "pk",
        "email",
        "date_joined",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
    )
    ordering = ("-pk",)


# @admin.register(Group)  # Group is already registered by Django
# class GroupAdmin(BaseGroupAdmin, BaseAdmin):
#     pass


@admin.register(Session)
class SessionAdmin(BaseAdmin):
    pass


@admin.register(Permission)
class PermissionAdmin(BaseAdmin):
    pass


@admin.register(ContentType)
class ContentTypeAdmin(BaseAdmin):
    pass
