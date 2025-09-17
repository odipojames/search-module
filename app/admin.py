from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Fields to display in list view
    list_display = ("id", "username", "county", "role", "is_staff", "is_active")
    list_filter = ("role", "county", "is_staff", "is_active")

    # Fields visible when editing a user
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("county", "role")}),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    # Fields when creating a new user in admin
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "county", "role", "password1", "password2"),
        }),
    )

    search_fields = ("username", "county")
    ordering = ("username",)
