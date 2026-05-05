# MLBB Setup Checklist ✅

Complete this checklist to get your MLBB hero data system running.

## Phase 1: Preparation ✓

- [ ] Git repository is up to date
- [ ] Python venv is activated (`.venv\Scripts\activate` or `.venv/bin/activate`)
- [ ] All requirements installed: `pip install -r requirements.txt`
- [ ] PostgreSQL database is running
- [ ] Redis is running (for Celery)

## Phase 2: Initial Setup 🚀

### Quick Start (Recommended)
```bash
# Run this one command to set everything up
python mlbb_complete_setup.py
```

Result:
- ✅ Creates 6 roles (Tank, Fighter, Assassin, Mage, Marksman, Support)
- ✅ Creates current patch (v1.9.04)
- ✅ Creates 30 base heroes
- ✅ Fetches all 132+ heroes from MLBB API
- ✅ Sets up Celery periodic tasks

- [ ] Run complete setup script
- [ ] Verify: "Setup Complete!" message displayed

### Alternative: Manual Steps
If you prefer to do it step by step:

```bash
# Step 1: Initialize roles, patch, base heroes
python manage.py seed_meta

# Step 2: Fetch all heroes from API
python manage.py fetch_mlbb_data --all --tier-auto

# Step 3: Setup Celery tasks
python manage.py setup_mlbb_tasks
```

- [ ] Seed meta completed
- [ ] Heroes fetched (should show "✅ Fetched 132 heroes")
- [ ] Celery tasks created

## Phase 3: Start Services 🔧

### Terminal 1: Django Development Server
```bash
python manage.py runserver
```
- [ ] Server running at http://localhost:8000

### Terminal 2: Celery Worker with Beat
```bash
celery -A config worker --beat --loglevel=info
```

Or separately:
```bash
# Terminal 2: Celery Worker
celery -A config worker --loglevel=info

# Terminal 3: Celery Beat
celery -A config beat --loglevel=info
```

- [ ] Worker started (should show "ready to accept tasks")
- [ ] Beat scheduler started

## Phase 4: Verification ✅

### Check Hero Data
```bash
# Open Django shell
python manage.py shell
>>> from apps.meta.models import Hero, TierEntry, Patch
>>> Hero.objects.count()  # Should show 30+
>>> TierEntry.objects.count()  # Should show entries
>>> Patch.objects.filter(is_current=True).first()
```

- [ ] Heroes in database: 30+
- [ ] Tier entries exist
- [ ] Current patch exists

### Check Celery Tasks
```bash
# In Django shell
>>> from django_celery_beat.models import PeriodicTask
>>> PeriodicTask.objects.count()  # Should show 3
>>> PeriodicTask.objects.all().values('name', 'enabled')
```

- [ ] 3 periodic tasks created
- [ ] All tasks enabled
- [ ] Sync MLBB Stats (4h)
- [ ] Fetch MLBB Heroes (daily)
- [ ] Recalculate Tier Scores (1h)

### Check Web Interface
- [ ] Open http://localhost:8000/meta/tier-list/
- [ ] See tier list with heroes
- [ ] See win rates, pick rates, ban rates
- [ ] Can vote on heroes (up/down)
- [ ] Can filter by role

### Check Celery Results
1. Go to Django Admin: http://localhost:8000/admin/
2. Navigate to: **Django Celery Results > Task Results**
3. Should see recent task executions

- [ ] Task results showing in admin
- [ ] sync_mlbb_stats tasks appear
- [ ] Tasks have successful status

## Phase 5: Configuration 📋

### Update Notification (Optional)
Add to your Django settings to get Celery task notifications:

```python
# config/settings/local.py
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
```

- [ ] Review Celery configuration
- [ ] Add custom settings if needed

### Adjust Schedules (Optional)
In Django Admin → Periodic Tasks, you can:
- Change sync frequency (currently 4 hours)
- Change fetch time (currently midnight)
- Disable/enable tasks

- [ ] Review current schedules
- [ ] Adjust if needed

## Phase 6: Testing 🧪

### Test Hero Fetching
```bash
# Dry-run mode (no database changes)
python manage.py fetch_mlbb_data --all --dry-run

# Actual fetch
python manage.py fetch_mlbb_data --stats-only
```

- [ ] Dry-run shows 132 heroes
- [ ] Stats-only updates successfully

### Test Celery Tasks
```bash
# In Django shell
from apps.meta.tasks import sync_mlbb_stats, recalculate_tier_scores
sync_mlbb_stats.delay()  # Queue task
recalculate_tier_scores.delay()
```

- [ ] Tasks queue successfully
- [ ] Tasks execute in Celery worker
- [ ] Results appear in admin

### Manual Update Test
```bash
# Update hero stats manually
python manage.py fetch_mlbb_data --stats-only
```

- [ ] Command completes without errors
- [ ] Stats updated in database

## Phase 7: Documentation 📚

- [ ] Read [MLBB_SETUP.md](MLBB_SETUP.md) for detailed guide
- [ ] Read [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) for technical details
- [ ] Bookmark management commands reference
- [ ] Save Celery troubleshooting tips

## Ready to Deploy! 🎉

Once all checkboxes are complete, your MLBB hero data system is ready:

### Daily Operations
1. Keep `celery -A config worker --beat` running
2. Monitor Django Admin → Celery Results
3. Check tier list at `/meta/tier-list/`
4. Users can vote on heroes in tier list

### Maintenance Tasks
- **Weekly:** Check Celery logs for errors
- **Monthly:** Verify data accuracy in Django Admin
- **As needed:** Run `python manage.py fetch_mlbb_data --all` for full refresh

### Support
- See troubleshooting section in [MLBB_SETUP.md](MLBB_SETUP.md)
- Check Celery logs: `celery -A config worker --loglevel=debug`
- View database queries: `python manage.py dbshell`

---

## Command Reference

```bash
# Setup & Initialization
python mlbb_complete_setup.py                    # Full setup (recommended)
python manage.py seed_meta                       # Create initial data
python manage.py setup_mlbb_tasks                # Create Celery tasks

# Data Management
python manage.py fetch_mlbb_data --all           # Fetch all + stats
python manage.py fetch_mlbb_data --stats-only    # Update stats only
python manage.py fetch_mlbb_data --all --dry-run # Preview

# Celery Management
celery -A config worker --beat                   # Start worker + beat
celery -A config worker                          # Worker only
celery -A config beat                            # Beat scheduler only
celery -A config inspect active                  # Check active tasks
celery -A config purge                           # Clear task queue

# Database
python manage.py shell                           # Django shell
python manage.py dbshell                         # PostgreSQL shell
python manage.py migrate                         # Apply migrations
```

---

**Setup Date:** ________________  
**Completed By:** ________________  
**Notes:** _________________________________________________

---

Once complete, remove this checklist or mark all items ✅
