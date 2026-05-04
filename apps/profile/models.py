from django.contrib.auth.hashers import check_password, make_password
from django.db import models


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
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Пользователь сайта"
        verbose_name_plural = "Пользователи сайта"
        ordering = ["-created_at"]

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
