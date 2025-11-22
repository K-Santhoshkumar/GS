from django.contrib import admin
from .models import OTPTransaction, OTPPurpose, OTPStatus

class OTPTransactionAdmin(admin.ModelAdmin):
    list_display = ('otp_code', 'get_recipient', 'purpose', 'status', 'created_at', 'sent_at', 'verified_at')
    list_filter = ('purpose', 'status', 'delivery_method', 'created_at')
    search_fields = ('email', 'phone', 'otp_code', 'user__email')
    readonly_fields = ('otp_code', 'created_at', 'sent_at', 'verified_at', 'expires_at')
    fieldsets = (
        ('OTP Information', {
            'fields': ('otp_code', 'purpose', 'status', 'delivery_method')
        }),
        ('Recipient', {
            'fields': ('user', 'email', 'phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at', 'verified_at', 'expires_at')
        }),
        ('Metadata', {
            'fields': ('attempts', 'ip_address', 'user_agent', 'additional_info')
        }),
    )

    def get_recipient(self, obj):
        if obj.user:
            return f"{obj.user.email} (User #{obj.user.id})"
        elif obj.email:
            return obj.email
        elif obj.phone:
            return obj.phone
        return "Unknown"
    get_recipient.short_description = "Recipient"

admin.site.register(OTPTransaction, OTPTransactionAdmin)
