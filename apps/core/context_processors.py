from apps.meta.models import Patch


def site_context(request):
    try:
        current_patch = Patch.objects.filter(is_current=True).first()
    except Exception:
        current_patch = None
    return {
        "current_patch": current_patch,
        "site_name": "PeakML",
    }
