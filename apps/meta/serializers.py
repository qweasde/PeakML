from rest_framework import serializers
from .models import Hero, Role, Patch, TierEntry


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("slug", "name_ru", "icon")


class HeroSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = Hero
        fields = ("id", "name", "name_ru", "slug", "role", "specialty", "icon")


class PatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patch
        fields = ("id", "version", "released_at", "is_current")


class TierEntrySerializer(serializers.ModelSerializer):
    hero = HeroSerializer(read_only=True)
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = TierEntry
        fields = ("id", "hero", "tier", "votes_up", "votes_down", "score", "notes")
