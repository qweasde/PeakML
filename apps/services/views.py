from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Service, ServiceOrder, SubscriptionPlan

CART_SESSION_KEY = "service_cart"


def _get_cart_service_ids(request):
    return request.session.get(CART_SESSION_KEY, [])


def _save_cart_service_ids(request, service_ids):
    request.session[CART_SESSION_KEY] = service_ids


def _get_cart_items(request):
    service_ids = _get_cart_service_ids(request)
    services = Service.objects.filter(pk__in=service_ids, is_active=True)
    service_map = {service.pk: service for service in services}
    return [service_map[service_id] for service_id in service_ids if service_id in service_map]


def index(request):
    services = Service.objects.filter(is_active=True, is_pro=False)
    cart_service_ids = _get_cart_service_ids(request)
    return render(request, "services/index.html", {"services": services, "cart_service_ids": cart_service_ids})


def pro(request):
    services = Service.objects.filter(is_active=True, is_pro=True)
    plans = list(SubscriptionPlan.objects.filter(is_active=True).order_by("sort_order"))
    for plan in plans:
        plan.description_lines = [line.strip() for line in plan.description.splitlines() if line.strip()]
    cart_service_ids = _get_cart_service_ids(request)
    return render(request, "services/pro.html", {
        "services": services,
        "plans": plans,
        "cart_service_ids": cart_service_ids
    })


@require_POST
def add_to_cart(request, service_id):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    service_ids = _get_cart_service_ids(request)
    if service.pk not in service_ids:
        service_ids.append(service.pk)
        _save_cart_service_ids(request, service_ids)
        messages.success(request, f"Услуга «{service.title}» добавлена в корзину.")
    else:
        messages.info(request, f"Услуга «{service.title}» уже в корзине.")
    return redirect("services:index")


@require_POST
def remove_from_cart(request, service_id):
    service_ids = _get_cart_service_ids(request)
    service_ids = [pk for pk in service_ids if pk != service_id]
    _save_cart_service_ids(request, service_ids)
    messages.success(request, "Услуга удалена из корзины.")
    return redirect("services:cart")


def cart(request):
    cart_items = _get_cart_items(request)
    cart_total = sum(item.price_amount for item in cart_items)
    total_display = f"{cart_total:.2f}".rstrip("0").rstrip(".")
    return render(request, "services/cart.html", {"cart_items": cart_items, "cart_total": total_display})


@require_POST
def checkout(request):
    service_ids = _get_cart_service_ids(request)
    cart_items = _get_cart_items(request)
    site_user = getattr(request, "site_user", None)

    if not cart_items:
        messages.error(request, "Ваша корзина пуста.")
        return redirect("services:cart")

    if not site_user or not site_user.is_authenticated:
        return redirect(f"/accounts/login/?next=/services/cart/")

    for service in cart_items:
        ServiceOrder.objects.create(
            service=service,
            site_user=site_user,
            full_name=site_user.full_name,
            email=site_user.email,
            phone=site_user.phone,
        )

    _save_cart_service_ids(request, [])
    messages.success(request, "Заказ оформлен. В ближайшее время мы свяжемся с вами для оплаты услуг.")
    return redirect("profile:detail")


@require_POST
def order(request, service_id):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    site_user = getattr(request, "site_user", None)

    if not site_user or not site_user.is_authenticated:
        return redirect(f"/accounts/login/?next=/services/")

    ServiceOrder.objects.create(
        service=service,
        site_user=site_user,
        full_name=site_user.full_name,
        email=site_user.email,
        phone=site_user.phone,
    )
    messages.success(request, f"Заявка на услугу «{service.title}» отправлена.")
    return redirect("services:index")
