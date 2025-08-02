from django.urls import path

from core.rest.views.registration import (
    LoginView,
    PublicUserRegistration,
    RegistrationView,
)

urlpatterns = [
    path(
        "register",
        PublicUserRegistration.as_view(),
        name="user-registration",
    ),
    path("register/ui", RegistrationView.as_view(), name="register-ui"),
    path("login/", LoginView.as_view(), name="login"),
]
