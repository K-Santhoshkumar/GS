from django.conf import settings
from django.db import models
from users.validators import PDF_IMG_EXT
from users.validators.wrappers import MigrationSafeFileValidators
from django.utils.translation import gettext_lazy as _


# -----------------------
# Choices / constants
# -----------------------
ACCOUNT_TYPES = [
    ("individual", "Individual"),
    ("proprietorship", "Proprietorship"),
    ("partnership", "Partnership"),
    ("pvt_ltd", "Private Limited Company"),
    ("llp", "LLP"),
    ("others", "Others"),
]

PRODUCT_CHOICES = [
    ("mutual_funds", "Mutual Funds"),
    ("pms", "PMS"),
    ("aif", "AIF"),
    ("lamf", "LAMF"),
    ("insurance", "Insurance"),
]


# -----------------------
# Model
# -----------------------
class CustomerOnboarding(models.Model):
    # --- Identity / Meta ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account_type = models.CharField(
        max_length=30, choices=ACCOUNT_TYPES, default="individual", db_index=True
    )
    status = models.CharField(max_length=30, default="draft")
    is_active = models.BooleanField(default=True)

    # --- Personal / Contact details ---
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=40)
    official_designation = models.CharField(max_length=200, blank=True, null=True)

    # --- ARN / APRN ---
    arn_code = models.CharField(
        max_length=100, blank=True, null=True, help_text="ARN code (AMFI/ARN)"
    )
    arn_document = models.FileField(
        upload_to="onboarding/arn/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
        help_text="PDF/Image, <= 500KB",
    )
    arn_expiry_date = models.DateField(blank=True, null=True)

    aprn_code = models.CharField(
        max_length=100, blank=True, null=True, help_text="APRN code (if any)"
    )
    aprn_document = models.FileField(
        upload_to="onboarding/aprn/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
        help_text="PDF/Image, <= 500KB",
    )
    aprn_expiry_date = models.DateField(blank=True, null=True)

    # --- Products allowed ---
    products_allowed = models.JSONField(
        default=list, help_text="List of allowed products", blank=True
    )

    # --- PAN / KYC ---
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    pan_document = models.FileField(
        upload_to="onboarding/pan/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, ["pdf", "png", "jpg", "jpeg"])],
        help_text="PDF/Image, <= 500KB",
    )

    # --- Bank details ---
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=64, blank=True, null=True)
    bank_ifsc = models.CharField(max_length=20, blank=True, null=True)
    cancelled_cheque = models.FileField(
        upload_to="onboarding/cheques/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
        help_text="PDF/Image, <= 500KB",
    )

    # --- Address ---
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    state = models.CharField(max_length=120, blank=True, null=True)
    pincode = models.CharField(max_length=12, blank=True, null=True)
    country = models.CharField(max_length=80, default="India")

    address_proof = models.FileField(
        upload_to="onboarding/address_proofs/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
        help_text="PDF/Image, <= 500KB",
    )

    # --- Agreement / Contracts ---
    agreement_document = models.FileField(
        upload_to="onboarding/agreements/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(600, ["pdf"])],
        help_text="PDF only, <= 600KB",
    )

    # --- Entity-specific documents ---
    moa_aoa = models.FileField(
        upload_to="onboarding/entity_docs/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
        help_text="MOA/AOA or Incorporation docs, <= 500KB",
    )
    board_resolution = models.FileField(
        upload_to="onboarding/entity_docs/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
        help_text="Board Resolution authorising signatory",
    )
    partnership_deed = models.FileField(
        upload_to="onboarding/entity_docs/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
        help_text="Partnership deed or LLP agreement",
    )

    # --- GST ---
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    gst_document = models.FileField(
        upload_to="onboarding/gst/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
    )

    # --- Authorized Signatory ---
    auth_signatory_name = models.CharField(max_length=255, blank=True, null=True)
    auth_signatory_email = models.EmailField(blank=True, null=True)
    auth_signatory_phone = models.CharField(max_length=40, blank=True, null=True)
    auth_signatory_pan = models.CharField(max_length=20, blank=True, null=True)
    auth_signatory_kyc = models.FileField(
        upload_to="onboarding/signatory_kyc/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
    )

    # --- Extra metadata ---
    notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    review_comments = models.TextField(blank=True, null=True)

    # --- Dummy fields (requested) ---
    dummy1 = models.CharField(max_length=100, blank=True, null=True)
    dummy2 = models.CharField(max_length=100, blank=True, null=True)
    dummy3 = models.CharField(max_length=100, blank=True, null=True)
    dummy4 = models.CharField(max_length=100, blank=True, null=True)
    dummy5 = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["account_type"]),
            models.Index(fields=["pan_number"]),
        ]
        verbose_name = "Customer Onboarding"
        verbose_name_plural = "Customer Onboardings"

    def __str__(self):
        return f"{self.customer_name} ({self.account_type})"
