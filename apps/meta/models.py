from django.db import models
from django.utils.text import slugify


class Role(models.Model):
    ROLE_CHOICES = [
        ("tank", "Танк"),
        ("fighter", "Боец"),
        ("assassin", "Убийца"),
        ("mage", "Маг"),
        ("marksman", "Стрелок"),
        ("support", "Саппорт"),
    ]
    slug = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True, primary_key=True)
    name_ru = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, default="")

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name_ru


class Hero(models.Model):
    DAMAGE_CHOICES = [
        ("physical", "Физический"),
        ("magic", "Магический"),
        ("mixed", "Смешанный"),
    ]
    PHASE_CHOICES = [
        ("early", "Ранняя игра"),
        ("mid", "Средняя игра"),
        ("late", "Поздняя игра"),
    ]
    MOBILITY_CHOICES = [
        ("high", "Высокая"),
        ("medium", "Средняя"),
        ("low", "Низкая"),
    ]

    name = models.CharField(max_length=100, unique=True)
    name_ru = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name="heroes")
    secondary_role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="heroes_secondary"
    )
    specialty = models.CharField(max_length=100, blank=True)
    release_patch = models.CharField(max_length=20, blank=True)
    is_free = models.BooleanField(default=False)
    image = models.ImageField(upload_to="heroes/", null=True, blank=True)
    icon = models.ImageField(upload_to="heroes/icons/", null=True, blank=True)

    damage_type = models.CharField(max_length=10, choices=DAMAGE_CHOICES, blank=True, default="", verbose_name="Тип урона")
    game_phase = models.CharField(max_length=10, choices=PHASE_CHOICES, blank=True, default="", verbose_name="Силён на стадии")
    mobility = models.CharField(max_length=10, choices=MOBILITY_CHOICES, blank=True, default="", verbose_name="Мобильность")
    has_cc = models.BooleanField(default=False, verbose_name="Есть контроль")
    has_sustain = models.BooleanField(default=False, verbose_name="Есть восстановление")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Герой"
        verbose_name_plural = "Герои"
        ordering = ["name"]

    def __str__(self):
        return self.name_ru or self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Patch(models.Model):
    version = models.CharField(max_length=20, unique=True)
    released_at = models.DateField()
    is_current = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Патч"
        verbose_name_plural = "Патчи"
        ordering = ["-released_at"]

    def __str__(self):
        return f"Патч {self.version}"

    def save(self, *args, **kwargs):
        # Только один патч может быть текущим
        if self.is_current:
            Patch.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class TierEntry(models.Model):
    TIER_CHOICES = [("S", "S"), ("A", "A"), ("B", "B"), ("C", "C")]

    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="tier_entries")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, related_name="tier_entries")
    tier = models.CharField(max_length=1, choices=TIER_CHOICES)
    votes_up = models.PositiveIntegerField(default=0)
    votes_down = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    win_rate  = models.FloatField(null=True, blank=True, verbose_name="Винрейт (%)")
    pick_rate = models.FloatField(null=True, blank=True, verbose_name="Пик-рейт (%)")
    ban_rate  = models.FloatField(null=True, blank=True, verbose_name="Бан-рейт (%)")

    class Meta:
        verbose_name = "Запись тирлиста"
        verbose_name_plural = "Записи тирлиста"
        unique_together = ("hero", "patch")
        ordering = ["tier", "-votes_up"]

    def __str__(self):
        return f"{self.hero} — {self.tier} ({self.patch.version})"

    @property
    def score(self):
        return self.votes_up - self.votes_down


class HeroCounter(models.Model):
    STRENGTH_CHOICES = [("hard", "Жёсткий"), ("soft", "Мягкий")]
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="countered_by_relations", verbose_name="Герой")
    countered_by = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="counters_relations", verbose_name="Контрится героем")
    strength = models.CharField(max_length=10, choices=STRENGTH_CHOICES, default="soft", verbose_name="Сила")

    class Meta:
        unique_together = ("hero", "countered_by")
        verbose_name = "Контр-пик"
        verbose_name_plural = "Контр-пики"

    def __str__(self):
        return f"{self.countered_by} → {self.hero} ({self.get_strength_display()})"


class HeroSynergy(models.Model):
    STRENGTH_CHOICES = [("strong", "Сильная"), ("moderate", "Умеренная")]
    hero_a = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="synergies_a", verbose_name="Герой A")
    hero_b = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="synergies_b", verbose_name="Герой B")
    strength = models.CharField(max_length=10, choices=STRENGTH_CHOICES, default="moderate", verbose_name="Сила")

    class Meta:
        unique_together = ("hero_a", "hero_b")
        verbose_name = "Синергия"
        verbose_name_plural = "Синергии"

    def __str__(self):
        return f"{self.hero_a} + {self.hero_b} ({self.get_strength_display()})"


class Item(models.Model):
    CATEGORY_CHOICES = [
        ("attack",   "Атака"),
        ("defense",  "Защита"),
        ("magic",    "Магия"),
        ("movement", "Передвижение"),
        ("jungle",   "Джунгли"),
        ("roaming",  "Поддержка"),
    ]

    name        = models.CharField(max_length=100, unique=True, verbose_name="Название (EN)")
    name_ru     = models.CharField(max_length=100, verbose_name="Название")
    slug        = models.SlugField(max_length=120, unique=True)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория")
    description = models.TextField(blank=True, verbose_name="Описание")
    icon        = models.ImageField(upload_to="items/", null=True, blank=True, verbose_name="Иконка")
    price       = models.PositiveIntegerField(default=0, verbose_name="Цена (золото)")
    patch       = models.ForeignKey(
        Patch, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="items", verbose_name="Добавлен в патче"
    )

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ["category", "name_ru"]

    def __str__(self):
        return self.name_ru or self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class HeroVote(models.Model):
    """Голос пользователя за тир героя."""
    user = models.ForeignKey(
        "profile.SiteUser", on_delete=models.CASCADE, related_name="hero_votes"
    )
    tier_entry = models.ForeignKey(TierEntry, on_delete=models.CASCADE, related_name="votes")
    is_upvote = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "tier_entry")
        verbose_name = "Голос"
        verbose_name_plural = "Голоса"
