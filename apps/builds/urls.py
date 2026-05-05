from django.urls import path
from . import views

app_name = "builds"

urlpatterns = [
    path("", views.builds_index, name="index"),
]
