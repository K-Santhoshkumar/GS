from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .providers import AIFProvider, PMSProvider


class BaseScheme(models.Model):
    """
    Abstract base model for PMS / AIF Schemes
    """

    # ===== Core Scheme Identity =====
    ia_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Investment Advisor / Scheme Name"
    )
    strategy_name = models.CharField(max_length=255, blank=True, null=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    benchmark_name = models.CharField(max_length=255, blank=True, null=True)

    open_ended_yes_no = models.BooleanField(
        blank=True,
        null=True,
        help_text="Is the scheme open-ended?"
    )
    expected_tenor = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Expected tenor of the scheme"
    )

    # ===== AUM & Investment =====
    aum = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Assets Under Management"
    )
    min_inv_amount = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Minimum Investment Amount"
    )

    # ===== Returns =====
    one_month_return = models.FloatField(blank=True, null=True)
    one_month_benchmark_return = models.FloatField(blank=True, null=True)

    three_month_return = models.FloatField(blank=True, null=True)
    three_month_benchmark_return = models.FloatField(blank=True, null=True)

    six_month_return = models.FloatField(blank=True, null=True)
    six_month_benchmark_return = models.FloatField(blank=True, null=True)

    one_year_return = models.FloatField(blank=True, null=True)
    one_year_benchmark_return = models.FloatField(blank=True, null=True)

    three_year_return = models.FloatField(blank=True, null=True)
    three_year_benchmark_return = models.FloatField(blank=True, null=True)

    five_year_return = models.FloatField(blank=True, null=True)
    five_year_benchmark_return = models.FloatField(blank=True, null=True)
    

    si_return = models.FloatField(
        blank=True,
        null=True,
        help_text="Since Inception Return"
    )
    si_benchmark_return = models.FloatField(
        blank=True,
        null=True,
        help_text="Since Inception Benchmark Return"
    )

    # ===== Fund Details =====
    date_of_inception = models.DateField(blank=True, null=True)
    age = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    fund_managers = models.TextField(blank=True, null=True)

    # ===== Fee Structure =====
    setup_fees = models.TextField(blank=True, null=True)
    fixed_fees = models.TextField(blank=True, null=True)
    variable_fees = models.TextField(blank=True, null=True)
    
    carry = models.TextField(blank=True, null=True)
    hurdle = models.TextField(blank=True, null=True)
    catch_up = models.BooleanField(blank=True, null=True)
    
    exit_load = models.CharField(max_length=255, blank=True, null=True)

    # ===== Strategy / Purpose =====
    purpose = models.TextField(blank=True, null=True)

    # ===== Display & Investment Controls =====
    
    sheet_type = models.CharField(
    max_length=50,
    blank=True,
    null=True,
    help_text="Excel sheet name used for uploading this scheme’s data."
)
    open_for_investment = models.BooleanField(default=True)

    # ===== Internal Controls =====
    is_shortlisted = models.BooleanField(default=False, db_index=True)
    scheme_priority = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Scheme priority from 1 (highest) to 5 (lowest)"
    )

    # ===== Metadata =====
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["scheme_priority", "ia_name"]
        indexes = [
            models.Index(fields=["is_shortlisted", "scheme_priority"]),
        ]

    @property
    def effective_priority(self):
        """
        Combines provider priority and scheme priority
        Lower number = higher priority
        """
        provider_priority = getattr(self.provider, "priority", 5)
        scheme_priority = self.scheme_priority or 5
        return (provider_priority * 10) + scheme_priority



class AIFScheme(BaseScheme):
    provider = models.ForeignKey(
        AIFProvider,
        on_delete=models.CASCADE,
        related_name="schemes",
        to_field="shortname",
        db_column="provider_shortname",
    )

    # AIF-specific fields
    capital_called_percent = models.FloatField(
        blank=True,
        null=True,
        help_text="Capital Called Percentage"
    )

    aif_category = models.CharField(
        max_length=255,
        choices=[
            ("CAT1", "Category I"),
            ("CAT2", "Category II"),
            ("CAT3", "Category III"),
            
        ],
        blank=True,
        null=True,
    )

    class Meta(BaseScheme.Meta):
        verbose_name = "AIF Scheme"
        verbose_name_plural = "AIF Schemes"

    def __str__(self):
        provider_name = self.provider.name if self.provider else "Unknown"
        return f"{provider_name} - {self.ia_name}"

#==== PMS Scheme Model inherits from base model ====#

class PMSScheme(BaseScheme):
    provider = models.ForeignKey(
        PMSProvider,
        on_delete=models.CASCADE,
        related_name="schemes",
        to_field="shortname",
        db_column="provider_shortname",
    )
  # ===== External IDs & Links =====

    ia_id = models.IntegerField(blank=True, null=True)
    ia_link = models.URLField(max_length=500, blank=True, null=True)
    source_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta(BaseScheme.Meta):
        verbose_name = "PMS Scheme"
        verbose_name_plural = "PMS Schemes"
        indexes = BaseScheme.Meta.indexes + [
            models.Index(fields=["ia_id"]),
        ]

    def __str__(self):
        provider_name = self.provider.name if self.provider else "Unknown"
        return f"{provider_name} - {self.ia_name}"