from django.shortcuts import render
from apps.guide.models import Build
from apps.meta.models import Role


def builds_index(request):
    role_filter = request.GET.get("role", "")
    qs = (
        Build.objects.filter(is_published=True)
        .select_related("hero", "hero__role", "patch", "role")
        .prefetch_related("items")
    )
    if role_filter:
        qs = qs.filter(hero__role__slug=role_filter)
    return render(request, "builds/index.html", {
        "builds":      qs,
        "roles":       Role.objects.all(),
        "role_filter": role_filter,
    })
