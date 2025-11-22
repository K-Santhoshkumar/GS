from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    BrokerOnboarding,
    CustomerOnboarding,
    EmployeeOnboarding,
)

User = get_user_model()

FALLBACK_PHONE = "0000000000"


# -----------------------------------------------------
# Helper Functions
# -----------------------------------------------------
def _display_name(user):
    """
    Pick a readable display name.
    """
    return user.get_full_name() or user.username or user.email.split("@")[0]


def _phone_value(user):
    """
    Use user's phone if available; fallback otherwise.
    """
    return getattr(user, "phone", None) or FALLBACK_PHONE


# -----------------------------------------------------
# Create / Update Customer Onboarding
# -----------------------------------------------------
def _ensure_customer_onboarding(user):
    name = _display_name(user)
    phone = _phone_value(user)

    onboarding, created = CustomerOnboarding.objects.get_or_create(
        customer_email=user.email,
        defaults={
            "customer_name": name,
            "customer_phone": phone,
        },
    )

    if not created:
        onboarding.customer_name = name
        onboarding.customer_phone = phone
        onboarding.save(update_fields=["customer_name", "customer_phone", "updated_at"])


# -----------------------------------------------------
# Create / Update Broker Onboarding
# -----------------------------------------------------
def _ensure_broker_onboarding(user):
    name = _display_name(user)
    phone = _phone_value(user)

    onboarding, created = BrokerOnboarding.objects.get_or_create(
        contact_email=user.email,
        defaults={
            "contact_name": name,
            "contact_phone": phone,
        },
    )

    if not created:
        onboarding.contact_name = name
        onboarding.contact_phone = phone
        onboarding.save(update_fields=["contact_name", "contact_phone", "updated_at"])


# -----------------------------------------------------
# Create / Update Employee Onboarding
# -----------------------------------------------------
def _ensure_employee_onboarding(user):
    name = _display_name(user)
    phone = _phone_value(user)

    onboarding, created = EmployeeOnboarding.objects.get_or_create(
        employee_email=user.email,
        defaults={
            "employee_name": name,
            "employee_phone": phone,
        },
    )

    if not created:
        onboarding.employee_name = name
        onboarding.employee_phone = phone
        onboarding.save(update_fields=["employee_name", "employee_phone", "updated_at"])


# -----------------------------------------------------
# MAIN SIGNAL — RUNS ONLY WHEN A NEW USER IS CREATED
# -----------------------------------------------------
@receiver(post_save, sender=User)
def sync_user_onboarding(sender, instance, created, **kwargs):
    """
    Automatically create onboarding record based on the user's role.
    Runs ONLY on first save of a new user (created=True).
    """
    if not created:
        return

    # Normalize the role field (avoid case issues, missing role, etc.)
    role = getattr(instance, "role", "CUSTOMER")
    role = (role or "CUSTOMER").upper()

    # Debug (optional):
    # print("SIGNAL TRIGGERED FOR ROLE:", role)

    if role == "BROKER":
        _ensure_broker_onboarding(instance)
    elif role == "EMPLOYEE":
        _ensure_employee_onboarding(instance)
    else:
        _ensure_customer_onboarding(instance)
