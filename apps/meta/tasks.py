from celery import shared_task


@shared_task
def recalculate_tier_scores():
    """Пересчитать рейтинги тиров на основе голосов."""
    from .models import TierEntry
    for entry in TierEntry.objects.all():
        # Здесь можно добавить логику авто-перемещения по тиру
        pass
