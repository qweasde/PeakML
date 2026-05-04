from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from apps.meta.models import HeroVote
from apps.services.models import ServiceOrder

from .auth import login_site_user, logout_site_user, site_login_required
from .forms import SiteUserLoginForm, SiteUserProfileForm, SiteUserSignupForm


@ensure_csrf_cookie
def signup_view(request):
    if getattr(request, "site_user", None) and request.site_user.is_authenticated:
        return redirect("profile:detail")

    if request.method == "POST":
        form = SiteUserSignupForm(request.POST)
        if form.is_valid():
            site_user = form.save()
            login_site_user(request, site_user)
            messages.success(request, "Аккаунт создан.")
            return redirect(request.POST.get("next") or "/")
    else:
        form = SiteUserSignupForm()

    return render(request, "account/signup.html", {"form": form})


@ensure_csrf_cookie
def login_view(request):
    if getattr(request, "site_user", None) and request.site_user.is_authenticated:
        return redirect(request.GET.get("next") or "/")

    if request.method == "POST":
        form = SiteUserLoginForm(request.POST)
        if form.is_valid():
            login_site_user(request, form.user)
            messages.success(request, "Вы вошли в аккаунт.")
            return redirect(request.POST.get("next") or "/")
    else:
        form = SiteUserLoginForm()

    return render(request, "account/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout_site_user(request)
        messages.success(request, "Вы вышли из аккаунта.")
        return redirect("/")
    return render(request, "account/logout.html")


@site_login_required
@ensure_csrf_cookie
def profile_view(request):
    if request.method == "POST":
        form = SiteUserProfileForm(request.POST, request.FILES, instance=request.site_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль сохранен.")
            return redirect("profile:detail")
    else:
        form = SiteUserProfileForm(instance=request.site_user)

    votes = (
        HeroVote.objects
        .filter(user=request.site_user)
        .select_related("tier_entry__hero", "tier_entry__patch", "tier_entry__hero__role")
        .order_by("-tier_entry__patch__released_at", "tier_entry__tier", "tier_entry__hero__name_ru")
    )
    orders = (
        ServiceOrder.objects
        .filter(site_user=request.site_user)
        .select_related("service")
        .order_by("-created_at")
    )

    tabs = [
        ("orders", "Мои заказы"),
        ("votes", "Мои голоса"),
        ("tournaments", "Мои турниры"),
        ("drafts", "Мои драфты"),
    ]

    return render(request, "profile/detail.html", {
        "form": form,
        "site_user": request.site_user,
        "votes": votes,
        "orders": orders,
        "tabs": tabs,
    })
