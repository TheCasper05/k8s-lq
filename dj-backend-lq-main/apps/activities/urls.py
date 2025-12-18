from django.urls import path
from . import views

app_name = "activities"

urlpatterns = [
    path("test/", views.TestEndpointView.as_view(), name="test_endpoint"),
]
