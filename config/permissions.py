def is_customer(user):
    return getattr(user, "role", "").upper() == "CUSTOMER" and hasattr(
        user, "customer_profile"
    )


def is_broker(user):
    return getattr(user, "role", "").upper() == "BROKER" and hasattr(
        user, "broker_profile"
    )


def is_employee(user):
    return getattr(user, "role", "").upper() == "EMPLOYEE" and hasattr(
        user, "employee_profile"
    )
