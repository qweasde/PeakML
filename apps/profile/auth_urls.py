from django.urls import path

from .views import login_view, logout_view, signup_view

urlpatterns = [
    path("login/", login_view, name="account_login"),
    path("signup/", signup_view, name="account_signup"),
    path("logout/", logout_view, name="account_logout"),
]
