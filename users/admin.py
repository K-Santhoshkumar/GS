from django.contrib import admin
from django.conf import settings
from users.models.brokerProfile import BrokerProfile
from users.models.customerProfile import CustomerProfile
from users.models.employeeProfile import EmployeeProfile
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "pan",
        "contact_phone",
        "email",
        "broker",
        "employee",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "state", "employee", "broker")
    search_fields = ("name", "pan", "contact_phone", "email")
    autocomplete_fields = ("broker", "employee")


@admin.register(BrokerProfile)
class BrokerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "contact_name",
        "contact_email",
        "contact_phone",
        "account_type",
        "status",
        "is_active",
        "created_at",
    )
    list_filter = ("account_type", "status", "is_active", "state")
    search_fields = ("contact_name", "contact_email", "arn_code", "pan_number")
    autocomplete_fields = ("employee",)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "employee_code",
        "contact_phone",
        "designation",
        "joining_date",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "designation", "joining_date")
    search_fields = ("name", "employee_code", "contact_phone", "designation")
