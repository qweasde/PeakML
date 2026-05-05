import re

from django.core.management.base import BaseCommand

from apps.meta.models import Hero, Patch, TierEntry


class Command(BaseCommand):
    help = "Sync hero win/pick/ban rates from mobilelegends.com/rank"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Don't save to DB, just print what would be updated")
        parser.add_argument("--debug", action="store_true", help="Print raw parsed data and unmatched heroes")
        parser.add_argument(
            "--tier-auto",
            action="store_true",
            help="Auto-assign tier based on win rate (S>=54, A>=51, B>=48, else C)",
        )

    def handle(self, *args, **options):
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except ImportError:
            self.stderr.write("playwright not installed. Run: pip install playwright && playwright install chromium")
            return

        dry_run = options["dry_run"]
        debug = options["debug"]
        tier_auto = options["tier_auto"]

        patch = Patch.objects.filter(is_current=True).first()
        if not patch:
            self.stderr.write("No current patch found. Set is_current=True on a patch in admin.")
            return

        self.stdout.write(f"Syncing stats for patch {patch.version}...")

        heroes_data = self._scrape(debug)
        if not heroes_data:
            self.stderr.write(
                "No hero data scraped.\n"
                "Run with --debug to see API responses.\n"
                "The site structure may have changed — check selectors in the command."
            )
            return

        self.stdout.write(f"Found {len(heroes_data)} heroes from site.")

        created = updated = skipped = 0
        for item in heroes_data:
            name = item["name"].strip()
            # Site shows Russian names — match by name_ru first, then English name
            hero = (
                Hero.objects.filter(name_ru__iexact=name).first()
                or Hero.objects.filter(name__iexact=name).first()
                or Hero.objects.filter(name_ru__icontains=name).first()
            )
            if not hero:
                if debug:
                    self.stdout.write(f"  SKIP (no DB match): '{name}'")
                skipped += 1
                continue

            if debug:
                self.stdout.write(
                    f"  MATCH: '{name}' → {hero.name_ru}  "
                    f"WR={item['win_rate']}%  Pick={item['pick_rate']}%  Ban={item['ban_rate']}%"
                )

            if not dry_run:
                entry, is_new = TierEntry.objects.get_or_create(
                    hero=hero,
                    patch=patch,
                    defaults={"tier": self._auto_tier(item["win_rate"]) if tier_auto else "B"},
                )
                entry.win_rate = item["win_rate"]
                entry.pick_rate = item["pick_rate"]
                entry.ban_rate = item["ban_rate"]
                if tier_auto:
                    entry.tier = self._auto_tier(item["win_rate"])
                entry.save(update_fields=["win_rate", "pick_rate", "ban_rate"] + (["tier"] if tier_auto else []))
                if is_new:
                    created += 1
                else:
                    updated += 1
            else:
                updated += 1

        label = "[DRY RUN] Would update" if dry_run else "Done."
        self.stdout.write(
            self.style.SUCCESS(
                f"{label} Created: {created}, Updated: {updated}, Skipped (no DB match): {skipped}"
            )
        )
        if skipped and not debug:
            self.stdout.write("Run with --debug to see which hero names were not found in DB.")

    # ------------------------------------------------------------------
    # Scraping
    # ------------------------------------------------------------------

    def _scrape(self, debug=False):
        from playwright.sync_api import sync_playwright

        results = []
        api_responses = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )

            def handle_response(response):
                url = response.url
                if response.status != 200:
                    return
                ct = response.headers.get("content-type", "")
                if "json" not in ct:
                    return
                # Catch any API call that looks like rank/hero data
                if any(kw in url for kw in ("rank", "hero", "stat", "pick", "win")):
                    try:
                        data = response.json()
                        api_responses.append({"url": url, "data": data})
                    except Exception:
                        pass

            page.on("response", handle_response)

            self.stdout.write("Opening mobilelegends.com/rank ...")
            page.goto("https://www.mobilelegends.com/rank", wait_until="networkidle", timeout=45000)

            if debug:
                self.stdout.write(f"\n[DEBUG] JSON API calls intercepted: {len(api_responses)}")
                for r in api_responses:
                    self.stdout.write(f"  {r['url']}")
                    data = r["data"]
                    if isinstance(data, dict):
                        self.stdout.write(f"    keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        self.stdout.write(f"    list length: {len(data)}, first item keys: {list(data[0].keys()) if data and isinstance(data[0], dict) else '?'}")

            # 1) Try to parse hero data from intercepted API responses
            for r in api_responses:
                heroes = self._extract_from_api(r["data"])
                if heroes:
                    if debug:
                        self.stdout.write(f"\n[DEBUG] Extracted {len(heroes)} heroes from API: {r['url']}")
                    results.extend(heroes)
                    break

            # 2) Fallback: parse rendered DOM
            if not results:
                if debug:
                    self.stdout.write("\n[DEBUG] No API data matched — falling back to DOM parsing")
                results = self._parse_dom(page, debug)

            browser.close()

        return results

    def _extract_from_api(self, data):
        """Try to extract hero stats from various API response shapes."""
        candidates = []

        if isinstance(data, list):
            candidates = data
        elif isinstance(data, dict):
            # Dig one level for common key patterns
            for key in ("data", "heroes", "list", "result", "records", "hero_list"):
                val = data.get(key)
                if isinstance(val, list):
                    candidates = val
                    break
                if isinstance(val, dict):
                    for subkey in ("list", "heroes", "records", "data"):
                        if isinstance(val.get(subkey), list):
                            candidates = val[subkey]
                            break
                    if candidates:
                        break

        results = []
        for item in candidates:
            if not isinstance(item, dict):
                continue
            name = (
                item.get("heroName") or item.get("hero_name") or item.get("name") or
                item.get("heroname") or item.get("Name") or item.get("HeroName") or ""
            )
            win_rate = self._parse_rate(
                item.get("winRate") or item.get("win_rate") or item.get("winrate") or
                item.get("WinRate") or item.get("win") or 0
            )
            pick_rate = self._parse_rate(
                item.get("pickRate") or item.get("pick_rate") or item.get("pickrate") or
                item.get("PickRate") or item.get("pick") or 0
            )
            ban_rate = self._parse_rate(
                item.get("banRate") or item.get("ban_rate") or item.get("banrate") or
                item.get("BanRate") or item.get("ban") or 0
            )
            if name and win_rate:
                results.append({"name": name, "win_rate": win_rate, "pick_rate": pick_rate, "ban_rate": ban_rate})

        return results

    def _parse_dom(self, page, debug=False):
        """Parse body text using the rank table structure visible on mobilelegends.com/rank.

        Observed pattern (each hero occupies 4 lines in body text):
          <rank_number>
          <hero_name_ru>
          <pick_rate>%
          <win_rate>%
          <ban_rate>%
        """
        body_text = page.inner_text("body")
        lines = [l.strip() for l in body_text.splitlines() if l.strip()]

        if debug:
            self.stdout.write(f"\n[DEBUG] Total body lines: {len(lines)}")
            self.stdout.write(f"[DEBUG] First 60 lines:\n" + "\n".join(f"  {i}: {l}" for i, l in enumerate(lines[:60])))

        results = self._parse_body_lines(lines, debug)

        if not results and debug:
            self.stdout.write(f"\n[DEBUG] Page title: {page.title()}")

        return results

    def _parse_body_lines(self, lines, debug=False):
        """Walk through body lines and pick up blocks: rank_num, name, pick%, win%, ban%."""
        results = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Detect a rank number (1-200)
            if re.match(r"^\d{1,3}$", line):
                rank = int(line)
                if rank < 1 or rank > 200:
                    i += 1
                    continue
                # Next non-empty line should be hero name
                j = i + 1
                # Collect up to 5 following lines and look for name + 3 percentages
                block = []
                while j < len(lines) and len(block) < 5:
                    block.append(lines[j])
                    j += 1
                percents = []
                name = None
                for part in block:
                    m = re.match(r"^(\d+\.?\d*)\s*%$", part)
                    if m:
                        percents.append(float(m.group(1)))
                    elif name is None and not re.match(r"^[\d.%\s]+$", part) and len(part) >= 2:
                        name = part
                if name and len(percents) >= 2:
                    # Column order on site: pick_rate, win_rate, ban_rate
                    results.append({
                        "name": name,
                        "pick_rate": percents[0] if len(percents) > 0 else None,
                        "win_rate": percents[1] if len(percents) > 1 else None,
                        "ban_rate": percents[2] if len(percents) > 2 else None,
                    })
                    if debug and len(results) <= 5:
                        self.stdout.write(
                            f"  #{rank} {name}: pick={percents[0] if percents else '?'}%  "
                            f"wr={percents[1] if len(percents)>1 else '?'}%  "
                            f"ban={percents[2] if len(percents)>2 else '?'}%"
                        )
                    i = j
                    continue
            i += 1
        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_rate(self, val):
        if not val:
            return None
        try:
            return float(str(val).replace("%", "").strip())
        except (ValueError, TypeError):
            return None

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
