# MLBB Hero Data - Setup & Usage Guide

## Overview

This guide explains how to set up and use the MLBB (Mobile Legends: Bang Bang) hero data fetching and syncing system.

## Quick Start

### 1. Initialize Initial Data
```bash
python manage.py seed_meta
```
This creates:
- 6 hero roles (Tank, Fighter, Assassin, Mage, Marksman, Support)
- Current patch (v1.9.04)
- 30 base heroes with tier assignments

### 2. Import All Heroes from MLBB API
```bash
python manage.py fetch_mlbb_data --all --tier-auto
```
This fetches all 132+ heroes and their current win/pick/ban rates from the official MLBB API.

**Options:**
- `--dry-run`: Preview what would be imported without saving
- `--tier-auto`: Auto-assign tiers based on win rates (S≥54%, A≥51%, B≥48%)
- `--no-stats`: Skip stat import (only fetch heroes)
- `--stats-only`: Only update stats for existing heroes (don't add new ones)

### 3. Setup Automatic Syncing (Celery)
```bash
python manage.py setup_mlbb_tasks
```
This creates 3 periodic tasks:
- **Sync MLBB Stats** - Every 4 hours (updates win/pick/ban rates)
- **Fetch MLBB Heroes** - Daily at midnight (full refresh)
- **Recalculate Tier Scores** - Every hour (updates tiers based on votes + win rates)

### 4. Start Celery with Beat Scheduler
```bash
celery -A config worker --beat --loglevel=info
```

Or in separate terminals:
```bash
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

## Management Commands

### `fetch_mlbb_data`
**Main command for fetching and syncing hero data**

```bash
# Fetch all heroes + sync stats with auto tier assignment
python manage.py fetch_mlbb_data --all --tier-auto

# Only update stats for existing heroes
python manage.py fetch_mlbb_data --stats-only

# Preview without saving
python manage.py fetch_mlbb_data --all --dry-run

# Without auto tier assignment
python manage.py fetch_mlbb_data --all --no-tier-auto
```

### `seed_heroes_from_web`
**Alternative command - fetch heroes from web API**

```bash
python manage.py seed_heroes_from_web --dry-run
python manage.py seed_heroes_from_web --tier-auto
python manage.py seed_heroes_from_web --no-stats
```

### `sync_mlbb_stats`
**Advanced command - scrape rank page for detailed stats**

```bash
python manage.py sync_mlbb_stats --dry-run
python manage.py sync_mlbb_stats --debug
python manage.py sync_mlbb_stats --tier-auto
```

### `seed_meta`
**Initialize base data**

```bash
python manage.py seed_meta
python manage.py seed_meta --reset  # Clear and reinitialize
```

### `setup_mlbb_tasks`
**Configure periodic Celery tasks**

```bash
python manage.py setup_mlbb_tasks
```

## Celery Tasks

### Direct Task Execution (for testing)
```python
from apps.meta.tasks import sync_mlbb_stats, fetch_mlbb_heroes, recalculate_tier_scores

# Sync stats immediately
sync_mlbb_stats.delay()

# Fetch all heroes immediately
fetch_mlbb_heroes.delay()

# Recalculate tier scores
recalculate_tier_scores.delay()
```

### Django Admin
You can also manage scheduled tasks from Django admin:
1. Go to `Admin > Django Celery Beat > Periodic Tasks`
2. View, enable/disable, or modify task schedules

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Mobile Legends API (gms.moontontech.com)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
                   [fetch_mlbb_data]
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Database                                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Hero Model (name, role, slug, etc.)                     │ │
│ │ TierEntry Model (win_rate, pick_rate, ban_rate, tier)   │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
                [recalculate_tier_scores]
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Web Application                                             │
│ - Tier List View                                            │
│ - Hero Rankings                                             │
│ - Win Rate Statistics                                       │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### Hero
- `name`: English name
- `name_ru`: Russian name
- `slug`: URL-friendly slug
- `role`: ForeignKey to Role (Tank, Fighter, etc.)
- `secondary_role`: Optional secondary role
- `icon`: Hero icon image
- Other metadata fields

### TierEntry
- `hero`: ForeignKey to Hero
- `patch`: ForeignKey to Patch
- `tier`: Tier grade (S, A, B, C)
- `win_rate`: Win rate percentage
- `pick_rate`: Pick rate percentage
- `ban_rate`: Ban rate percentage
- `votes_up`: User upvotes
- `votes_down`: User downvotes

### Patch
- `version`: Patch version (e.g., "1.9.04")
- `released_at`: Release date
- `is_current`: Mark as current patch
- `notes`: Patch notes

## Troubleshooting

### Issue: "No current patch found"
**Solution:** Create a patch in Django admin and set `is_current=True`

```bash
python manage.py shell
>>> from apps.meta.models import Patch
>>> from datetime import datetime
>>> Patch.objects.create(
...     version="1.9.04",
...     released_at=datetime.now(),
...     is_current=True,
...     notes="Current patch"
... )
```

### Issue: Celery tasks not running
**Check:**
1. Redis is running
2. Celery worker is running (`celery -A config worker`)
3. Celery beat is running (`celery -A config beat`)
4. Check logs: `celery -A config worker --loglevel=debug`

### Issue: Few heroes found in `sync_mlbb_stats`
**Cause:** The page structure on mobilelegends.com may have changed
**Solution:** Use `fetch_mlbb_data` instead - it's more reliable

## Performance Tips

1. **Use `--stats-only` for frequent updates** (faster, no new heroes)
2. **Run full fetch nightly** during low-traffic hours
3. **Set appropriate Celery worker concurrency:**
   ```bash
   celery -A config worker --concurrency=4 --loglevel=info
   ```
4. **Use Redis for caching** to speed up tier list views

## API Reference

### Programmatic Usage
```python
from apps.meta.models import Hero, TierEntry, Patch

# Get current patch
current_patch = Patch.objects.filter(is_current=True).first()

# Get all tier entries with stats
entries = TierEntry.objects.filter(
    patch=current_patch
).select_related('hero').order_by('-win_rate')

# Get top heroes by tier
for tier in ['S', 'A', 'B', 'C']:
    top_heroes = entries.filter(tier=tier)
    for entry in top_heroes:
        print(f"{entry.hero.name_ru}: {entry.win_rate}% WR")
```

## Configuration

### Environment Variables
```bash
# .env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=$REDIS_URL
CELERY_RESULT_BACKEND=django-db
```

### Django Settings (config/settings/base.py)
```python
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
```

## Updates & Logs

- Check task execution: Admin → Django Celery Results → Task Results
- Celery worker logs: Run with `--loglevel=info` or `--loglevel=debug`
- Django logs: Check `settings.LOGGING` configuration

---

**Last Updated:** May 5, 2026  
**Version:** 1.0
