from django.db import migrations, models


def populate_unique_emails(apps, schema_editor):
    User = apps.get_model("core", "User")
    used_emails = set()

    for user in User.objects.order_by("id"):
        raw_email = (user.email or "").strip().lower()

        if not raw_email:
            base_name = (user.username or f"user{user.id}").strip().lower() or f"user{user.id}"
            base_name = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in base_name)
            raw_email = f"{base_name}@local.invalid"

        candidate = raw_email
        suffix = 1
        while candidate in used_emails:
            local_part, domain = raw_email.split("@", 1)
            suffix += 1
            candidate = f"{local_part}-{suffix}@{domain}"

        if user.email != candidate:
            user.email = candidate
            user.save(update_fields=["email"])

        used_emails.add(candidate)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(populate_unique_emails, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True, verbose_name="email address"),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
