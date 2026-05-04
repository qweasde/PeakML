from django.db import models
from django.utils.text import slugify


class GuideSeries(models.Model):
    """Серия гайдов (напр. «Гайды по ролям»)."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField(blank=True)
    role = models.ForeignKey(
        "meta.Role", on_delete=models.SET_NULL, null=True, blank=True, related_name="guide_series"
    )
    order = models.PositiveSmallIntegerField(default=0)
    cover = models.ImageField(upload_to="guides/covers/", null=True, blank=True)

    class Meta:
        verbose_name = "Серия гайдов"
        verbose_name_plural = "Серии гайдов"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class Guide(models.Model):
    DIFFICULTY_CHOICES = [
        ("beginner", "Новичок"),
        ("intermediate", "Средний"),
        ("advanced", "Продвинутый"),
    ]

    series = models.ForeignKey(
        GuideSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="guides"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    excerpt = models.TextField(max_length=400, blank=True)
    content = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="beginner")
    cover = models.ImageField(upload_to="guides/", null=True, blank=True)
    published = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Гайд"
        verbose_name_plural = "Гайды"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_content_html(self):
        import markdown
        return markdown.markdown(self.content, extensions=["fenced_code", "tables", "nl2br"])


class GlossaryTerm(models.Model):
    term = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=120)
    definition = models.TextField()
    example = models.TextField(blank=True)

    class Meta:
        verbose_name = "Термин словаря"
        verbose_name_plural = "Словарь"
        ordering = ["term"]

    def __str__(self):
        return self.term

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.term)
        super().save(*args, **kwargs)
