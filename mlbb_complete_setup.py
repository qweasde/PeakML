#!/usr/bin/env python
"""
Complete MLBB Hero Data Setup & Sync Script
Run this to set up everything from scratch.

Usage:
    python mlbb_complete_setup.py    # Full setup
    python mlbb_complete_setup.py --test-only    # Test without saving
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.core.management import call_command
from django.utils import timezone
import argparse


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Complete MLBB Hero Data Setup")
    parser.add_argument(
        "--test-only", action="store_true",
        help="Run with --dry-run (no database changes)"
    )
    args = parser.parse_args()

    dry_run_arg = ["--dry-run"] if args.test_only else []
    test_label = "[TEST MODE] " if args.test_only else ""

    print_header("🎮 MLBB Hero Data Complete Setup")
    print(f"Started: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Step 1: Seed meta data
    print_header(f"{test_label}Step 1/4: Initialize Meta Data")
    print("Creating roles, patch, and base heroes...")
    try:
        call_command("seed_meta")
        print("✅ Meta data initialized\n")
    except Exception as e:
        print(f"⚠️  Meta data issue (may already exist): {e}\n")

    # Step 2: Fetch all heroes
    print_header(f"{test_label}Step 2/4: Fetch MLBB Heroes")
    print("Fetching all heroes and stats from MLBB API...")
    print("This may take 1-2 minutes...\n")
    try:
        cmd_args = ["--all", "--tier-auto"] + dry_run_arg
        call_command("fetch_mlbb_data", *cmd_args)
        print("✅ Heroes fetched successfully\n")
    except Exception as e:
        print(f"❌ Failed to fetch heroes: {e}\n")
        sys.exit(1)

    # Step 3: Setup Celery tasks (skip in test mode)
    if not args.test_only:
        print_header("Step 3/4: Setup Celery Periodic Tasks")
        print("Creating automated sync schedules...")
        try:
            call_command("setup_mlbb_tasks")
            print("✅ Celery tasks configured\n")
        except Exception as e:
            print(f"⚠️  Celery setup issue: {e}")
            print("    (You can run this manually later: python manage.py setup_mlbb_tasks)\n")

        # Step 4: Print next steps
        print_header("Step 4/4: Next Steps")
        print("""
Start the application with Celery:

  Option 1 - Single command (background beat scheduling):
    celery -A config worker --beat --loglevel=info

  Option 2 - Separate worker and beat (recommended):
    Terminal 1: celery -A config worker --loglevel=info
    Terminal 2: celery -A config beat --loglevel=info

Then access the tier list at: http://localhost:8000/meta/tier-list/

📋 Scheduled Tasks:
  - Every 4 hours:    Sync hero stats from API
  - Daily at 00:00:   Full hero fetch
  - Every hour:       Recalculate tier scores

For manual updates:
  python manage.py fetch_mlbb_data --stats-only        # Quick update
  python manage.py fetch_mlbb_data --all --tier-auto   # Full refresh

        """)
    else:
        print_header("TEST MODE - COMPLETE")
        print("✅ All operations completed in test mode (--dry-run)")
        print("\nRun without --test-only to save changes to database\n")

    print_header("Setup Complete!")
    print(f"Finished: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()
