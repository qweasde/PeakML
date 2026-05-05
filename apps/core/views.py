from django.shortcuts import render
from apps.meta.models import Patch
from apps.guide.models import Guide, Build
from .models import HomeSection


def home(request):
    patch = Patch.objects.filter(is_current=True).first()

    sections = HomeSection.objects.filter(is_enabled=True).order_by("order")

    latest_guides = Guide.objects.filter(published=True).order_by("-created_at").select_related("series")[:3]

    top_builds = Build.objects.filter(is_published=True).order_by("order", "-created_at").select_related("hero", "hero__role", "patch")[:4]

    return render(request, "home.html", {
        "patch":         patch,
        "sections":      sections,
        "latest_guides": latest_guides,
        "top_builds":    top_builds,
    })
