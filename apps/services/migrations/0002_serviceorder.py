import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profile", "0001_initial"),
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=255, verbose_name="ФИО")),
                ("email", models.EmailField(max_length=254, verbose_name="Email")),
                ("phone", models.CharField(blank=True, max_length=32, verbose_name="Телефон")),
                ("comment", models.TextField(blank=True, verbose_name="Комментарий")),
                ("status", models.CharField(choices=[("new", "Новая"), ("in_progress", "В работе"), ("done", "Выполнена"), ("canceled", "Отменена")], default="new", max_length=20, verbose_name="Статус")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("service", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="services.service", verbose_name="Услуга")),
                ("site_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="service_orders", to="profile.siteuser", verbose_name="Пользователь сайта")),
            ],
            options={
                "verbose_name": "Заявка на услугу",
                "verbose_name_plural": "Заявки на услуги",
                "ordering": ["-created_at"],
            },
        ),
    ]
