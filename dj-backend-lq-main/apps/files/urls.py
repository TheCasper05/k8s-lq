from django.urls import path
from . import views

app_name = "files"

urlpatterns = [
    path("presigned-url", views.PresignedURLView.as_view(), name="presigned-url"),
    path(
        "presigned-download-url",
        views.PresignedDownloadURLView.as_view(),
        name="presigned-download-url",
    ),
]
