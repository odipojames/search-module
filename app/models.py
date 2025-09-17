from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, county=None, role="normal"):
        if not username:
            raise ValueError("The Username field is required")
        user = self.model(username=username, county=county, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, county="N/A"):
        user = self.create_user(username=username, password=password, county=county, role="is_registrar_in_charge")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("normal", "Normal"),
        ("is_registrar", "Registrar"),
        ("is_registrar_in_charge", "Registrar In Charge"),
    ]

    username = models.CharField(max_length=150, unique=True)
    county = models.CharField(max_length=100)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="normal")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["county"]

    def __str__(self):
        return f"{self.username} ({self.role})"
