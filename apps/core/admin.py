from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .admin_forms import ADMIN_USERNAME, AdminOnlyAuthenticationForm
from .models import SiteConfig, User, HomeSection


def admin_only_has_permission(request):
    return (
        request.user.is_active
        and request.user.is_staff
        and request.user.is_superuser
        and request.user.username == ADMIN_USERNAME
    )


admin.site.has_permission = admin_only_has_permission
admin.site.login_form = AdminOnlyAuthenticationForm
admin.site.site_header = "PeakML Admin"
admin.site.site_title = "PeakML Admin"
admin.site.index_title = "Управление сайтом"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Профиль", {"fields": ("full_name", "age", "gender", "player_role", "phone")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("PeakML", {"fields": ("is_pro", "pro_until", "avatar", "ml_server")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "full_name", "is_staff", "is_superuser"),
            },
        ),
    )
    list_display = ("email", "full_name", "player_role", "is_pro", "is_staff")
    list_filter = ("gender", "player_role", "is_pro", "ml_server", "is_staff")
    search_fields = ("email", "full_name", "phone")


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Название", {"fields": ("site_name", "browser_title")}),
        ("Изображения", {"fields": ("logo_icon", "favicon")}),
    )

    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteConfig.get()
        url = reverse("admin:core_siteconfig_change", args=[obj.pk])
        return HttpResponseRedirect(url)


@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display  = ("get_slug_display", "is_enabled", "order")
    list_editable = ("is_enabled", "order")
    ordering      = ("order",)
    fieldsets = (
        (None, {"fields": ("slug", "is_enabled", "order")}),
        ("Текст секции", {"fields": ("badge", "title", "subtitle"), "description": "Оставьте поля пустыми для использования текста по умолчанию"}),
    )

    def has_add_permission(self, request):
        return HomeSection.objects.count() < len(HomeSection.SLUG_CHOICES)

    def has_delete_permission(self, request, obj=None):
        return False
