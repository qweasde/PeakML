from django.db import migrations, models
import apps.core.models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_user_profile_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteConfig",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("site_name", models.CharField(default="PeakML", max_length=100, verbose_name="Название сайта")),
                (
                    "browser_title",
                    models.CharField(
                        default="PeakML",
                        help_text="Отображается в заголовке вкладки браузера",
                        max_length=200,
                        verbose_name="Заголовок в табе браузера",
                    ),
                ),
                (
                    "logo_icon",
                    models.ImageField(
                        blank=True,
                        help_text="Небольшое изображение слева от названия в навбаре",
                        null=True,
                        upload_to="site/",
                        verbose_name="Иконка логотипа",
                    ),
                ),
                (
                    "favicon",
                    models.FileField(
                        blank=True,
                        help_text="Иконка в табе браузера, файл .ico",
                        null=True,
                        upload_to="site/",
                        validators=[apps.core.models._validate_ico],
                        verbose_name="Favicon (.ico)",
                    ),
                ),
            ],
            options={
                "verbose_name": "Настройки сайта",
                "verbose_name_plural": "Настройки сайта",
            },
        ),
    ]
