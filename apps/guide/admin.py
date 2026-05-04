from django.contrib import admin
from .models import GuideSeries, Guide, GlossaryTerm


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


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ("term",)
    search_fields = ("term", "definition")
    prepopulated_fields = {"slug": ("term",)}
