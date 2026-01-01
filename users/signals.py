from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from users.models.brokerProfile import BrokerProfile
from users.models.customerProfile import CustomerProfile
from users.models.employeeProfile import EmployeeProfile
from users.utils.dummy_relations import get_default_broker, get_default_employee

User = get_user_model()
DEFAULT_PHONE = "9999999999"


# ==========================================================
# CREATE PROFILES ON USER CREATION
# ==========================================================
@receiver(post_save, sender=User)
def create_profiles(sender, instance, created, **kwargs):
    if not created or instance.is_superuser:
        return

    role = (instance.role or "CUSTOMER").upper()

    with transaction.atomic():
        if role == "BROKER" and not hasattr(instance, "broker_profile"):
            BrokerProfile.objects.create(
                user=instance,
                contact_name=instance.get_full_name() or instance.username,
                contact_email=instance.email,
                contact_phone=DEFAULT_PHONE,
            )

        elif role == "CUSTOMER" and not hasattr(instance, "customer_profile"):
            CustomerProfile.objects.create(
                user=instance,
                name=instance.get_full_name() or instance.username,
                email=instance.email,
                contact_phone=DEFAULT_PHONE,
                
            )

        elif role == "EMPLOYEE" and not hasattr(instance, "employee_profile"):
            EmployeeProfile.objects.create(
                user=instance,
                name=instance.get_full_name() or instance.username,
                email=instance.email,
                contact_phone=DEFAULT_PHONE,
            )


# ==========================================================
# SYNC CUSTOMER PROFILE → USER
# ==========================================================
@receiver(post_save, sender=CustomerProfile)
def sync_customer_profile_to_user(sender, instance, **kwargs):
    user = instance.user
    update_fields = []

    if instance.name:
        parts = instance.name.strip().split(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else ""

        if user.first_name != first:
            user.first_name = first
            update_fields.append("first_name")

        if user.last_name != last:
            user.last_name = last
            update_fields.append("last_name")

    if instance.email and user.email != instance.email:
        user.email = instance.email
        update_fields.append("email")

    if update_fields:
        user.save(update_fields=update_fields)


# ==========================================================
# SYNC BROKER PROFILE → USER
# ==========================================================
@receiver(post_save, sender=BrokerProfile)
def sync_broker_profile_to_user(sender, instance, **kwargs):
    user = instance.user
    update_fields = []

    if instance.contact_name:
        parts = instance.contact_name.strip().split(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else ""

        if user.first_name != first:
            user.first_name = first
            update_fields.append("first_name")

        if user.last_name != last:
            user.last_name = last
            update_fields.append("last_name")

    if instance.contact_email and user.email != instance.contact_email:
        user.email = instance.contact_email
        update_fields.append("email")

    if update_fields:
        user.save(update_fields=update_fields)


# ==========================================================
# SYNC EMPLOYEE PROFILE → USER  ✅ (THIS WAS MISSING)
# ==========================================================
@receiver(post_save, sender=EmployeeProfile)
def sync_employee_profile_to_user(sender, instance, **kwargs):
    user = instance.user
    update_fields = []

    if instance.name:
        parts = instance.name.strip().split(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else ""

        if user.first_name != first:
            user.first_name = first
            update_fields.append("first_name")

        if user.last_name != last:
            user.last_name = last
            update_fields.append("last_name")

    if instance.email and user.email != instance.email:
        user.email = instance.email
        update_fields.append("email")

    if update_fields:
        user.save(update_fields=update_fields)
