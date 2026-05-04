from apps.meta.models import Patch

from .models import SiteConfig


def site_context(request):
    try:
        current_patch = Patch.objects.filter(is_current=True).first()
    except Exception:
        current_patch = None
    try:
        site_config = SiteConfig.get()
    except Exception:
        site_config = None
    return {
        "current_patch": current_patch,
        "site_name": site_config.site_name if site_config else "PeakML",
        "site_config": site_config,
        "user": getattr(request, "site_user", None),
        "site_user": getattr(request, "site_user", None),
        "staff_user": getattr(request, "user", None),
    }
