from django.contrib import admin

from .models import SiteUser


@admin.register(SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "player_role", "phone", "is_active", "created_at")
    list_filter = ("gender", "player_role", "is_active", "created_at")
    search_fields = ("email", "full_name", "phone")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("full_name", "email", "password", "is_active")}),
        ("Профиль", {"fields": ("age", "gender", "player_role", "phone")}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )
