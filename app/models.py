from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, county=None, registry=None, role="normal"):
        if not username:
            raise ValueError("The Username field is required")
        user = self.model(username=username, county=county, registry=registry, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, county="N/A", registry="N/A"):
        user = self.create_user(username=username, password=password, county=county, registry=registry, role="is_registrar_in_charge")
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
    registry = models.CharField(max_length=100, null=True, blank=True)  # new field
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="normal")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["county"]

    def __str__(self):
        return f"{self.username} ({self.role})"


class OfficialSearchApplication(models.Model):
    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("assigned", "Assigned"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    ]

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    parcel_number = models.CharField(max_length=100)
    purpose = models.TextField()
    county = models.CharField(max_length=100)
    registry = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Assigned registrar (set by registrar in charge)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_applications"
    )

    def __str__(self):
        return f"Application #{self.id} - {self.parcel_number}"


class Payment(models.Model):
    application = models.OneToOneField(
        OfficialSearchApplication,
        on_delete=models.CASCADE,
        related_name="payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_number = models.CharField(max_length=100, unique=True)
    payment_reference = models.CharField(max_length=100)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - App #{self.application.id}"


class Certificate(models.Model):
    application = models.OneToOneField(
        OfficialSearchApplication,
        on_delete=models.CASCADE,
        related_name="certificate"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_certificates"
    )
    signed_file = models.FileField(upload_to="certificates/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for Application #{self.application.id}"


class Review(models.Model):
    application = models.ForeignKey(
        OfficialSearchApplication,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} on App #{self.application.id}"
