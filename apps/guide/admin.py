from django.contrib import admin
from .models import GuideSeries, Guide, GlossaryTerm, Build


@admin.register(GuideSeries)
class GuideSeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "role", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ("title", "series", "difficulty", "published", "views", "updated_at")
    list_filter = ("published", "difficulty", "series")
    list_editable = ("published",)
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display        = ("hero", "title", "role", "patch", "is_published", "order")
    list_editable       = ("is_published", "order")
    list_filter         = ("is_published", "patch", "role")
    search_fields       = ("title", "hero__name_ru")
    autocomplete_fields = ("hero",)
    filter_horizontal   = ("items",)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("hero", "role", "title", "slug", "description", "patch", "is_published", "order")}),
        ("Предметы сборки", {"fields": ("items",)}),
    )


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ("term",)
    search_fields = ("term", "definition")
    prepopulated_fields = {"slug": ("term",)}
