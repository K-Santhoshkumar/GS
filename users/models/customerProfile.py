from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, FileExtensionValidator
from users.utils.dummy_relations import get_default_employee, get_default_broker
from users.models.brokerProfile import BrokerProfile
from users.models.employeeProfile import EmployeeProfile
from users.validators.validators import (
    pan_validator,
    mobile_validator,
    MigrationSafeFileValidators,
)


class CustomerProfile(models.Model):
    # validators
    """pan_validator = RegexValidator(
        regex=r"^[A-Z]{5}[0-9]{4}[A-Z]$",
        message="Enter a valid PAN (e.g. ABCDE1234F). Use uppercase letters.",
    )
    mobile_validator = RegexValidator(
        regex=r"^[6-9]\d{9}$",
        message="Enter a valid 10-digit Indian mobile number starting with 6-9.",
    )"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # delete profile when user deleted
        related_name="customer_profile",
    )

    name = models.CharField(max_length=200)
    pan = models.CharField(max_length=10, validators=[pan_validator], unique=True)
    contact_phone = models.CharField(
        max_length=10, validators=[mobile_validator], unique=True
    )
    email = models.EmailField(blank=True, null=True)

    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    pan_copy = models.FileField(
        upload_to="uploads/pan/",
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
        blank=True,
        null=True,
    )
    address_proof = models.FileField(
        upload_to="uploads/address/",
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
        blank=True,
        null=True,
    )

    # RELATIONSHIPS
    broker = models.ForeignKey(
        BrokerProfile,
        on_delete=models.SET_NULL,
        null=True,
        default=get_default_broker,
        related_name="customers",
    )

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        default=get_default_employee,
        related_name="customers",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["pan"]),
            models.Index(fields=["contact_phone"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.pan})"
