import csv
import io

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django import forms

from .models import Hero, Role, Patch, TierEntry, HeroVote, HeroCounter, HeroSynergy, Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display   = ("name_ru", "name", "category", "price", "patch")
    list_filter    = ("category", "patch")
    search_fields  = ("name", "name_ru")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "name_ru", "slug", "category", "price", "patch")}),
        ("Детали", {"fields": ("description", "icon")}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("slug", "name_ru")


class HeroCounterInline(admin.TabularInline):
    model = HeroCounter
    fk_name = "hero"
    autocomplete_fields = ("countered_by",)
    extra = 1
    verbose_name = "Контр-пик"
    verbose_name_plural = "Контр-пики (кем контрится этот герой)"


class HeroSynergyInline(admin.TabularInline):
    model = HeroSynergy
    fk_name = "hero_a"
    autocomplete_fields = ("hero_b",)
    extra = 1
    verbose_name = "Синергия"
    verbose_name_plural = "Синергии"


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ru", "role", "damage_type", "game_phase", "mobility", "has_cc", "has_sustain", "is_free")
    list_filter = ("role", "damage_type", "game_phase", "mobility", "has_cc", "has_sustain", "is_free")
    list_editable = ("damage_type", "game_phase", "mobility", "has_cc", "has_sustain")

    search_fields = ("name", "name_ru")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "name_ru", "slug", "role", "secondary_role", "specialty", "release_patch", "is_free")}),
        ("Медиа", {"fields": ("image", "icon")}),
        ("Характеристики драфта", {"fields": ("damage_type", "game_phase", "mobility", "has_cc", "has_sustain")}),

    )
    inlines = [HeroCounterInline, HeroSynergyInline]


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


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label="CSV-файл")


@admin.register(HeroCounter)
class HeroCounterAdmin(admin.ModelAdmin):
    list_display = ("hero", "countered_by", "strength")
    list_filter = ("strength",)
    search_fields = ("hero__name_ru", "countered_by__name_ru")
    autocomplete_fields = ("hero", "countered_by")
    change_list_template = "admin/meta/herocounter/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv_view),
                name="meta_herocounter_import_csv",
            ),
        ]
        return custom + urls

    def import_csv_view(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                reader = csv.DictReader(
                    io.TextIOWrapper(request.FILES["csv_file"], encoding="utf-8")
                )
                created = updated = errors = 0
                for row in reader:
                    hero_name = row.get("hero_name", "").strip()
                    counter_name = row.get("countered_by_name", "").strip()
                    strength = row.get("strength", "soft").strip()
                    try:
                        hero = Hero.objects.get(name_ru=hero_name)
                        counter = Hero.objects.get(name_ru=counter_name)
                        _, is_new = HeroCounter.objects.update_or_create(
                            hero=hero, countered_by=counter,
                            defaults={"strength": strength},
                        )
                        if is_new:
                            created += 1
                        else:
                            updated += 1
                    except Hero.DoesNotExist:
                        errors += 1
                self.message_user(
                    request,
                    f"Импорт завершён: создано {created}, обновлено {updated}, ошибок {errors}."
                )
                return HttpResponseRedirect("..")
        else:
            form = CsvImportForm()

        return render(request, "admin/csv_import.html", {
            "form": form,
            "title": "Импорт контр-пиков из CSV",
            "description": "Формат CSV: hero_name, countered_by_name, strength (hard/soft)",
            "opts": self.model._meta,
            "has_permission": True,
        })


@admin.register(HeroSynergy)
class HeroSynergyAdmin(admin.ModelAdmin):
    list_display = ("hero_a", "hero_b", "strength")
    list_filter = ("strength",)
    search_fields = ("hero_a__name_ru", "hero_b__name_ru")
    autocomplete_fields = ("hero_a", "hero_b")
    change_list_template = "admin/meta/herosynergy/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv_view),
                name="meta_herosynergy_import_csv",
            ),
        ]
        return custom + urls

    def import_csv_view(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                reader = csv.DictReader(
                    io.TextIOWrapper(request.FILES["csv_file"], encoding="utf-8")
                )
                created = updated = errors = 0
                for row in reader:
                    hero_a_name = row.get("hero_a_name", "").strip()
                    hero_b_name = row.get("hero_b_name", "").strip()
                    strength = row.get("strength", "moderate").strip()
                    try:
                        hero_a = Hero.objects.get(name_ru=hero_a_name)
                        hero_b = Hero.objects.get(name_ru=hero_b_name)
                        _, is_new = HeroSynergy.objects.update_or_create(
                            hero_a=hero_a, hero_b=hero_b,
                            defaults={"strength": strength},
                        )
                        if is_new:
                            created += 1
                        else:
                            updated += 1
                    except Hero.DoesNotExist:
                        errors += 1
                self.message_user(
                    request,
                    f"Импорт завершён: создано {created}, обновлено {updated}, ошибок {errors}."
                )
                return HttpResponseRedirect("..")
        else:
            form = CsvImportForm()

        return render(request, "admin/csv_import.html", {
            "form": form,
            "title": "Импорт синергий из CSV",
            "description": "Формат CSV: hero_a_name, hero_b_name, strength (strong/moderate)",
            "opts": self.model._meta,
            "has_permission": True,
        })
