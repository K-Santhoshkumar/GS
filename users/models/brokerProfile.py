# users/models/brokerProfile.py

import os
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

# =====================================================================
#               FILE VALIDATORS (MIGRATION-SAFE, NO INNER FUNCS)
# =====================================================================

PDF_IMG_EXT = ["pdf", "png", "jpg", "jpeg", "gif"]

""" 
class MigrationSafeFileValidators:
    
    #Migration-safe validator for file size + extension.
    #Safe against missing files on disk (won't raise FileNotFoundError during size check).
    

    def __init__(self, max_kb, allowed_exts):
        self.max_kb = int(max_kb)
        # store a copy for deconstruct to serialize
        self.allowed_exts = [ext.lower() for ext in allowed_exts]

    def __call__(self, file_obj):
        # file_obj can be None / empty string etc.
        if not file_obj:
            return

        # --- Size check ---
        try:
            size = None
            # FileField FieldFile exposes .size via storage.size(name)
            # but storage.size can raise if file not present on disk.
            size = getattr(file_obj, "size", None)
            # if .size is None try to compute via file-like object
            if size is None and hasattr(file_obj, "file"):
                try:
                    file_obj.file.seek(0, os.SEEK_END)
                    size = file_obj.file.tell()
                    file_obj.file.seek(0)
                except Exception:
                    size = None
        except Exception:
            # If we cannot determine size (missing file, storage error), skip size validation.
            size = None

        if size is not None:
            if size > self.max_kb * 1024:
                raise ValidationError(f"File size must be <= {self.max_kb} KB")

        # --- Extension check ---
        try:
            name = getattr(file_obj, "name", None)
            if name:
                ext = os.path.splitext(name)[1].lstrip(".").lower()
                if ext and ext not in self.allowed_exts:
                    raise ValidationError(
                        f"Allowed file types: {', '.join(self.allowed_exts)}"
                    )
        except Exception:
            # be tolerant if file object doesn't expose name
            return

    def deconstruct(self):
        return (
            "users.models.brokerProfile.MigrationSafeFileValidators",
            [self.max_kb, list(self.allowed_exts)],
            {},
        )

    def __repr__(self):
        return f"MigrationSafeFileValidators(max_kb={self.max_kb}, allowed_exts={self.allowed_exts})"


# ==============================================================
#                     AUTO-FOLDER CREATOR
# ==============================================================


def ensure_upload_folder(path: str):
    #Automatically creates MEDIA_ROOT/upload_to folder if missing.
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    directory = os.path.dirname(full_path)

    # Create full directory structure
    os.makedirs(directory, exist_ok=True)

    return path
 """

# =====================================================================
#                             CONSTANTS
# =====================================================================

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


# =====================================================================
#                           BROKER MODEL
# =====================================================================


class BrokerProfile(models.Model):

    # --- User Link ---
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="broker_profile",
    )

    # --- Identity ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account_type = models.CharField(
        max_length=30, choices=ACCOUNT_TYPES, default="individual", db_index=True
    )
    status = models.CharField(max_length=30, default="draft")
    is_active = models.BooleanField(default=True)

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
        ]
        verbose_name = "Broker profile"
        verbose_name_plural = "Broker profiles"

    def __str__(self):
        return f"{self.contact_name} ({self.account_type})"
