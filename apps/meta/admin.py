from django.contrib import admin
from .models import Hero, Role, Patch, TierEntry, HeroVote


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("slug", "name_ru")


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ru", "role", "is_free")
    list_filter = ("role", "is_free")
    search_fields = ("name", "name_ru")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Patch)
class PatchAdmin(admin.ModelAdmin):
    list_display = ("version", "released_at", "is_current")
    list_editable = ("is_current",)


@admin.register(TierEntry)
class TierEntryAdmin(admin.ModelAdmin):
    list_display = ("hero", "patch", "tier", "votes_up", "votes_down")
    list_filter = ("patch", "tier", "hero__role")
    list_editable = ("tier",)
    search_fields = ("hero__name", "hero__name_ru")
    autocomplete_fields = ("hero",)


@admin.register(HeroVote)
class HeroVoteAdmin(admin.ModelAdmin):
    list_display = ("user", "tier_entry", "is_upvote", "created_at")
    list_filter = ("is_upvote",)
