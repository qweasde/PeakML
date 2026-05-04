from django.shortcuts import render, get_object_or_404
from .models import GuideSeries, Guide, GlossaryTerm


def guide_index(request):
    series_list = GuideSeries.objects.prefetch_related("guides").filter(
        guides__published=True
    ).distinct().order_by("order")
    latest = Guide.objects.filter(published=True).order_by("-created_at")[:6]
    return render(request, "guide/index.html", {
        "series_list": series_list,
        "latest": latest,
    })


def guide_detail(request, slug):
    guide = get_object_or_404(Guide, slug=slug, published=True)
    Guide.objects.filter(pk=guide.pk).update(views=guide.views + 1)
    related = Guide.objects.filter(
        published=True, series=guide.series
    ).exclude(pk=guide.pk).order_by("order")[:4]
    return render(request, "guide/detail.html", {
        "guide": guide,
        "content_html": guide.get_content_html(),
        "related": related,
    })


def glossary(request):
    terms = GlossaryTerm.objects.all()
    return render(request, "guide/glossary.html", {"terms": terms})
