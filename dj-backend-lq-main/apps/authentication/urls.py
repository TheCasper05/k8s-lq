from django.urls import path

from . import views

app_name = "authentication"

# Note: Login/logout/registration are handled by allauth at /accounts/ and /_allauth/
# This app exposes an authenticated profile page that is used as the default
# LOGIN_REDIRECT_URL (`/accounts/profile/`).

urlpatterns = [
    path("profile/", views.profile, name="profile"),
]
