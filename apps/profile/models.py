import datetime

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class SiteUser(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Мужской"
        FEMALE = "female", "Женский"

    class PlayerRole(models.TextChoices):
        TANK = "tank", "Танк"
        FIGHTER = "fighter", "Боец"
        ASSASSIN = "assassin", "Убийца"
        MAGE = "mage", "Маг"
        MARKSMAN = "marksman", "Стрелок"
        SUPPORT = "support", "Поддержка"

    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    email = models.EmailField(unique=True, verbose_name="Email")
    password = models.CharField(max_length=128, verbose_name="Пароль")
    age = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Возраст")
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True, verbose_name="Пол")
    player_role = models.CharField(max_length=20, choices=PlayerRole.choices, blank=True, verbose_name="Роль")
    phone = models.CharField(max_length=32, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True, verbose_name="Фото")
    subscription_plan = models.ForeignKey(
        "services.SubscriptionPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscribers",
        verbose_name="Подписка PRO",
    )
    subscription_started_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата начала подписки")
    subscription_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата окончания подписки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Пользователь сайта"
        verbose_name_plural = "Пользователи сайта"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = SiteUser.objects.get(pk=self.pk)
                if old.subscription_plan_id != self.subscription_plan_id:
                    if self.subscription_plan_id is not None:
                        self.subscription_started_at = timezone.now()
                        self.subscription_expires_at = timezone.now() + datetime.timedelta(days=30)
                    else:
                        self.subscription_started_at = None
                        self.subscription_expires_at = None
            except SiteUser.DoesNotExist:
                pass
        elif self.subscription_plan_id:
            self.subscription_started_at = timezone.now()
            self.subscription_expires_at = timezone.now() + datetime.timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
