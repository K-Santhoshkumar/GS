# users/validators/role_validator.py

from django.contrib.auth import get_user_model

User = get_user_model()

ROLE_MAP = {
    "broker": "BROKER",
    "customer": "CUSTOMER",
    "employee": "EMPLOYEE",
}


def validate_user_role(email: str, expected_role: str):
    """
    Returns:
        None  → user not found
        True  → role matches
        False → role mismatch
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None  # USER NOT FOUND

    expected = ROLE_MAP.get(expected_role.lower())
    if not expected:
        return False

    return user.role.upper() == expected


def is_authorized_request_user(user, required_role: str):
    """Return True only for authenticated users with correct role."""
    if not user.is_authenticated:
        return False

    expected = ROLE_MAP.get(required_role.lower())
    if not expected:
        return False

    return user.role.upper() == expected
