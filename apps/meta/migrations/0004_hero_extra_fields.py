from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meta", "0003_hero_counter_synergy"),
    ]

    operations = [
        migrations.AddField(
            model_name="hero",
            name="damage_type",
            field=models.CharField(
                blank=True, default="",
                choices=[("physical", "Физический"), ("magic", "Магический"), ("mixed", "Смешанный")],
                max_length=10, verbose_name="Тип урона",
            ),
        ),
        migrations.AddField(
            model_name="hero",
            name="game_phase",
            field=models.CharField(
                blank=True, default="",
                choices=[("early", "Ранняя игра"), ("mid", "Средняя игра"), ("late", "Поздняя игра")],
                max_length=10, verbose_name="Фаза игры",
            ),
        ),
        migrations.AddField(
            model_name="hero",
            name="mobility",
            field=models.CharField(
                blank=True, default="",
                choices=[("high", "Высокая"), ("medium", "Средняя"), ("low", "Низкая")],
                max_length=10, verbose_name="Мобильность",
            ),
        ),
        migrations.AddField(
            model_name="hero",
            name="has_cc",
            field=models.BooleanField(default=False, verbose_name="Есть CC"),
        ),
        migrations.AddField(
            model_name="hero",
            name="has_sustain",
            field=models.BooleanField(default=False, verbose_name="Есть sustain"),
        ),
    ]
