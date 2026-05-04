from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("PeakML", {"fields": ("is_pro", "pro_until", "avatar", "ml_server")}),
    )
    list_display = ("email", "username", "is_pro", "is_staff")
    list_filter = ("is_pro", "ml_server", "is_staff")
