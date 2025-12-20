from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from graphene_django_cruddals import CRUDDALSView
from config.schema import schema
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from core.views import home

from config.graphql_depth import depth_limit_validator
from authentication.views import profile as auth_profile
from config.health import health_check, readiness_check, liveness_check
from authentication.jwt_views import (
    JWTLoginView,
    JWTRefreshView,
    JWTSessionView,
    JWTSignupView,
    JWTResendEmailVerificationView,
    JWTVerifyEmailView,
    JWTPasswordResetRequestView,
    JWTPasswordResetConfirmView,
    JWTSocialLoginView,
    JWTValidateView,
)
from authentication.jwt_views.realtime_tokens import RealtimeTokenView

urlpatterns = [
    path("", home),
    path("health/", health_check, name="health"),
    path("readiness/", readiness_check, name="readiness"),
    path("liveness/", liveness_check, name="liveness"),
    path(
        "graphql/",
        csrf_exempt(
            CRUDDALSView.as_view(
                graphiql=settings.ENVIRONMENT != "production",
                schema=schema,
                validation_rules=[depth_limit_validator(8)],
            )
        ),
    ),
    # JWT authentication endpoints (override allauth headless to return JWT tokens)
    path(
        "_allauth/browser/v1/auth/login",
        csrf_exempt(JWTLoginView.as_view()),
        name="jwt_login",
    ),
    path(
        "_allauth/browser/v1/auth/signup",
        csrf_exempt(JWTSignupView.as_view()),
        name="jwt_signup",
    ),
    path(
        "_allauth/browser/v1/auth/token/refresh",
        csrf_exempt(JWTRefreshView.as_view()),
        name="jwt_refresh",
    ),
    path(
        "_allauth/browser/v1/auth/session",
        csrf_exempt(JWTSessionView.as_view()),
        name="jwt_session",
    ),
    path(
        "_allauth/browser/v1/auth/resend-verification",
        csrf_exempt(JWTResendEmailVerificationView.as_view()),
        name="jwt_resend_verification",
    ),
    path(
        "_allauth/browser/v1/auth/email/verify/resend",
        csrf_exempt(JWTResendEmailVerificationView.as_view()),
        name="jwt_resend_verification_email",
    ),
    path(
        "_allauth/browser/v1/auth/email/verify",
        csrf_exempt(JWTVerifyEmailView.as_view()),
        name="jwt_verify_email_alt",
    ),
    path(
        "_allauth/app/v1/auth/verify-email",
        csrf_exempt(JWTVerifyEmailView.as_view()),
        name="jwt_verify_email_app",
    ),
    # Password reset endpoints
    path(
        "_allauth/browser/v1/auth/password/reset",
        csrf_exempt(JWTPasswordResetRequestView.as_view()),
        name="jwt_password_reset",
    ),
    path(
        "_allauth/browser/v1/auth/password/reset/key",
        csrf_exempt(JWTPasswordResetConfirmView.as_view()),
        name="jwt_password_reset_confirm",
    ),
    # Social auth endpoint
    path(
        "_allauth/browser/v1/auth/social",
        csrf_exempt(JWTSocialLoginView.as_view()),
        name="jwt_social_login",
    ),
    # JWT validation endpoint for microservices (e.g., realtime-service)
    path(
        "auth/jwt/validate/",
        csrf_exempt(JWTValidateView.as_view()),
        name="jwt_validate",
    ),
    # Realtime JWT token generation endpoint
    path(
        "api/v1/realtime/token",
        csrf_exempt(RealtimeTokenView.as_view()),
        name="realtime_token",
    ),
    # Urls files app (Boto3 S3 presigned URLs)
    path("api/v1/files/", include("files.urls")),
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
    path("files/", include("files.urls")),
    # TODO: Eliminar este endpoint, se creó para pruebas
    path("activities/", include("activities.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files in development/DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# URLs only available in local environment
if settings.ENVIRONMENT == "local":
    urlpatterns += [
        path("accounts/profile/", auth_profile, name="account_profile"),
        path("i18n/", include("django.conf.urls.i18n")),
        path("auth/", include("authentication.urls")),
    ]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("_nested_admin/", include("nested_admin.urls")),
)
