# users/utils/dummy_relations.py
from users.models.employeeProfile import EmployeeProfile
from users.models.brokerProfile import BrokerProfile

DEFAULT_BROKER_CODE = "BHH173"
DEFAULT_EMPLOYEE_CODE = "3546"


def get_default_broker():
    return BrokerProfile.objects.filter(
        broker_code=DEFAULT_BROKER_CODE,
        is_active=True
    ).first()


def get_default_employee():
    return EmployeeProfile.objects.filter(
        employee_code=DEFAULT_EMPLOYEE_CODE,
        is_active=True
    ).first()
