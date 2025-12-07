from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from users.models.brokerProfile import BrokerProfile
from users.models.employeeProfile import EmployeeProfile
from users.models.customerProfile import CustomerProfile
from users.utils.dummy_relations import get_default_broker, get_default_employee

User = get_user_model()
DEFAULT_PHONE = "0000000000"


@receiver(post_save, sender=User)
def create_onboarding_for_user(sender, instance, created, **kwargs):
    if not created or instance.is_superuser:
        return

    role = (getattr(instance, "role", "CUSTOMER") or "CUSTOMER").upper()

    with transaction.atomic():
        if role == "BROKER" and not hasattr(instance, "broker_profile"):
            BrokerProfile.objects.create(
                user=instance,
                contact_name=instance.username,
                contact_email=instance.email,
                contact_phone=DEFAULT_PHONE,
            )

        elif role == "EMPLOYEE" and not hasattr(instance, "employee_profile"):
            EmployeeProfile.objects.create(
                user=instance,
                name=instance.username,
                contact_phone=DEFAULT_PHONE,
                email=instance.email,
            )

        elif role == "CUSTOMER" and not hasattr(instance, "customer_profile"):
            CustomerProfile.objects.create(
                user=instance,
                name=instance.username,
                contact_phone=DEFAULT_PHONE,
                email=instance.email,
                broker_id=get_default_broker(),
                employee_id=get_default_employee(),
            )
