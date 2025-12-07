from django.db import models
from django.contrib.auth.models import AbstractUser


# ------------------------------------------------------------------------------
#   CUSTOM USER
# ------------------------------------------------------------------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("CUSTOMER", "Customer"),
        ("BROKER", "Broker"),
        ("EMPLOYEE", "Employee"),
        ("ADMIN", "Admin"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="CUSTOMER")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
