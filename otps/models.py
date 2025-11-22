from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

User = get_user_model()

class OTPPurpose(models.TextChoices):
    """Define purposes for which OTPs can be generated"""
    LOGIN = 'LOGIN', 'Login Authentication'
    SIGNUP = 'SIGNUP', 'New Account Creation'
    PASSWORD_RESET = 'PASSWORD_RESET', 'Password Reset'
    EMAIL_VERIFICATION = 'EMAIL_VERIFICATION', 'Email Verification'
    TRANSACTION_VERIFICATION = 'TRANSACTION_VERIFICATION', 'Transaction Verification'
    PROFILE_UPDATE = 'PROFILE_UPDATE', 'Profile Update'
    OTHER = 'OTHER', 'Other Purpose'

class OTPStatus(models.TextChoices):
    """Define the status of the OTP"""
    CREATED = 'CREATED', 'Created'
    DELIVERED = 'DELIVERED', 'Delivered'
    VERIFIED = 'VERIFIED', 'Verified'
    EXPIRED = 'EXPIRED', 'Expired'
    INVALIDATED = 'INVALIDATED', 'Invalidated'

class DeliveryMethod(models.TextChoices):
    """Define the delivery method for OTPs"""
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'
    BOTH = 'BOTH', 'Both Email and SMS'

class OTPTransaction(models.Model):
    """
    Comprehensive model for tracking OTP generation, delivery, and usage.
    This serves as the central record for all OTP-related activities.
    """
    # OTP and basic details
    otp_code = models.CharField(max_length=10, help_text="The generated OTP code")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, 
                            help_text="User associated with this OTP (can be null for signup)")
    
    # Contact information
    email = models.EmailField(null=True, blank=True, help_text="Email address for sending OTP")
    phone = models.CharField(max_length=15, null=True, blank=True, help_text="Phone number for sending OTP")
    
    # Purpose and status tracking
    purpose = models.CharField(
        max_length=30,
        choices=OTPPurpose.choices,
        default=OTPPurpose.OTHER,
        help_text="Purpose for which this OTP was generated"
    )
    status = models.CharField(
        max_length=20,
        choices=OTPStatus.choices,
        default=OTPStatus.CREATED,
        help_text="Current status of this OTP"
    )
    delivery_method = models.CharField(
        max_length=10,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.EMAIL,
        help_text="Method used to deliver the OTP"
    )
    
    # Timestamps for complete lifecycle tracking
    created_at = models.DateTimeField(default=timezone.now, help_text="When the OTP was generated")
    sent_at = models.DateTimeField(null=True, blank=True, help_text="When the OTP was sent")
    verified_at = models.DateTimeField(null=True, blank=True, help_text="When the OTP was successfully verified")
    expires_at = models.DateTimeField(help_text="When the OTP will expire")
    
    # Additional metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of the requester")
    user_agent = models.TextField(null=True, blank=True, help_text="User agent of the requester")
    additional_info = models.JSONField(null=True, blank=True, help_text="Additional information as needed")
    attempts = models.PositiveSmallIntegerField(default=0, help_text="Number of verification attempts made")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "OTP Transaction"
        verbose_name_plural = "OTP Transactions"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['email', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['otp_code']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        recipient = self.email or self.phone or f"User #{self.user_id}" if self.user_id else "Unknown"
        return f"OTP: {self.otp_code} for {recipient} ({self.get_purpose_display()}) - {self.get_status_display()}"
    
    def mark_as_sent(self):
        """Mark the OTP as sent"""
        self.sent_at = timezone.now()
        self.status = OTPStatus.DELIVERED
        self.save(update_fields=['sent_at', 'status'])
    
    def mark_as_verified(self):
        """Mark the OTP as verified"""
        self.verified_at = timezone.now()
        self.status = OTPStatus.VERIFIED
        self.save(update_fields=['verified_at', 'status'])
    
    def increment_attempts(self):
        """Increment the number of verification attempts"""
        self.attempts += 1
        self.save(update_fields=['attempts'])
        return self.attempts
    
    def is_expired(self):
        """Check if the OTP is expired"""
        return timezone.now() >= self.expires_at
    
    def invalidate(self):
        """Invalidate this OTP"""
        self.status = OTPStatus.INVALIDATED
        self.save(update_fields=['status'])
        
    @classmethod
    def generate_otp(cls, length=6):
        """Generate a random OTP of specified length"""
        return get_random_string(length=length, allowed_chars='0123456789')
