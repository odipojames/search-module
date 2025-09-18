from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OfficialSearchApplication, Payment, Certificate, Review

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "county", "registry", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active", "county", "registry")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("county", "registry", "role")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "county", "registry", "role", "password1", "password2", "is_staff", "is_active"),
        }),
    )
    search_fields = ("username", "county", "registry")
    ordering = ("username",)


@admin.register(OfficialSearchApplication)
class OfficialSearchApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "applicant", "parcel_number", "county", "registry", "status", "assigned_to", "submitted_at")
    list_filter = ("status", "county", "registry")
    search_fields = ("parcel_number", "applicant__username", "registry")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "application", "amount", "payment_reference", "paid_at")
    search_fields = ("invoice_number", "payment_reference", "application__parcel_number")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("application", "uploaded_by", "uploaded_at")
    search_fields = ("application__parcel_number", "uploaded_by__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("application", "reviewer", "created_at")
    search_fields = ("application__parcel_number", "reviewer__username")
