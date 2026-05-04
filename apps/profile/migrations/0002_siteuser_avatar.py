from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profile", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteuser",
            name="avatar",
            field=models.ImageField(blank=True, null=True, upload_to="avatars/", verbose_name="Фото"),
        ),
    ]
