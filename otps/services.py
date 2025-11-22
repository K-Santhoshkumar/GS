"""
Services for OTP management.

This module provides the core functionality for OTP generation, validation, and delivery.
It serves as the central OTP engine for the entire application.
"""

import logging
import sys
import os
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.db.models import Q

from .models import OTPTransaction, OTPPurpose, OTPStatus, DeliveryMethod

logger = logging.getLogger(__name__)

# Constants
DEFAULT_OTP_LENGTH = 6
DEFAULT_OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 3


def generate_otp(
    purpose, 
    email=None, 
    phone=None, 
    user=None, 
    length=DEFAULT_OTP_LENGTH, 
    expiry_minutes=DEFAULT_OTP_EXPIRY_MINUTES, 
    ip_address=None,
    user_agent=None,
    deliver=True,
    additional_info=None
):
    """
    Generate an OTP and store it in the database.
    
    Args:
        purpose (str): Purpose for which OTP is generated (use OTPPurpose constants)
        email (str, optional): Email to send OTP to
        phone (str, optional): Phone number to send OTP to
        user (User, optional): User object associated with this OTP
        length (int, optional): Length of OTP. Defaults to 6.
        expiry_minutes (int, optional): Expiry time in minutes. Defaults to 10.
        ip_address (str, optional): IP address of the requester
        user_agent (str, optional): User agent of the requester
        deliver (bool, optional): Whether to deliver the OTP immediately. Defaults to True.
        additional_info (dict, optional): Additional information to store
        
    Returns:
        tuple: (OTPTransaction object, generated OTP code)
    """
    # Validate inputs
    if not email and not phone and not user:
        raise ValueError("Must provide either email, phone or user")
    
    if not email and not phone:
        # Try to get email from user if not provided directly
        if user and hasattr(user, 'email'):
            email = user.email
    
    # Determine delivery method
    delivery_method = DeliveryMethod.EMAIL
    if email and phone:
        delivery_method = DeliveryMethod.BOTH
    elif phone and not email:
        delivery_method = DeliveryMethod.SMS
    
    # Generate OTP and create transaction record
    otp_code = get_random_string(length=length, allowed_chars='0123456789')
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
    
    # Create OTP transaction
    otp_transaction = OTPTransaction.objects.create(
        otp_code=otp_code,
        user=user,
        email=email,
        phone=phone,
        purpose=purpose,
        status=OTPStatus.CREATED,
        delivery_method=delivery_method,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
        additional_info=additional_info or {}
    )
    
    # Log OTP generation (this helps debugging)
    _log_otp_generation(otp_transaction)
    
    # Deliver OTP if requested
    if deliver:
        deliver_otp(otp_transaction)
    
    return otp_transaction, otp_code


def verify_otp(otp_code, purpose, email=None, phone=None, user=None, invalidate_on_success=True):
    """
    Verify an OTP.
    
    Args:
        otp_code (str): The OTP code to verify
        purpose (str): Purpose for which OTP was generated
        email (str, optional): Email associated with the OTP
        phone (str, optional): Phone number associated with the OTP
        user (User, optional): User object associated with the OTP
        invalidate_on_success (bool, optional): Whether to invalidate the OTP after successful verification
        
    Returns:
        bool: Whether the verification was successful
    """
    if not otp_code:
        return False
        
    # Build query to find the OTP
    query = Q(otp_code=otp_code, purpose=purpose, status=OTPStatus.DELIVERED)
    
    if email:
        query &= Q(email=email)
    if phone:
        query &= Q(phone=phone)
    if user:
        query &= Q(user=user)
    
    # Find the most recently created matching OTP
    otp_transaction = OTPTransaction.objects.filter(query).order_by('-created_at').first()
    
    if not otp_transaction:
        logger.warning(f"OTP verification failed: No matching OTP found for {purpose}")
        return False
    
    # Check if OTP is expired
    if otp_transaction.is_expired():
        otp_transaction.status = OTPStatus.EXPIRED
        otp_transaction.save(update_fields=['status'])
        logger.info(f"OTP verification failed: OTP expired for {otp_transaction.email or otp_transaction.phone}")
        return False
    
    # Increment attempt counter
    attempts = otp_transaction.increment_attempts()
    
    # Check if max attempts exceeded
    if attempts > MAX_OTP_ATTEMPTS:
        otp_transaction.invalidate()
        logger.warning(f"OTP verification failed: Max attempts exceeded for {otp_transaction.email or otp_transaction.phone}")
        return False
    
    # Mark as verified
    otp_transaction.mark_as_verified()
    
    # Invalidate OTP to prevent reuse if requested
    if invalidate_on_success:
        otp_transaction.invalidate()
    
    logger.info(f"OTP verified successfully for {otp_transaction.email or otp_transaction.phone}")
    return True


def deliver_otp(otp_transaction):
    """
    Deliver an OTP via the specified delivery method.
    
    Args:
        otp_transaction (OTPTransaction): The OTP transaction to deliver
    
    Returns:
        bool: Whether the delivery was successful
    """
    if otp_transaction.delivery_method == DeliveryMethod.EMAIL:
        return _deliver_via_email(otp_transaction)
    elif otp_transaction.delivery_method == DeliveryMethod.SMS:
        return _deliver_via_sms(otp_transaction)
    elif otp_transaction.delivery_method == DeliveryMethod.BOTH:
        email_success = _deliver_via_email(otp_transaction)
        sms_success = _deliver_via_sms(otp_transaction)
        return email_success or sms_success
    else:
        logger.error(f"Unknown delivery method: {otp_transaction.delivery_method}")
        return False


