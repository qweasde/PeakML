import logging
from celery import shared_task
from django.core.management import call_command
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_mlbb_stats(self):
    """
    Sync hero win/pick/ban rates from mobilelegends.com.
    
    Runs: Every 4 hours
    Retries: Up to 3 times on failure
    """
    try:
        logger.info("🔄 Starting MLBB stats sync task...")
        call_command('fetch_mlbb_data', '--stats-only', '--tier-auto')
        logger.info("✅ MLBB stats sync completed successfully")
        return {"status": "success", "timestamp": timezone.now().isoformat()}
    except Exception as exc:
        logger.error(f"❌ MLBB stats sync failed: {exc}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=300)  # Retry in 5 minutes


@shared_task(bind=True, max_retries=3)
def fetch_mlbb_heroes(self):
    """
    Fetch and import all MLBB heroes from API.
    
    Runs: Daily at midnight
    Retries: Up to 3 times on failure
    """
    try:
        logger.info("🔄 Starting MLBB heroes fetch task...")
        call_command('fetch_mlbb_data', '--all', '--tier-auto')
        logger.info("✅ MLBB heroes fetch completed successfully")
        return {"status": "success", "timestamp": timezone.now().isoformat()}
    except Exception as exc:
        logger.error(f"❌ MLBB heroes fetch failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=600)  # Retry in 10 minutes


@shared_task
def recalculate_tier_scores():
    """
    Recalculate tier scores based on user votes.
    
    This task:
    - Calculates vote deltas for each tier entry
    - Optionally auto-adjusts tiers based on win rates
    
    Runs: Every hour
    """
    from .models import TierEntry
    
    logger.info("📊 Recalculating tier scores...")
    
    updated = 0
    for entry in TierEntry.objects.all().select_related('hero', 'patch'):
        old_tier = entry.tier
        
        # Calculate score based on votes
        score = entry.votes_up - entry.votes_down
        
        # Auto-adjust tier if win rate data is available
        if entry.win_rate:
            if entry.win_rate >= 54:
                new_tier = "S"
            elif entry.win_rate >= 51:
                new_tier = "A"
            elif entry.win_rate >= 48:
                new_tier = "B"
            else:
                new_tier = "C"
            
            if new_tier != old_tier:
                entry.tier = new_tier
                entry.save(update_fields=['tier'])
                updated += 1
                logger.info(f"  {entry.hero.name_ru}: {old_tier} → {new_tier} (WR={entry.win_rate}%)")
    
    logger.info(f"✅ Tier recalculation complete: {updated} entries updated")
