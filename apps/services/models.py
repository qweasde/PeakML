import re
from decimal import Decimal, InvalidOperation

from django.db import models


class Service(models.Model):
    title = models.CharField(max_length=160, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.CharField(max_length=80, verbose_name="Цена")
    price_note = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Текст после цены",
        help_text="Необязательный текст после слеша, например: час, игра, месяц.",
    )
    icon = models.ImageField(upload_to="services/icons/", null=True, blank=True, verbose_name="Иконка")
    is_pro = models.BooleanField(default=False, verbose_name="Только PRO", help_text="Пометить услугу как доступную по подписке PRO.")
    is_active = models.BooleanField(default=True, verbose_name="Показывать на сайте")
    sort_order = models.PositiveIntegerField(default=100, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    @property
    def price_display(self):
        if self.price_note:
            return f"{self.price} ₽ / {self.price_note}"
        return f"{self.price} ₽"

    @property
    def price_amount(self):
        if not self.price:
            return Decimal(0)

        cleaned = re.sub(r"[^\d.,]", "", self.price).strip().replace(",", ".")
        if not cleaned:
            return Decimal(0)

        try:
            return Decimal(cleaned)
        except InvalidOperation:
            digits = re.sub(r"\D", "", self.price)
            return Decimal(digits or 0)


class ServiceOrder(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Выполнена"
        CANCELED = "canceled", "Отменена"

    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="orders", verbose_name="Услуга")
    site_user = models.ForeignKey(
        "profile.SiteUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_orders",
        verbose_name="Пользователь сайта",
    )
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=32, blank=True, verbose_name="Телефон")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заявка на услугу"
        verbose_name_plural = "Заявки на услуги"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.service} — {self.full_name}"


class SubscriptionPlan(models.Model):
    """План подписки PRO."""
    title = models.CharField(max_length=160, verbose_name="Название")
    description = models.TextField(verbose_name="Что входит", help_text="Список преимуществ, по одному на строку")
    price = models.CharField(max_length=80, verbose_name="Цена")
    is_featured = models.BooleanField(default=False, verbose_name="Выделенный план", help_text="Центральный блок со ярким дизайном")
    is_active = models.BooleanField(default=True, verbose_name="Показывать на сайте")
    sort_order = models.PositiveIntegerField(default=100, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "План подписки"
        verbose_name_plural = "Планы подписки"
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title
