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
