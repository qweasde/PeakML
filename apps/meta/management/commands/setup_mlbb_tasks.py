"""
Setup periodic Celery Beat tasks for MLBB data synchronization.

Usage:
    python manage.py setup_mlbb_tasks  # Create/update scheduled tasks
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import json


class Command(BaseCommand):
    help = "Setup periodic tasks for MLBB data sync"

    def handle(self, *args, **options):
        self.stdout.write("Setting up MLBB periodic tasks...\n")

        # Task 1: Sync stats every 4 hours
        schedule_4h, created = IntervalSchedule.objects.get_or_create(
            every=4,
            period=IntervalSchedule.HOURS,
        )
        
        task_sync, created = PeriodicTask.objects.update_or_create(
            name="Sync MLBB Stats",
            defaults={
                "task": "apps.meta.tasks.sync_mlbb_stats",
                "interval": schedule_4h,
                "enabled": True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✅ Created: Sync MLBB Stats (every 4 hours)"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Updated: Sync MLBB Stats"))

        # Task 2: Fetch all heroes daily at midnight
        schedule_midnight, created = CrontabSchedule.objects.get_or_create(
            hour=0,
            minute=0,
            day_of_week='*',
        )
        
        task_fetch, created = PeriodicTask.objects.update_or_create(
            name="Fetch MLBB Heroes",
            defaults={
                "task": "apps.meta.tasks.fetch_mlbb_heroes",
                "crontab": schedule_midnight,
                "enabled": True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✅ Created: Fetch MLBB Heroes (daily at 00:00)"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Updated: Fetch MLBB Heroes"))

        # Task 3: Recalculate tier scores every hour
        schedule_1h, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.HOURS,
        )
        
        task_recalc, created = PeriodicTask.objects.update_or_create(
            name="Recalculate Tier Scores",
            defaults={
                "task": "apps.meta.tasks.recalculate_tier_scores",
                "interval": schedule_1h,
                "enabled": True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✅ Created: Recalculate Tier Scores (every hour)"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Updated: Recalculate Tier Scores"))

        self.stdout.write(self.style.SUCCESS("\n✅ All periodic tasks configured!"))
        self.stdout.write(
            "\n📝 To start Celery Beat scheduler, run:\n"
            "   celery -A config worker --beat --loglevel=info\n"
        )
