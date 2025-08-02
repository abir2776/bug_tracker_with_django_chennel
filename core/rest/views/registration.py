from django.shortcuts import redirect
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import registration


class PublicUserRegistration(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = registration.PublicUserRegistrationSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(True, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(TemplateView):
    template_name = "core/registration.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Register - Create Your Account"
        return context


class LoginView(TemplateView):
    template_name = "core/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Login - Welcome Back"
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("projects-list")
        return super().get(request, *args, **kwargs)
