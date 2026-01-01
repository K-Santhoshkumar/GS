from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models.brokerProfile import BrokerProfile
from users.models.authSignatory import AuthorizedSignatory
from users.models.customerProfile import CustomerProfile
from users.models.employeeProfile import EmployeeProfile

User = get_user_model()

# =====================================================
# CUSTOM USER ADMIN
# =====================================================
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")


# =====================================================
# AUTHORIZED SIGNATORY INLINE (MAX 4)
# =====================================================
class AuthorizedSignatoryInline(admin.TabularInline):
    model = AuthorizedSignatory
    extra = 0
    max_num = 4
    can_delete = True

    fields = (
        "auth_signatory_name",
        "auth_signatory_email",
        "auth_signatory_phone",
        "auth_signatory_pan",
        "auth_signatory_kyc",
        "created_at",
    )

    readonly_fields = ("created_at",)

    def has_add_permission(self, request, obj=None):
        if obj and obj.authorized_signatories.count() >= 4:
            return False
        return True


# =====================================================
# BROKER PROFILE ADMIN
# =====================================================
@admin.register(BrokerProfile)
class BrokerProfileAdmin(admin.ModelAdmin):

    # 🔹 List page
    list_display = (
        "broker_code",
        "contact_name",
        "contact_email",
        "contact_phone",
        "account_type",
        "status",
        "is_active",
        "is_profile_completed",
        "created_at",
    )

    list_filter = (
        "account_type",
        "status",
        "is_active",
        "is_profile_completed",
    )

    search_fields = (
        "broker_code",
        "contact_name",
        "contact_email",
        "contact_phone",
        "arn_code",
        "pan_number",
    )

    autocomplete_fields = ("employee",)

    readonly_fields = (
        "broker_code",
        "created_at",
        "updated_at",
        "submitted_at",
        "reviewed_at",
    )

    inlines = [AuthorizedSignatoryInline]

    fieldsets = (
        ("Broker Identity", {
            "fields": (
                "broker_code",
                "user",
                "account_type",
                "status",
                "is_active",
                "is_profile_completed",
            )
        }),
        ("Contact Details", {
            "fields": (
                "contact_name",
                "contact_email",
                "contact_phone",
                "official_designation",
            )
        }),
        ("Review & Meta", {
            "fields": (
                "notes",
                "submitted_at",
                "reviewed_by",
                "reviewed_at",
                "review_comments",
            )
        }),
        ("System", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
        
    )
    ordering = ["-id"]


# =====================================================
# CUSTOMER PROFILE ADMIN
# =====================================================
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

    list_filter = (
        "is_active",
        "state",
        "employee",
        "broker",
    )

    search_fields = (
        "name",
        "pan",
        "contact_phone",
        "email",
    )

    autocomplete_fields = (
        "broker",
        "employee",
    )


# =====================================================
# EMPLOYEE PROFILE ADMIN
# =====================================================
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

    list_filter = (
        "is_active",
        "designation",
        "joining_date",
    )

    search_fields = (
        "name",
        "employee_code",
        "contact_phone",
        "designation",
    )
