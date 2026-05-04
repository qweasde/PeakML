from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160, verbose_name="Название")),
                ("description", models.TextField(verbose_name="Описание")),
                ("price", models.CharField(max_length=80, verbose_name="Цена")),
                ("price_note", models.CharField(blank=True, help_text="Необязательный текст после слеша, например: час, игра, месяц.", max_length=120, verbose_name="Текст после цены")),
                ("icon", models.ImageField(blank=True, null=True, upload_to="services/icons/", verbose_name="Иконка")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать на сайте")),
                ("sort_order", models.PositiveIntegerField(default=100, verbose_name="Порядок")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Услуга",
                "verbose_name_plural": "Услуги",
                "ordering": ["sort_order", "title"],
            },
        ),
    ]
