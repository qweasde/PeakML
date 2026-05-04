from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_user_email_login"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="age",
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Возраст"),
        ),
        migrations.AddField(
            model_name="user",
            name="full_name",
            field=models.CharField(blank=True, max_length=255, verbose_name="ФИО"),
        ),
        migrations.AddField(
            model_name="user",
            name="gender",
            field=models.CharField(blank=True, choices=[("male", "Мужской"), ("female", "Женский")], max_length=10, verbose_name="Пол"),
        ),
        migrations.AddField(
            model_name="user",
            name="phone",
            field=models.CharField(blank=True, max_length=32, verbose_name="Телефон"),
        ),
        migrations.AddField(
            model_name="user",
            name="player_role",
            field=models.CharField(blank=True, choices=[("tank", "Танк"), ("fighter", "Боец"), ("assassin", "Убийца"), ("mage", "Маг"), ("marksman", "Стрелок"), ("support", "Поддержка")], max_length=20, verbose_name="Роль"),
        ),
    ]
