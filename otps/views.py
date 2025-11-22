from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login

from .models import OTPPurpose, OTPStatus
from .services import generate_otp, verify_otp, invalidate_existing_otps

# These views could be used as utility views for OTP management
# Most likely your existing apps will handle OTP verification in their own views
