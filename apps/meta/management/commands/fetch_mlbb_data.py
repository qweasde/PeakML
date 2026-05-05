"""
Unified command for fetching and syncing MLBB hero data.

This command combines:
1. Fetching all heroes and their stats from the MLBB API
2. Syncing win/pick/ban rates to existing hero records
3. Updating tier assignments based on win rates

Usage:
    python manage.py fetch_mlbb_data --all          # Fetch all + sync stats
    python manage.py fetch_mlbb_data --stats-only   # Only sync stats (no new heroes)
    python manage.py fetch_mlbb_data --dry-run      # Dry run
"""
import json
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.meta.models import Hero, Patch, TierEntry, Role


# Hero ID mapping (official MLBB hero IDs)
HERO_MAP = {
    1: ("Miya", "marksman"),
    2: ("Balmond", "fighter"),
    3: ("Saber", "assassin"),
    4: ("Alice", "mage"),
    5: ("Nana", "support"),
    6: ("Tigreal", "tank"),
    7: ("Alucard", "fighter"),
    8: ("Karina", "assassin"),
    9: ("Akai", "tank"),
    10: ("Franco", "tank"),
    11: ("Bane", "fighter"),
    12: ("Bruno", "marksman"),
    13: ("Clint", "marksman"),
    14: ("Rafaela", "support"),
    15: ("Eudora", "mage"),
    16: ("Zilong", "fighter"),
    17: ("Fanny", "assassin"),
    18: ("Layla", "marksman"),
    19: ("Minotaur", "tank"),
    20: ("Lolita", "tank"),
    21: ("Hayabusa", "assassin"),
    22: ("Freya", "fighter"),
    23: ("Gord", "mage"),
    24: ("Natalia", "assassin"),
    25: ("Kagura", "mage"),
    26: ("Chou", "fighter"),
    27: ("Sun", "fighter"),
    28: ("Alpha", "fighter"),
    29: ("Ruby", "fighter"),
    30: ("Yi Sun-shin", "marksman"),
    31: ("Moskov", "marksman"),
    32: ("Johnson", "tank"),
    33: ("Cyclops", "mage"),
    34: ("Estes", "support"),
    35: ("Hilda", "fighter"),
    36: ("Aurora", "mage"),
    37: ("Lapu-Lapu", "fighter"),
    38: ("Vexana", "mage"),
    39: ("Roger", "fighter"),
    40: ("Karrie", "marksman"),
    41: ("Gatotkaca", "tank"),
    42: ("Harley", "mage"),
    43: ("Irithel", "marksman"),
    44: ("Grock", "tank"),
    45: ("Argus", "fighter"),
    46: ("Odette", "mage"),
    47: ("Lancelot", "assassin"),
    48: ("Diggie", "support"),
    49: ("Hylos", "tank"),
    50: ("Zhask", "mage"),
    51: ("Helcurt", "assassin"),
    52: ("Pharsa", "mage"),
    53: ("Lesley", "marksman"),
    54: ("Jawhead", "fighter"),
    55: ("Angela", "support"),
    56: ("Gusion", "assassin"),
    57: ("Valir", "mage"),
    58: ("Martis", "fighter"),
    59: ("Uranus", "tank"),
    60: ("Hanabi", "marksman"),
    61: ("Chang'e", "mage"),
    62: ("Kaja", "fighter"),
    63: ("Selena", "assassin"),
    64: ("Aldous", "fighter"),
    65: ("Claude", "marksman"),
    66: ("Vale", "mage"),
    67: ("Leomord", "fighter"),
    68: ("Lunox", "mage"),
    69: ("Hanzo", "assassin"),
    70: ("Belerick", "tank"),
    71: ("Kimmy", "marksman"),
    72: ("Thamuz", "fighter"),
    73: ("Harith", "mage"),
    74: ("Minsitthar", "fighter"),
    75: ("Kadita", "mage"),
    76: ("Faramis", "support"),
    77: ("Badang", "fighter"),
    78: ("Khufra", "tank"),
    79: ("Granger", "marksman"),
    80: ("Guinevere", "fighter"),
    81: ("Esmeralda", "tank"),
    82: ("Terizla", "fighter"),
    83: ("X.Borg", "fighter"),
    84: ("Ling", "assassin"),
    85: ("Dyrroth", "fighter"),
    86: ("Lylia", "mage"),
    87: ("Baxia", "tank"),
    88: ("Masha", "fighter"),
    89: ("Wanwan", "marksman"),
    90: ("Silvanna", "fighter"),
    91: ("Cecilion", "mage"),
    92: ("Carmilla", "support"),
    93: ("Atlas", "tank"),
    94: ("Popol and Kupa", "marksman"),
    95: ("Yu Zhong", "fighter"),
    96: ("Luo Yi", "mage"),
    97: ("Benedetta", "assassin"),
    98: ("Khaleed", "fighter"),
    99: ("Barats", "tank"),
    100: ("Brody", "marksman"),
    101: ("Yve", "mage"),
    102: ("Mathilda", "support"),
    103: ("Paquito", "fighter"),
    104: ("Gloo", "tank"),
    105: ("Beatrix", "marksman"),
    106: ("Phoveus", "fighter"),
    107: ("Aulus", "fighter"),
    108: ("Natan", "marksman"),
    109: ("Floryn", "support"),
    110: ("Edith", "tank"),
    111: ("Valentina", "mage"),
    112: ("Aamon", "assassin"),
    113: ("Fredrinn", "fighter"),
    114: ("Julian", "fighter"),
    115: ("Xavier", "mage"),
    116: ("Melissa", "marksman"),
    117: ("Yin", "fighter"),
    118: ("Gatotkaca", "tank"),
    119: ("Novaria", "mage"),
    120: ("Joy", "assassin"),
    121: ("Arlott", "fighter"),
    122: ("Nolan", "assassin"),
    123: ("Cici", "fighter"),
    124: ("Chip", "tank"),
    125: ("Zhuxin", "mage"),
    126: ("Lukas", "fighter"),
    127: ("Suyou", "assassin"),
    128: ("Skins", "fighter"),
    129: ("Kalea", "tank"),
    130: ("Rooney", "marksman"),
    131: ("ArcLight", "marksman"),
    132: ("Marcelko", "fighter"),
}

