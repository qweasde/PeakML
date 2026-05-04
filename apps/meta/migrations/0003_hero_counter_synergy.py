from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("meta", "0002_siteuser_votes"),
    ]

    operations = [
        migrations.CreateModel(
            name="HeroCounter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("strength", models.CharField(choices=[("hard", "Жёсткий"), ("soft", "Мягкий")], default="soft", max_length=10, verbose_name="Сила")),
                ("countered_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="counters_relations", to="meta.hero", verbose_name="Контрится героем")),
                ("hero", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="countered_by_relations", to="meta.hero", verbose_name="Герой")),
            ],
            options={
                "verbose_name": "Контр-пик",
                "verbose_name_plural": "Контр-пики",
            },
        ),
        migrations.AlterUniqueTogether(
            name="herocounter",
            unique_together={("hero", "countered_by")},
        ),
        migrations.CreateModel(
            name="HeroSynergy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("strength", models.CharField(choices=[("strong", "Сильная"), ("moderate", "Умеренная")], default="moderate", max_length=10, verbose_name="Сила")),
                ("hero_a", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="synergies_a", to="meta.hero", verbose_name="Герой A")),
                ("hero_b", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="synergies_b", to="meta.hero", verbose_name="Герой B")),
            ],
            options={
                "verbose_name": "Синергия",
                "verbose_name_plural": "Синергии",
            },
        ),
        migrations.AlterUniqueTogether(
            name="herosynergy",
            unique_together={("hero_a", "hero_b")},
        ),
    ]
