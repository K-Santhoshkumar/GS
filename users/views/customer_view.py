import json
from functools import wraps
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden

from otps.services import generate_otp, verify_otp, invalidate_existing_otps
from otps.models import OTPPurpose

# ✅ Only mandatory imports for authorization & blocking
from config.permissions import is_customer
from config.decorators import customer_required, block_logged_in_for_role

User = get_user_model()


@require_POST
def send_customer_otp(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    email = data.get("email", "").strip()
    purpose = data.get("purpose", "").upper()

    if not email:
        return JsonResponse({"success": False, "message": "Email required"}, status=400)

    if purpose == "LOGIN":
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "User not found"}, status=404
            )

        if not is_customer(user):
            return JsonResponse(
                {"success": False, "message": "Unauthorized"}, status=401
            )

        otp_purpose = OTPPurpose.LOGIN

    elif purpose == "SIGNUP":
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"success": False, "message": "Email already exists"}, status=400
            )

        otp_purpose = OTPPurpose.SIGNUP

    else:
        return JsonResponse(
            {"success": False, "message": "Invalid purpose"}, status=400
        )

    invalidate_existing_otps(otp_purpose, email=email)
    generate_otp(otp_purpose, email=email, deliver=True)

    return JsonResponse({"success": True, "message": "OTP sent"})


@ensure_csrf_cookie
# @block_logged_in_for_role("customer", "users:customer_home")
def customer_register(request):

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        otp = request.POST.get("otp_code", "").strip()
        phone = request.POST.get("phone", "").strip()
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.", "error")
            return render(
                request, "users/customer_register.html", {"email": email}, status=400
            )

        if not verify_otp(otp, OTPPurpose.SIGNUP, email=email):
            messages.error(request, "Invalid OTP.", "error")
            return render(
                request, "users/customer_register.html", {"email": email}, status=400
            )

        username = email.split("@")[0]
        base, i = username, 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{i}"
            i += 1

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username, email=email, role="CUSTOMER"
                )
                user.set_unusable_password()
                user.save()
                profile = user.customer_profile
                profile.contact_phone = phone
                profile.save()
                login(request, user)

            return redirect("users:customer_home")

        except Exception as e:
            messages.error(request, "Registration Failed", "error")
            print("Registration Error:", e)
            return render(
                request, "users/customer_register.html", {"email": email}, status=500
            )

    return render(request, "users/customer_register.html")


@ensure_csrf_cookie
@csrf_protect
# @block_logged_in_for_role("customer", "users:customer_home")
def customer_login(request):

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        otp = request.POST.get("otp_code", "").strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found.", "error")
            return render(
                request, "users/customer_login.html", {"email": email}, status=400
            )

        if not verify_otp(otp, OTPPurpose.LOGIN, email=email):
            messages.error(request, "Invalid OTP.", "error")
            return render(
                request, "users/customer_login.html", {"email": email}, status=400
            )

        if not is_customer(user):
            return HttpResponseForbidden("Not allowed")

        login(request, user)
        return redirect("users:customer_home")

    return render(request, "users/customer_login.html")


@login_required
@customer_required
def customer_home(request):
    return render(request, "users/customer_home.html")


@login_required
@customer_required
def customer_profile(request):

    if not hasattr(request.user, "customerprofile"):
        messages.error(request, "Profile not created yet!", "error")
        return redirect("users:unauthorized")

    profile = request.user.customer_profile

    if request.method == "POST":
        profile.customer_name = request.POST.get("name", profile.customer_name)
        profile.customer_phone = request.POST.get("phone_no", profile.customer_phone)
        profile.save()
        messages.success(request, "Profile updated.", "success")
        return redirect("users:customer_profile")

    return render(request, "users/customer_profile.html", {"profile": profile})


@require_POST
@customer_required
def customer_logout(request):
    logout(request)
    return redirect("users:customer_login")
