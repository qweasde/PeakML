from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email address must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Расширенный пользователь."""

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

    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, verbose_name="ФИО")
    age = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Возраст")
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        verbose_name="Пол",
    )
    player_role = models.CharField(
        max_length=20,
        choices=PlayerRole.choices,
        blank=True,
        verbose_name="Роль",
    )
    phone = models.CharField(max_length=32, blank=True, verbose_name="Телефон")
    is_pro = models.BooleanField(default=False, verbose_name="Pro-подписка")
    pro_until = models.DateTimeField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    ml_server = models.CharField(
        max_length=20,
        choices=[("ru", "Россия/СНГ"), ("sea", "SEA"), ("eu", "Europe")],
        default="ru",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class HomeSection(models.Model):
    SLUG_CHOICES = [
        ("features",     "Что внутри"),
        ("guides",       "Последние гайды"),
        ("builds",       "Лучшие сборки"),
        ("how_it_works", "Как это работает"),
        ("cta",          "Призыв к действию"),
    ]

    slug       = models.CharField(max_length=50, choices=SLUG_CHOICES, unique=True, verbose_name="Блок")
    is_enabled = models.BooleanField(default=True, verbose_name="Показывать")
    order      = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")
    badge      = models.CharField(max_length=80, blank=True, verbose_name="Бейдж", help_text="Маленький тег над заголовком, необязательно")
    title      = models.CharField(max_length=200, blank=True, verbose_name="Заголовок", help_text="Оставьте пустым для использования заголовка по умолчанию")
    subtitle   = models.CharField(max_length=400, blank=True, verbose_name="Подзаголовок", help_text="Необязательно")

    class Meta:
        verbose_name = "Блок главной страницы"
        verbose_name_plural = "Блоки главной страницы"
        ordering = ["order"]

    def __str__(self):
        return self.get_slug_display()

    @property
    def template_name(self):
        return f"home/sections/{self.slug}.html"


def _validate_ico(value):
    if not value.name.lower().endswith(".ico"):
        raise ValidationError("Допустимы только файлы с расширением .ico")


class SiteConfig(models.Model):
    site_name = models.CharField(max_length=100, default="PeakML", verbose_name="Название сайта")
    browser_title = models.CharField(
        max_length=200,
        default="PeakML",
        verbose_name="Заголовок в табе браузера",
        help_text="Отображается в заголовке вкладки браузера",
    )
    logo_icon = models.ImageField(
        upload_to="site/",
        null=True,
        blank=True,
        verbose_name="Иконка логотипа",
        help_text="Небольшое изображение слева от названия в навбаре",
    )
    favicon = models.FileField(
        upload_to="site/",
        null=True,
        blank=True,
        validators=[_validate_ico],
        verbose_name="Favicon (.ico)",
        help_text="Иконка в табе браузера, файл .ico",
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Singleton: always pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
