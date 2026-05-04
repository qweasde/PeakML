from django.db import migrations, models


def clear_old_votes(apps, schema_editor):
    HeroVote = apps.get_model("meta", "HeroVote")
    HeroVote.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("profile", "0001_initial"),
        ("meta", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(clear_old_votes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="herovote",
            name="user",
            field=models.ForeignKey(on_delete=models.CASCADE, related_name="hero_votes", to="profile.siteuser"),
        ),
    ]
