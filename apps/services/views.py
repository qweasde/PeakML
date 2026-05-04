from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Service, ServiceOrder


def index(request):
    services = Service.objects.filter(is_active=True)
    return render(request, "services/index.html", {"services": services})


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
