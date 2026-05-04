from django.shortcuts import render
from apps.meta.models import TierEntry, Patch


def home(request):
    patch = Patch.objects.filter(is_current=True).first()
    top_heroes = []
    if patch:
        top_heroes = (
            TierEntry.objects.filter(patch=patch, tier="S")
            .select_related("hero", "hero__role")
            .order_by("-votes_up")[:6]
        )
    return render(request, "home.html", {"top_heroes": top_heroes, "patch": patch})