def invalidate_existing_otps(purpose, email=None, phone=None, user=None):
    """
    Invalidate any existing active OTPs for a specific purpose and recipient.
    This is useful before generating a new OTP to ensure only one is active.
    
    Args:
        purpose (str): Purpose of the OTPs to invalidate
        email (str, optional): Email associated with the OTPs
        phone (str, optional): Phone number associated with the OTPs
        user (User, optional): User associated with the OTPs
    """
    query = Q(purpose=purpose, status__in=[OTPStatus.CREATED, OTPStatus.DELIVERED])
    
    if email:
        query &= Q(email=email)
    if phone:
        query &= Q(phone=phone)
    if user:
        query &= Q(user=user)
    
    OTPTransaction.objects.filter(query).update(status=OTPStatus.INVALIDATED)


def get_recent_otps(limit=50):
    """Get recent OTPs for debugging purposes"""
    return OTPTransaction.objects.all().order_by('-created_at')[:limit]


# Private helper functions

def _deliver_via_email(otp_transaction):
    """Send OTP via email"""
    if not otp_transaction.email:
        logger.error("Cannot deliver OTP via email: No email address provided")
        return False
    
    # Get purpose display name
    purpose_display = dict(OTPPurpose.choices).get(otp_transaction.purpose, otp_transaction.purpose)
    
    # Format OTP message
    email_subject = f"Your {purpose_display} OTP Code - Goalstox"
    email_message = f"""
*********************************************************
*                                                       *
*  YOUR OTP CODE: {otp_transaction.otp_code}           *
*  Purpose: {purpose_display}                          *
*  Valid for: {DEFAULT_OTP_EXPIRY_MINUTES} minutes     *
*                                                       *
*********************************************************

This is an automated message from Goalstox.
    """
    
    try:
        print(f"DEBUG: About to send OTP email to {otp_transaction.email}")
        # Send email
        send_mail(
            email_subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [otp_transaction.email],
            fail_silently=False,
        )
        print(f"DEBUG: send_mail() called for {otp_transaction.email}")
        # Mark OTP as sent
        otp_transaction.mark_as_sent()
        logger.info(f"OTP sent via email to {otp_transaction.email}")
        return True
    
    except Exception as e:
        print(f"DEBUG: Exception in send_mail: {e}")
        logger.error(f"Failed to send OTP via email: {str(e)}")
        return False


def _deliver_via_sms(otp_transaction):
    """Send OTP via SMS"""
    if not otp_transaction.phone:
        logger.error("Cannot deliver OTP via SMS: No phone number provided")
        return False
    
    # This is a placeholder for actual SMS delivery integration
    # To be implemented when SMS functionality is added
    logger.warning("SMS delivery not yet implemented")
    
    # For now we'll just simulate successful delivery for testing
    # In production, integrate with an SMS provider here
    otp_transaction.mark_as_sent()
    
    return True


def _log_otp_generation(otp_transaction):
    """
    Log OTP generation for debugging purposes.
    Also writes to console and LATEST_OTP.txt for visibility.
    """
    # Log to Python logger
    logger.info(
        f"Generated OTP: {otp_transaction.otp_code} for "
        f"{otp_transaction.email or otp_transaction.phone or f'User #{otp_transaction.user_id}'} "
        f"(Purpose: {otp_transaction.purpose})"
    )
    
    # Format console message
    border = "!" * 70
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    recipient = otp_transaction.email or otp_transaction.phone or f"User #{otp_transaction.user_id}" if otp_transaction.user_id else "Unknown"
    
    # Print to console with high visibility
    print("\n" + border, file=sys.stdout, flush=True)
    print(f"!!! OTP GENERATED at {timestamp} !!!  Purpose: {otp_transaction.purpose}", file=sys.stdout, flush=True)
    print(f"!!! RECIPIENT: {recipient}", file=sys.stdout, flush=True)
    print(f"!!! OTP CODE: {otp_transaction.otp_code}", file=sys.stdout, flush=True)
    print(border + "\n", file=sys.stdout, flush=True)
    
    # Create a simple box around the OTP - highly visible
    otp_in_box = f"""
+----------------------+
|                      |
|   OTP: {otp_transaction.otp_code}         |
|   For: {recipient}   |
|                      |
+----------------------+
"""
    print(otp_in_box, flush=True)
    
    # Write to LATEST_OTP.txt for easy reference
    try:
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        otp_file_path = os.path.join(project_dir, 'LATEST_OTP.txt')
        with open(otp_file_path, 'w', encoding='utf-8') as f:
            f.write(f"OTP: {otp_transaction.otp_code}\n")
            f.write(f"Email: {otp_transaction.email or 'N/A'}\n")
            f.write(f"Phone: {otp_transaction.phone or 'N/A'}\n")
            f.write(f"Type: {otp_transaction.purpose}\n")
            f.write(f"Time: {timestamp}\n")
    except Exception as e:
        logger.error(f"Failed to write to LATEST_OTP.txt: {str(e)}")
