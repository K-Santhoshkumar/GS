from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class BaseProvider(models.Model):
    """
    Abstract base model for PMS / AIF Providers
    """

    # Basic identity
    name = models.CharField(max_length=200)
    shortname = models.CharField(
        max_length=50,
        unique=True,
        help_text="Short code for provider mapping (e.g., ICICI, HDFC, AXIS)"
    )

    logo_url = models.URLField(max_length=500, blank=True, null=True)

    # Address details
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=100, default="India", null=True)

    # Contact details
    contact_person_name = models.CharField(max_length=200, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    # Provider-level controls
    is_whitelisted = models.BooleanField(default=False, db_index=True)

    priority = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Priority from 1 (highest) to 5 (lowest)"
    )

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["priority", "name"]
        indexes = [
            models.Index(fields=["is_whitelisted", "priority"]),
            models.Index(fields=["shortname"]),
        ]

    def __str__(self):
        return self.name



class PMSProvider(BaseProvider):
    """
    Model for PMS Providers
    """

    class Meta(BaseProvider.Meta):
        verbose_name = "PMS Provider"
        verbose_name_plural = "PMS Providers"


class AIFProvider(BaseProvider):
    """
    Model for AIF Providers
    """

    class Meta(BaseProvider.Meta):
        verbose_name = "AIF Provider"
        verbose_name_plural = "AIF Providers"