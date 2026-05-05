from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.profile.auth import site_login_required
from .models import Hero, Role, Patch, TierEntry, HeroVote, Item
from .serializers import TierEntrySerializer, HeroSerializer, PatchSerializer


# ── Web views ──────────────────────────────────────────────────

def tier_list(request):
    patch = Patch.objects.filter(is_current=True).first()
    patches = Patch.objects.all()
    role_filter = request.GET.get("role", "")

    patch_id = request.GET.get("patch")
    if patch_id:
        patch = get_object_or_404(Patch, pk=patch_id)

    entries = {}
    if patch:
        qs = TierEntry.objects.filter(patch=patch).select_related("hero", "hero__role")
        if role_filter:
            qs = qs.filter(hero__role__slug=role_filter)
        for tier in ("S", "A", "B", "C"):
            entries[tier] = qs.filter(tier=tier).order_by("-votes_up")

    # Голоса текущего пользователя
    user_votes = {}
    if request.site_user.is_authenticated:
        user_votes = dict(
            HeroVote.objects.filter(
                user=request.site_user,
                tier_entry__patch=patch,
            ).values_list("tier_entry_id", "is_upvote")
        )

    roles = Role.objects.all()
    return render(request, "meta/tier_list.html", {
        "entries": entries,
        "patch": patch,
        "patches": patches,
        "roles": roles,
        "role_filter": role_filter,
        "user_votes": user_votes,
    })


@require_POST
@site_login_required
def vote(request, entry_id):
    """HTMX endpoint для голосования."""
    entry = get_object_or_404(TierEntry, pk=entry_id)
    direction = request.POST.get("direction")
    is_upvote = direction == "up"

    vote_obj, created = HeroVote.objects.get_or_create(
        user=request.site_user,
        tier_entry=entry,
        defaults={"is_upvote": is_upvote},
    )
    if not created:
        if vote_obj.is_upvote == is_upvote:
            # Повторный клик — отменяем голос
            vote_obj.delete()
            if is_upvote:
                TierEntry.objects.filter(pk=entry_id).update(votes_up=entry.votes_up - 1)
            else:
                TierEntry.objects.filter(pk=entry_id).update(votes_down=entry.votes_down - 1)
        else:
            vote_obj.is_upvote = is_upvote
            vote_obj.save()
            if is_upvote:
                TierEntry.objects.filter(pk=entry_id).update(
                    votes_up=entry.votes_up + 1, votes_down=entry.votes_down - 1
                )
            else:
                TierEntry.objects.filter(pk=entry_id).update(
                    votes_down=entry.votes_down + 1, votes_up=entry.votes_up - 1
                )
    else:
        if is_upvote:
            TierEntry.objects.filter(pk=entry_id).update(votes_up=entry.votes_up + 1)
        else:
            TierEntry.objects.filter(pk=entry_id).update(votes_down=entry.votes_down + 1)

    entry.refresh_from_db()
    return render(request, "meta/partials/vote_buttons.html", {
        "entry": entry,
        "user_vote": is_upvote if HeroVote.objects.filter(user=request.site_user, tier_entry=entry).exists() else None,
    })


def items_list(request):
    category_filter = request.GET.get("category", "")
    qs = Item.objects.all()
    if category_filter:
        qs = qs.filter(category=category_filter)
    return render(request, "meta/items.html", {
        "items":           qs,
        "categories":      Item.CATEGORY_CHOICES,
        "category_filter": category_filter,
    })


# ── DRF API viewsets ───────────────────────────────────────────

class HeroViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hero.objects.select_related("role").all()
    serializer_class = HeroSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "name_ru", "slug"]


class TierListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TierEntrySerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["tier", "votes_up"]

    def get_queryset(self):
        patch_id = self.request.query_params.get("patch")
        role = self.request.query_params.get("role")
        qs = TierEntry.objects.select_related("hero", "hero__role")
        if patch_id:
            qs = qs.filter(patch_id=patch_id)
        else:
            patch = Patch.objects.filter(is_current=True).first()
            if patch:
                qs = qs.filter(patch=patch)
        if role:
            qs = qs.filter(hero__role__slug=role)
        return qs

    @action(detail=False, methods=["get"])
    def current(self, request):
        patch = Patch.objects.filter(is_current=True).first()
        if not patch:
            return Response({"detail": "Текущий патч не найден."}, status=404)
        entries = TierEntry.objects.filter(patch=patch).select_related("hero", "hero__role")
        serializer = self.get_serializer(entries, many=True)
        return Response({"patch": PatchSerializer(patch).data, "entries": serializer.data})
