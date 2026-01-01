# -----------------------------------------------------
# REQUIRED IMPORTS (All Correct Django Best Practices)
# -----------------------------------------------------
from django.db import models
from users.models.user import CustomUser
from django.conf import settings
from users.validators.validators import (
    mobile_validator,
)


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        null=True,  # Make sure this allows null for default records
        blank=True,
    )

    name = models.CharField(max_length=200)
    employee_code = models.CharField(max_length=50, unique=True)
    contact_phone = models.CharField(
        max_length=10, validators=[mobile_validator], unique=True
    )
    designation = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True, null=True)
    is_profile_completed = models.BooleanField(default=False)
    # ---- 5 Dummy Fields ----
    dummy1 = models.CharField(max_length=100, blank=True, null=True)
    dummy2 = models.CharField(max_length=100, blank=True, null=True)
    dummy3 = models.CharField(max_length=100, blank=True, null=True)
    dummy4 = models.CharField(max_length=100, blank=True, null=True)
    dummy5 = models.CharField(max_length=100, blank=True, null=True)

    is_active = models.BooleanField(default=False)
    joining_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.employee_code})"
