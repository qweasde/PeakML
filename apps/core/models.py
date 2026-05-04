from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Расширенный пользователь."""
    is_pro = models.BooleanField(default=False, verbose_name="Pro-подписка")
    pro_until = models.DateTimeField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    ml_server = models.CharField(
        max_length=20,
        choices=[("ru", "Россия/СНГ"), ("sea", "SEA"), ("eu", "Europe")],
        default="ru",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email or self.username
