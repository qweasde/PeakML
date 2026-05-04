from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "meta-api"

router = DefaultRouter()
router.register("heroes", views.HeroViewSet, basename="hero")
router.register("tierlist", views.TierListViewSet, basename="tierlist")

urlpatterns = [
    path("", include(router.urls)),
]
