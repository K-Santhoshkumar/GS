# users/models/brokerProfile.py
import random
import string
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from users.models.employeeProfile import EmployeeProfile
from django.utils.translation import gettext_lazy as _
from users.validators.validators import (
    pan_validator,
    mobile_validator,
    MigrationSafeFileValidators,
)

PDF_IMG_EXT = ["pdf", "png", "jpg", "jpeg", "gif"]


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

class BrokerProfile(models.Model):

    # --- User Link ---
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="broker_profile",
    )
    broker_code = models.CharField(
        max_length=6,
        unique=True,
        editable=False,
        db_index=True,
        null=True,      # REQUIRED for now
        blank=True,
    )

    # --- Identity ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account_type = models.CharField(
        max_length=30, choices=ACCOUNT_TYPES, default="individual", db_index=True
    )
    status = models.CharField(max_length=30, default="draft")
    is_active = models.BooleanField(default=False)
    is_profile_completed = models.BooleanField(default=False)
    # --- Contact Info ---
    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(
        max_length=10, validators=[mobile_validator], unique=True
    )
    official_designation = models.CharField(max_length=200, blank=True, null=True)

    # --- ARN ---
    arn_code = models.CharField(max_length=100, blank=True, null=True)
    arn_document = models.FileField(
        upload_to="onboarding/arn/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
    )
    arn_expiry_date = models.DateField(blank=True, null=True)

    # --- APRN ---
    aprn_code = models.CharField(max_length=100, blank=True, null=True)
    aprn_document = models.FileField(
        upload_to="onboarding/aprn/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
    )
    aprn_expiry_date = models.DateField(blank=True, null=True)

    # --- Products Allowed ---
    products_allowed = models.JSONField(default=list, blank=True)

    # --- PAN ---
    pan_number = models.CharField(
        max_length=10,
        validators=[pan_validator],
        unique=True,
        blank=True,
        null=True,
    )
    pan_document = models.FileField(
        upload_to="onboarding/pan/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
    )

    # --- Bank ---
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=64, blank=True, null=True)
    bank_ifsc = models.CharField(max_length=20, blank=True, null=True)
    cancelled_cheque = models.FileField(
        upload_to="onboarding/cheques/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
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
    )

    # --- Agreement ---
    agreement_document = models.FileField(
        upload_to="onboarding/agreements/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(600, ["pdf"])],
    )

    # --- Entity Documents ---
    moa_aoa = models.FileField(
        upload_to="onboarding/entity_docs/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
    )
    board_resolution = models.FileField(
        upload_to="onboarding/entity_docs/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
    )
    partnership_deed = models.FileField(
        upload_to="onboarding/entity_docs/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
    )

    # --- GST ---
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    gst_document = models.FileField(
        upload_to="onboarding/gst/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
    )

    # --- Review Metadata ---
    notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_brokers",
    )

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="broker_profiles",
    )

    reviewed_at = models.DateTimeField(blank=True, null=True)
    review_comments = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["account_type"]),
            models.Index(fields=["pan_number"]),
            models.Index(fields=["broker_code"]),
        ]
        ordering = ["-id"]
        verbose_name = "Broker profile"
        verbose_name_plural = "Broker profiles"

    # -------- Broker Code Generator --------
    def _generate_broker_code(self):
        letters = "".join(random.choices(string.ascii_uppercase, k=2))
        digits = "".join(random.choices(string.digits, k=3))
        return f"B{letters}{digits}"

    def save(self, *args, **kwargs):
        if not self.broker_code:
            while True:
                code = self._generate_broker_code()
                if not BrokerProfile.objects.filter(broker_code=code).exists():
                    self.broker_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.broker_code} - {self.contact_name}"
