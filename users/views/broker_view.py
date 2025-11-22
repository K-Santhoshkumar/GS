from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.messages import get_messages
import json

from users.validators.role_validator import validate_user_role
from otps.services import generate_otp, verify_otp, invalidate_existing_otps
from otps.models import OTPPurpose
from ..models import BrokerOnboarding

User = get_user_model()


# ======================================================
# Helpers
# ======================================================
def _get_broker_defaults(user):
    return {
        "contact_name": user.get_full_name() or user.username or user.email,
        "contact_phone": (
            getattr(user, "phone_no", None) or getattr(user, "phone", None) or "N/A"
        ),
    }


def _get_or_create_broker_onboarding(user):
    onboarding, created = BrokerOnboarding.objects.get_or_create(
        contact_email=user.email,
        defaults=_get_broker_defaults(user),
    )

    if not created:
        defaults = _get_broker_defaults(user)
        updated = False
        for field, value in defaults.items():
            if getattr(onboarding, field) != value:
                setattr(onboarding, field, value)
                updated = True
        if updated:
            onboarding.save()

    return onboarding


# ======================================================
# LOGIN VIEW (OTP + PASSWORD)
# ======================================================


@ensure_csrf_cookie
@csrf_protect
def broker_login(request):
    # Clear any stale messages from previous views
    list(get_messages(request))

    if request.method == "POST":
        email = request.POST.get("email") or ""
        password = request.POST.get("password") or ""
        otp_code = request.POST.get("otp_code") or ""

        # ----------------------------------------
        # OTP LOGIN
        # ----------------------------------------
        if otp_code:
            if verify_otp(otp_code, OTPPurpose.LOGIN, email=email):
                try:
                    user = User.objects.get(email=email)

                    # STRICT ROLE CHECK
                    if user.role.upper() != "BROKER":
                        messages.error(request, "Unauthorized")
                        return render(request, "users/broker_login.html")

                    login(request, user)
                    return redirect("users:broker_home")

                except User.DoesNotExist:
                    messages.error(request, "User not found.")
            else:
                messages.error(request, "Invalid OTP.")

            return render(request, "users/broker_login.html")

        # ----------------------------------------
        # PASSWORD LOGIN
        # ----------------------------------------
        user = authenticate(request, username=email, password=password)

        if user:
            if user.role.upper() != "BROKER":
                messages.error(request, "Unauthorized")
                return render(request, "users/broker_login.html")

            login(request, user)
            return redirect("users:broker_home")

        messages.error(request, "Invalid credentials.")

    return render(request, "users/broker_login.html")


# ======================================================
# REGISTER VIEW (OTP ONLY)
# ======================================================
@ensure_csrf_cookie
def broker_register(request):
    if request.method == "POST":
        email = request.POST.get("email") or ""
        otp_code = request.POST.get("otp_code") or ""

        # ----------------------------------------
        # SEND OTP FIRST
        # ----------------------------------------
        if not otp_code:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return redirect("users:broker_register")

            invalidate_existing_otps(OTPPurpose.SIGNUP, email=email)
            generate_otp(OTPPurpose.SIGNUP, email=email, deliver=True)

            messages.info(request, "OTP sent to your email.")
            return render(
                request,
                "users/broker_register.html",
                {"email": email, "otp_sent": True},
            )

        # ----------------------------------------
        # OTP VERIFIED → CREATE USER
        # ----------------------------------------
        if verify_otp(otp_code, OTPPurpose.SIGNUP, email=email):

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return redirect("users:broker_register")

            # Unique username
            username = email.split("@")[0]
            base = username
            cnt = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{cnt}"
                cnt += 1

            import secrets
            import string

            password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
            )

            # CRITICAL — Set role BEFORE saving → signals create only BrokerOnboarding
            user = User(username=username, email=email, role="BROKER")
            user.set_password(password)
            user.save()

            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("users:broker_home")

        messages.error(request, "Invalid OTP.")
        return render(
            request,
            "users/broker_register.html",
            {"email": email, "otp_sent": True},
        )

    return render(request, "users/broker_register.html")


# ======================================================
# PROFILE VIEW
# ======================================================
@login_required
def broker_profile(request):
    profile = _get_or_create_broker_onboarding(request.user)

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone_no")

        if name:
            profile.contact_name = name.strip()

        if phone:
            profile.contact_phone = phone.strip()

        profile.save()
        messages.success(request, "Profile updated successfully!")

    return render(request, "users/broker_profile.html", {"profile": profile})


# ======================================================
# HOME VIEW
# ======================================================
@ensure_csrf_cookie
@login_required
def broker_home(request):
    return render(request, "users/broker_home.html")


# ======================================================
# LOGOUT VIEW
# ======================================================
@csrf_protect
@require_POST
def broker_logout(request):
    from django.contrib.auth import logout

    logout(request)
    messages.success(request, "Logout successful!")
    return redirect("users:broker_login")


# ======================================================
# SEND OTP (Ajax)
# ======================================================
@require_POST
def send_broker_otp(request):
    data = json.loads(request.body or "{}")
    email = data.get("email") or ""
    purpose = (data.get("purpose") or "LOGIN").upper()

    # Purpose mapping
    if purpose == "LOGIN":
        otp_purpose = OTPPurpose.LOGIN
    elif purpose == "SIGNUP":
        otp_purpose = OTPPurpose.SIGNUP
    elif purpose == "RESET":
        otp_purpose = OTPPurpose.PASSWORD_RESET
    else:
        return JsonResponse({"success": False, "message": "Invalid purpose"})

    # ----------------------------------------
    # ROLE VALIDATION (LOGIN & RESET only)
    # ----------------------------------------
    if purpose != "SIGNUP":
        try:
            validate_user_role(email, "broker")
        except ValueError as err:
            return JsonResponse({"success": False, "message": str(err)}, status=401)

    # SIGNUP must use NEW email only
    if purpose == "SIGNUP" and User.objects.filter(email=email).exists():
        return JsonResponse(
            {"success": False, "message": "Email already registered"},
            status=400,
        )

    try:
        user = User.objects.get(email=email) if purpose != "SIGNUP" else None

        invalidate_existing_otps(otp_purpose, email=email)

        generate_otp(
            purpose=otp_purpose,
            email=email,
            user=user,
            deliver=True,
        )

        return JsonResponse({"success": True, "message": "OTP sent successfully"})

    except User.DoesNotExist:
        return JsonResponse({"success": False, "message": "User not found"})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
