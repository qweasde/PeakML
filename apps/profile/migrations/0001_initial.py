from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SiteUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=255, verbose_name="ФИО")),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="Email")),
                ("password", models.CharField(max_length=128, verbose_name="Пароль")),
                ("age", models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Возраст")),
                ("gender", models.CharField(blank=True, choices=[("male", "Мужской"), ("female", "Женский")], max_length=10, verbose_name="Пол")),
                ("player_role", models.CharField(blank=True, choices=[("tank", "Танк"), ("fighter", "Боец"), ("assassin", "Убийца"), ("mage", "Маг"), ("marksman", "Стрелок"), ("support", "Поддержка")], max_length=20, verbose_name="Роль")),
                ("phone", models.CharField(blank=True, max_length=32, verbose_name="Телефон")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Пользователь сайта",
                "verbose_name_plural": "Пользователи сайта",
                "ordering": ["-created_at"],
            },
        ),
    ]
