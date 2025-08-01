from django.urls import path

from core.rest.views.registration import PublicUserRegistration

urlpatterns = [
    path(
        "register",
        PublicUserRegistration.as_view(),
        name="user-registration",
    )
]
