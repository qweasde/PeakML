from django.contrib import admin

from .models import Service, ServiceOrder


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "price_display", "is_active", "sort_order", "updated_at")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("title", "description", "price", "price_note")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "description", "icon")}),
        ("Цена", {"fields": ("price", "price_note")}),
        ("Публикация", {"fields": ("is_active", "sort_order")}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ("service", "full_name", "email", "phone", "status", "created_at")
    list_filter = ("status", "service", "created_at")
    list_editable = ("status",)
    search_fields = ("full_name", "email", "phone", "comment", "service__title")
    readonly_fields = ("service", "site_user", "full_name", "email", "phone", "comment", "created_at", "updated_at")
    fieldsets = (
        ("Заявка", {"fields": ("service", "status", "comment")}),
        ("Клиент", {"fields": ("site_user", "full_name", "email", "phone")}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )
