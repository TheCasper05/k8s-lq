"""
JWT viewset split into focused modules.
"""

from .email_verification import (
    JWTResendEmailVerificationView,
    JWTVerifyEmailView,
    handle_verification_email_rate_limit,
)
from .login import JWTLoginView
from .password import (
    JWTPasswordResetConfirmView,
    JWTPasswordResetRequestView,
)
from .signup import JWTSignupView
from .social import JWTSocialLoginView
from .tokens import JWTRefreshView, JWTSessionView
from .utils import _client_ip, _is_email_verified, _ratelimit
from .validate import JWTValidateView

__all__ = [
    "_client_ip",
    "_is_email_verified",
    "_ratelimit",
    "JWTLoginView",
    "JWTSignupView",
    "JWTRefreshView",
    "JWTSessionView",
    "JWTVerifyEmailView",
    "JWTResendEmailVerificationView",
    "JWTPasswordResetRequestView",
    "JWTPasswordResetConfirmView",
    "JWTSocialLoginView",
    "JWTValidateView",
    "handle_verification_email_rate_limit",
]