API_URL = "https://api.gms.moontontech.com/api/gms/source/2669606/2756567"
BASE_BODY = {
    "pageSize": 20,
    "filters": [
        {"field": "bigrank", "operator": "eq", "value": "101"},
        {"field": "match_type", "operator": "eq", "value": 0},
    ],
    "sorts": [
        {"data": {"field": "main_hero_win_rate", "order": "desc"}, "type": "sequence"},
        {"data": {"field": "main_heroid", "order": "desc"}, "type": "sequence"},
    ],
    "fields": [
        "main_hero", "main_hero_appearance_rate", "main_hero_ban_rate",
        "main_hero_channel", "main_hero_win_rate", "main_heroid",
    ],
}


class Command(BaseCommand):
    help = "Fetch MLBB heroes data from API and sync stats"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all", action="store_true",
            help="Fetch new heroes + sync stats (default mode)"
        )
        parser.add_argument(
            "--stats-only", action="store_true",
            help="Only sync stats for existing heroes (no new heroes)"
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Don't write to database"
        )
        parser.add_argument(
            "--tier-auto", action="store_true",
            help="Auto-assign tier based on win rate (S>=54, A>=51, B>=48, else C)"
        )
        parser.add_argument(
            "--no-stats", action="store_true",
            help="Don't update TierEntry (for --all mode)"
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        tier_auto = options["tier_auto"]
        no_stats = options["no_stats"]
        stats_only = options["stats_only"]

        self.stdout.write(f"🔄 Starting MLBB data sync at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Get or create current patch
        patch = Patch.objects.filter(is_current=True).first()
        if not patch:
            if dry_run:
                self.stdout.write(self.style.WARNING("⚠️  No current patch found (dry-run mode)"))
            else:
                self.stderr.write(self.style.ERROR("❌ No current patch. Set is_current=True on a Patch in admin."))
                return
        else:
            self.stdout.write(f"📌 Using patch: {patch.version}\n")

        # Fetch data from API
        heroes_data = self._fetch_from_api(dry_run)
        if not heroes_data:
            self.stderr.write(self.style.ERROR("❌ Failed to fetch data from API"))
            return

        self.stdout.write(f"✅ Fetched {len(heroes_data)} heroes from MLBB API\n")

        # Process heroes
        created_heroes = updated_heroes = created_stats = updated_stats = skipped = 0

        for item in heroes_data:
            heroid = item["heroid"]
            name_ru = item["name_ru"].strip()
            en_name, role_slug = HERO_MAP.get(heroid, (f"hero_{heroid}", None))

            win_rate = item["win_rate"]
            pick_rate = item["pick_rate"]
            ban_rate = item["ban_rate"]

            # Skip if stats-only mode
            if stats_only:
                hero = (
                    Hero.objects.filter(name_ru__iexact=name_ru).first() or
                    Hero.objects.filter(name__iexact=en_name).first()
                )
                if not hero:
                    skipped += 1
                    continue
            else:
                # Create or update Hero
                if not dry_run:
                    hero, is_new = Hero.objects.get_or_create(
                        name=en_name,
                        defaults={
                            "name_ru": name_ru,
                            "slug": self._make_slug(en_name),
                            "role": Role.objects.filter(slug=role_slug).first() if role_slug else None,
                        },
                    )
                    if not is_new and hero.name_ru != name_ru:
                        hero.name_ru = name_ru
                        hero.save(update_fields=["name_ru"])
                        updated_heroes += 1
                    elif is_new:
                        created_heroes += 1
                else:
                    hero = Hero.objects.filter(name=en_name).first()
                    self.stdout.write(
                        f"  [{heroid:3d}] {en_name:20s} WR={win_rate:5.2f}% "
                        f"Pick={pick_rate:5.2f}% Ban={ban_rate:6.2f}%"
                    )
                    continue

            # Update stats
            if not no_stats and patch:
                if not dry_run:
                    entry, is_new = TierEntry.objects.get_or_create(
                        hero=hero, patch=patch,
                        defaults={"tier": self._auto_tier(win_rate) if tier_auto else "B"}
                    )
                    entry.win_rate = win_rate
                    entry.pick_rate = pick_rate
                    entry.ban_rate = ban_rate
                    if tier_auto:
                        entry.tier = self._auto_tier(win_rate)
                    entry.save(update_fields=["win_rate", "pick_rate", "ban_rate"] + (["tier"] if tier_auto else []))
                    if is_new:
                        created_stats += 1
                    else:
                        updated_stats += 1

        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\n[DRY RUN] Would create {created_heroes} heroes, "
                f"update {updated_heroes}, create {created_stats} stats, update {updated_stats} stats\n"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Complete!\n"
                f"   Heroes: +{created_heroes} new, {updated_heroes} updated\n"
                f"   Stats:  +{created_stats} new, {updated_stats} updated\n"
            ))

    def _fetch_from_api(self, dry_run=False):
        """Fetch all heroes from MLBB API using Playwright for session."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.stderr.write("playwright not installed. Run: pip install playwright")
            return []

        self.stdout.write("🌐 Opening mobilelegends.com to get session...")
        session_headers = {}

        def handle_request(request):
            if "gms/source" in request.url and not session_headers:
                session_headers.update(request.headers)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ))
            page.on("request", handle_request)
            try:
                page.goto("https://www.mobilelegends.com/rank", wait_until="networkidle", timeout=45000)
            except Exception as e:
                self.stderr.write(f"⚠️  Failed to load page: {e}")
                browser.close()
                return []
            cookies = page.context.cookies()
            browser.close()

        if not session_headers:
            self.stderr.write("⚠️  Could not capture session headers")
            return []

        cookie_str = "; ".join(f'{c["name"]}={c["value"]}' for c in cookies)
        session_headers["cookie"] = cookie_str

        # Paginate through all heroes
        all_heroes = []
        seen_ids = set()
        total = 9999
        page_idx = 1

        while len(all_heroes) < total and page_idx <= 20:
            body = {**BASE_BODY, "pageIndex": page_idx}
            try:
                resp = requests.post(API_URL, json=body, headers=session_headers, timeout=15)
                data = resp.json()
            except Exception as e:
                self.stderr.write(f"⚠️  Request failed on page {page_idx}: {e}")
                break

            total = data.get("data", {}).get("total", 0)
            records = data.get("data", {}).get("records", [])
            if not records:
                break

            for r in records:
                d = r.get("data", {})
                heroid = d.get("main_heroid")
                if not heroid or heroid in seen_ids:
                    continue
                seen_ids.add(heroid)
                hero_info = d.get("main_hero", {}).get("data", {})
                all_heroes.append({
                    "heroid": heroid,
                    "name_ru": hero_info.get("name", f"Hero {heroid}"),
                    "icon_url": hero_info.get("head", ""),
                    "win_rate": round(d.get("main_hero_win_rate", 0) * 100, 2),
                    "pick_rate": round(d.get("main_hero_appearance_rate", 0) * 100, 2),
                    "ban_rate": round(d.get("main_hero_ban_rate", 0) * 100, 2),
                })

            self.stdout.write(f"   Page {page_idx}: {len(records)} heroes")
            page_idx += 1

        return all_heroes

    def _make_slug(self, name):
        base = slugify(name)
        if not base:
            base = slugify(name, allow_unicode=True)
        slug = base
        n = 1
        while Hero.objects.filter(slug=slug).exists():
            slug = f"{base}-{n}"
            n += 1
        return slug

    def _auto_tier(self, win_rate):
        if win_rate is None:
            return "B"
        if win_rate >= 54:
            return "S"
        if win_rate >= 51:
            return "A"
        if win_rate >= 48:
            return "B"
        return "C"
