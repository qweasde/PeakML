from django.urls import path
from . import views

app_name = "guide"

urlpatterns = [
    path("", views.guide_index, name="index"),
    path("glossary/", views.glossary, name="glossary"),
    path("<slug:slug>/", views.guide_detail, name="detail"),
]
