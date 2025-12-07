from django.db import transaction
from users.models.employeeProfile import EmployeeProfile


def get_default_employee():
    """
    Safe default employee creation that doesn't require a user
    """
    try:
        # Try to get any employee that doesn't have a user (system default)
        emp = EmployeeProfile.objects.filter(user__isnull=True, is_active=True).first()
        if emp:
            return emp.id

        # If no default employee exists, create one without a user
        with transaction.atomic():
            emp, created = EmployeeProfile.objects.get_or_create(
                employee_code="DEFAULT_EMP",
                defaults={
                    "name": "Default Employee",
                    "mobile": "9999999999",
                    "email": "default_employee@goalstox.com",
                    "is_active": True,
                    # Don't set user for default records
                },
            )
            return emp.id
    except Exception as e:
        print(f"Error getting default employee: {e}")
        # Last resort: get ANY employee
        emp = EmployeeProfile.objects.first()
        if emp:
            return emp.id
        return None


def get_default_broker():
    """
    Safe default broker creation that doesn't require a user
    """
    try:
        from users.models.brokerProfile import BrokerProfile

        # Try to get any broker that doesn't have a user (system default)
        broker = BrokerProfile.objects.filter(user__isnull=True, is_active=True).first()
        if broker:
            return broker.id

        # If no default broker exists, create one without a user
        with transaction.atomic():
            broker, created = BrokerProfile.objects.get_or_create(
                contact_email="default_broker@goalstox.com",
                defaults={
                    "contact_name": "Default Broker",
                    "contact_phone": "9999999999",
                    "account_type": "others",
                    "is_active": True,
                    "status": "approved",
                    # Don't set user for default records
                },
            )
            return broker.id
    except Exception as e:
        print(f"Error getting default broker: {e}")
        # Last resort: get ANY broker
        broker = BrokerProfile.objects.first()
        if broker:
            return broker.id
        return None
