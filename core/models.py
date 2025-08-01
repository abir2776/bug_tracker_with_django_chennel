import logging

from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import BaseModelWithUID

from .choices import UserGender, UserStatus
from .managers import CustomUserManager

logger = logging.getLogger(__name__)


class User(AbstractUser, BaseModelWithUID):
    email = models.EmailField(unique=True, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
    )
    gender = models.CharField(
        max_length=20,
        blank=True,
        choices=UserGender.choices,
        default=UserGender.UNKNOWN,
    )
    date_of_birth = models.DateField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ("-date_joined",)

    def __str__(self):
        return f"UID: {self.uid}, Phone: {self.email}"

    def get_name(self):
        name = " ".join([self.first_name, self.last_name])
        return name.strip()
