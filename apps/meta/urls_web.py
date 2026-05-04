from django.urls import path
from . import views

app_name = "meta"

urlpatterns = [
    path("", views.tier_list, name="index"),
    path("vote/<int:entry_id>/", views.vote, name="vote"),
]
