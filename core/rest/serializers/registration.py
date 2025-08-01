import logging

from rest_framework import serializers

from core.choices import UserStatus
from core.models import User

logger = logging.getLogger(__name__)


class PublicUserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=50)
    first_name = serializers.CharField(min_length=2, max_length=50)
    last_name = serializers.CharField(min_length=2, max_length=50)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "phone",
            "first_name",
            "last_name",
        )

    def validate_email(self, data):
        email = data.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with email already exists!")
        return data

    def create(self, validated_data, *args, **kwargs):
        email = validated_data["email"].lower()
        password = validated_data["password"]
        first_name = validated_data["first_name"]
        last_name = validated_data["last_name"]

        user = User.objects.create(
            email=email,
            username=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            status=UserStatus.ACTIVE,
        )
        user.set_password(password)
        user.save()
        return user
