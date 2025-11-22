from django.contrib.auth import get_user_model

User = get_user_model()

# Map friendly names → values stored in CustomUser.role
ROLE_MAP = {
    "broker": "BROKER",
    "customer": "CUSTOMER",
    "employee": "EMPLOYEE",
}


def validate_user_role(email: str, expected_role: str) -> None:
    """
    Raise ValueError if the given email does NOT belong to the expected role.

    expected_role: one of "broker", "customer", "employee" (case-insensitive)
    """

    # 1) User must exist
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValueError("User does not exist")

    # 2) Normalize role name
    expected_role_key = expected_role.lower()
    if expected_role_key not in ROLE_MAP:
        raise ValueError(f"Unknown expected role: {expected_role}")

    expected_role_value = ROLE_MAP[expected_role_key]

    # 3) Compare against CustomUser.role (which stores uppercase values)
    actual_role_value = (user.role or "").upper()

    if actual_role_value != expected_role_value:
        raise ValueError("Unauthorized")

    # If no exception, validation passed
    return None
