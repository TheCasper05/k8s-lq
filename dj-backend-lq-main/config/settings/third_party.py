"""
Third-party integrations configuration.
(Graphene, REST Framework, Unfold, etc.)
"""

from datetime import timedelta

from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from config.settings.base import ENVIRONMENT

# Graphene configuration
graphene_middleware = ["apps.core.middlewares.GraphQLJWTMiddleware"]
if ENVIRONMENT != "production":
    graphene_middleware.append("graphene_django.debug.DjangoDebugMiddleware")

GRAPHENE = {
    "SCHEMA": "config.schema.schema",
    "MIDDLEWARE": graphene_middleware,
}

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",  # Keep for admin/browsable API
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# SimpleJWT configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# Unfold (Django Admin) configuration
UNFOLD = {
    "SITE_TITLE": "LingoQuesto",
    "SITE_HEADER": "LingoQuesto",
    "SITE_SUBHEADER": "LingoQuesto",
    "SITE_DROPDOWN": [
        {
            "icon": "diamond",
            "title": _("LingoQuesto"),
            "link": "https://lingoquesto.com",
        },
    ],
    "SHOW_LANGUAGES": True,
    "SITE_URL": "https://lingoquesto.com",
    "SITE_SYMBOL": "speed",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Django Auth"),
                "icon": "security",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:authentication_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                    {
                        "title": _("Permissions"),
                        "icon": "lock",
                        "link": reverse_lazy("admin:auth_permission_changelist"),
                    },
                    {
                        "title": _("Sessions"),
                        "icon": "timer",
                        "link": reverse_lazy("admin:sessions_session_changelist"),
                    },
                    {
                        "title": _("Content Types"),
                        "icon": "article",
                        "link": reverse_lazy(
                            "admin:contenttypes_contenttype_changelist"
                        ),
                    },
                ],
            },
            {
                "title": _("Django Allauth"),
                "icon": "security",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Email Addresses"),
                        "icon": "email",
                        "link": reverse_lazy("admin:account_emailaddress_changelist"),
                    },
                    {
                        "title": _("Social Accounts"),
                        "icon": "share",
                        "link": reverse_lazy(
                            "admin:socialaccount_socialaccount_changelist"
                        ),
                    },
                    {
                        "title": _("Social Application Tokens"),
                        "icon": "key",
                        "link": reverse_lazy(
                            "admin:socialaccount_socialtoken_changelist"
                        ),
                    },
                ],
            },
            {
                "title": _("Authentication"),
                "icon": "person",
                "collapsible": True,
                "items": [
                    {
                        "title": _("User Profiles"),
                        "icon": "account_circle",
                        "link": reverse_lazy(
                            "admin:authentication_userprofile_changelist"
                        ),
                    },
                    {
                        "title": _("Institutions"),
                        "icon": "business",
                        "link": reverse_lazy(
                            "admin:authentication_institution_changelist"
                        ),
                    },
                    {
                        "title": _("Workspaces"),
                        "icon": "workspaces",
                        "link": reverse_lazy(
                            "admin:authentication_workspace_changelist"
                        ),
                    },
                    {
                        "title": _("Workspace Memberships"),
                        "icon": "group_add",
                        "link": reverse_lazy(
                            "admin:authentication_userworkspacemembership_changelist"
                        ),
                    },
                ],
            },
        ],
    },
}
