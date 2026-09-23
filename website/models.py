from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    """
    A single editing service offered publicly (spec section 8).
    `category` drives the /services/?category=... filter that stands
    in for separate "Academic Editing" / "Scientific Editing" pages —
    see Phase 3 design notes. Admin-editable so new services don't
    require a code deploy (spec section 32).
    """

    class Category(models.TextChoices):
        ACADEMIC = "ACADEMIC", _("Academic Editing")
        SCIENTIFIC = "SCIENTIFIC", _("Scientific Editing")

    class PricingModel(models.TextChoices):
        PER_WORD = "PER_WORD", _("Per word")
        PER_PAGE = "PER_PAGE", _("Per page")
        PER_HOUR = "PER_HOUR", _("Per hour")
        FLAT_FEE = "FLAT_FEE", _("Flat fee")
        CUSTOM = "CUSTOM", _("Custom quote")

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    pricing_model = models.CharField(max_length=20, choices=PricingModel.choices)
    minimum_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SubjectArea(models.Model):
    """
    A subject/discipline area (spec section 9), used both on the public
    site and later to match assignments to editors by expertise.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("subject area")
        verbose_name_plural = _("subject areas")
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)