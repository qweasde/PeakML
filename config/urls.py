from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.profile.auth_urls")),
    path("profile/", include("apps.profile.urls", namespace="profile")),
    path("api/meta/", include("apps.meta.urls", namespace="meta-api")),
    path("meta/", include("apps.meta.urls_web", namespace="meta")),
    path("guide/", include("apps.guide.urls_web", namespace="guide")),
    path("draft/", include("apps.draft.urls", namespace="draft")),
    path("", include("apps.core.urls", namespace="core")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
