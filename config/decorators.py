# config/decorators.py

from django.http import HttpResponseForbidden
from config.permissions import is_customer, is_broker, is_employee
from django.shortcuts import render, redirect
from django.contrib import messages
from functools import wraps
from users.validators.role_validator import is_authorized_request_user


def customer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not is_customer(request.user):
            return HttpResponseForbidden("Not allowed")
        return view_func(request, *args, **kwargs)

    return wrapper


def broker_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not is_broker(request.user):
            return HttpResponseForbidden("Not allowed")
        return view_func(request, *args, **kwargs)

    return wrapper


def employee_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not is_employee(request.user):
            return HttpResponseForbidden("Not allowed")
        return view_func(request, *args, **kwargs)

    return wrapper


def block_logged_in_for_role(role_name, redirect_to):
    """Prevents logged-in users from opening login/register pages."""

    def decorator(view_fn):
        @wraps(view_fn)
        def wrapper(request, *args, **kwargs):

            if request.user.is_authenticated:
                if is_authorized_request_user(request.user, role_name):
                    return redirect(redirect_to)

                messages.error(request, "You cannot access this page while logged in.")
                return redirect("users:unauthorized")

            return view_fn(request, *args, **kwargs)

        return wrapper

    return decorator
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


ROLE_CONFIG = {
    "broker": {
        "profile_attr": "broker_profile",
        "home_url": "users:broker:broker_home",
    },
    "customer": {
        "profile_attr": "customer_profile",
        "home_url": "users:customer:customer_home",
    },
    "employee": {
        "profile_attr": "employee_profile",
        "home_url": "users:employee:employee_home",
    },
}


def dashboard_access_required(role):
    """
    Polymorphic dashboard access decorator.

    Enforces:
    - profile exists
    - profile.is_profile_completed == True
    - profile.is_active == True

    Works for broker / customer / employee
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            config = ROLE_CONFIG.get(role)

            if not config:
                raise ValueError(f"Invalid role '{role}' passed to decorator")

            profile = getattr(request.user, config["profile_attr"], None)

            if (
                not profile
                or not profile.is_profile_completed
                or not profile.is_active
            ):
                messages.warning(
                    request,
                    "Complete and activate your profile to access dashboard."
                )
                return redirect(config["home_url"])

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
