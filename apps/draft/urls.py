from django.urls import path
from . import views

app_name = "draft"

urlpatterns = [
    path("", views.draft_page, name="index"),
    path("analyze/", views.analyze, name="analyze"),
]
