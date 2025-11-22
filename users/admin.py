from django.contrib import admin

from .models import (
    BrokerOnboarding,
    CustomerOnboarding,
    CustomUser,
    EmployeeOnboarding,
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")


@admin.register(CustomerOnboarding)
class CustomerOnboardingAdmin(admin.ModelAdmin):
    list_display = ("customer_email", "account_type", "status", "is_active")
    list_filter = ("account_type", "status", "is_active")
    search_fields = ("customer_name", "customer_email", "pan_number")


@admin.register(BrokerOnboarding)
class BrokerOnboardingAdmin(admin.ModelAdmin):
    list_display = ("contact_email", "account_type", "status", "is_active")
    list_filter = ("account_type", "status", "is_active")
    search_fields = ("contact_name", "contact_email", "pan_number")


@admin.register(EmployeeOnboarding)
class EmployeeOnboardingAdmin(admin.ModelAdmin):
    list_display = ("employee_email", "account_type", "status", "is_active")
    list_filter = ("account_type", "status", "is_active")
    search_fields = ("employee_name", "employee_email", "pan_number")
