from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.meta.models import Role, Hero, Patch, TierEntry


ROLES = [
    ("tank", "Танк", "shield"),
    ("fighter", "Боец", "swords"),
    ("assassin", "Убийца", "zap"),
    ("mage", "Маг", "sparkles"),
    ("marksman", "Стрелок", "crosshair"),
    ("support", "Саппорт", "heart"),
]

HEROES = [
    # (name, name_ru, role_slug, secondary_role_slug|None, specialty, is_free)
    ("Chou", "Чоу", "fighter", "assassin", "Control/Charge", True),
    ("Layla", "Лайла", "marksman", None, "Reap", True),
    ("Tigreal", "Тигреал", "tank", None, "Crowd Control/Initiator", True),
    ("Nana", "Нана", "support", "mage", "Crowd Control/Poke", True),
    ("Balmond", "Болмонд", "fighter", None, "Damage", True),
    ("Saber", "Сейбер", "assassin", None, "Burst Damage/Finisher", True),
    ("Lapu-Lapu", "Лапу-Лапу", "fighter", None, "Charge/Burst", False),
    ("Eudora", "Эудора", "mage", None, "Burst Damage", True),
    ("Alucard", "Алукард", "fighter", "assassin", "Damage/Lifesteal", True),
    ("Kagura", "Кагура", "mage", None, "Poke/Burst Damage", False),
    ("Lancelot", "Лансело", "assassin", None, "Burst Damage/Reap", False),
    ("Ling", "Линг", "assassin", None, "Damage/Mobility", False),
    ("Lunox", "Люнокс", "mage", None, "Burst/Sustain Mage", False),
    ("Gusion", "Гюзен", "assassin", "mage", "Burst Damage", False),
    ("Cici", "Сиси", "fighter", None, "Damage/Durable", False),
    ("Fredrinn", "Фредрин", "fighter", "tank", "Durable/Charge", False),
    ("Arlott", "Арлотт", "fighter", "assassin", "Reap/Damage", False),
    ("Vale", "Вейл", "mage", None, "Burst Damage/Poke", False),
    ("Leomord", "Леомурд", "fighter", None, "Charge/Damage", False),
    ("Jawhead", "Джохед", "fighter", "tank", "Crowd Control/Initiator", False),
    ("Mathilda", "Матильда", "support", "assassin", "Speed Up/Mobility", False),
    ("Atlas", "Атлас", "tank", None, "Crowd Control/Initiator", False),
    ("Khufra", "Хуфра", "tank", None, "Crowd Control/Initiator", False),
    ("Claude", "Клод", "marksman", "assassin", "Damage/Burst", False),
    ("Beatrix", "Беатрис", "marksman", None, "Damage", False),
    ("Yi Sun-shin", "Ли Сун Шин", "marksman", "assassin", "Damage/Poke", False),
    ("Fanny", "Фэнни", "assassin", None, "Damage/Mobility", False),
    ("Cyclops", "Циклоп", "mage", None, "Burst Damage/Poke", True),
    ("Rafaela", "Рафаэль", "support", None, "Heal/Speed Up", True),
    ("Johnson", "Джонсон", "tank", None, "Crowd Control/Initiator", False),
]

TIER_DATA = {
    "S": ["Ling", "Kagura", "Lancelot", "Mathilda", "Atlas"],
    "A": ["Gusion", "Chou", "Khufra", "Fanny", "Beatrix", "Lunox", "Vale"],
    "B": ["Lapu-Lapu", "Claude", "Yi Sun-shin", "Leomord", "Fredrinn", "Johnson", "Arlott"],
    "C": ["Cici", "Jawhead", "Cyclops", "Eudora", "Balmond", "Layla", "Alucard"],
}


class Command(BaseCommand):
    help = "Засеять начальные данные: роли, герои, патч, тирлист"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Очистить все данные перед засевом")

    def handle(self, *args, **options):
        if options["reset"]:
            TierEntry.objects.all().delete()
            Hero.objects.all().delete()
            Patch.objects.all().delete()
            Role.objects.all().delete()
            self.stdout.write(self.style.WARNING("Данные очищены"))

        # Roles
        role_map = {}
        for slug, name_ru, icon in ROLES:
            role, created = Role.objects.get_or_create(slug=slug, defaults={"name_ru": name_ru, "icon": icon})
            if not created:
                role.name_ru = name_ru
                role.icon = icon
                role.save()
            role_map[slug] = role
        self.stdout.write(f"  Роли: {len(role_map)} шт.")

        # Patch
        patch, _ = Patch.objects.get_or_create(
            version="1.9.04",
            defaults={"released_at": "2025-04-15", "is_current": True, "notes": "Текущий патч"},
        )
        if not patch.is_current:
            patch.is_current = True
            patch.save()
        self.stdout.write(f"  Патч: {patch}")

        # Heroes
        hero_map = {}
        for name, name_ru, role_slug, sec_slug, specialty, is_free in HEROES:
            hero, _ = Hero.objects.get_or_create(
                name=name,
                defaults={
                    "name_ru": name_ru,
                    "role": role_map.get(role_slug),
                    "secondary_role": role_map.get(sec_slug) if sec_slug else None,
                    "specialty": specialty,
                    "is_free": is_free,
                },
            )
            hero_map[name] = hero
        self.stdout.write(f"  Герои: {len(hero_map)} шт.")

        # Tier entries
        created_count = 0
        for tier, names in TIER_DATA.items():
            for name in names:
                hero = hero_map.get(name)
                if not hero:
                    self.stdout.write(self.style.WARNING(f"  Герой не найден: {name}"))
                    continue
                _, created = TierEntry.objects.get_or_create(
                    hero=hero, patch=patch, defaults={"tier": tier}
                )
                if created:
                    created_count += 1
        self.stdout.write(f"  Тир-записи: {created_count} создано")

        self.stdout.write(self.style.SUCCESS("Данные засеяны успешно!"))
