from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.messages import get_messages
import json

from users.validators.role_validator import validate_user_role
from otps.services import generate_otp, verify_otp, invalidate_existing_otps
from otps.models import OTPPurpose

from ..models import EmployeeOnboarding

User = get_user_model()


# ======================================================
# Helpers
# ======================================================
def _get_employee_defaults(user):
    return {
        "employee_name": user.get_full_name() or user.username or user.email,
        "employee_phone": getattr(user, "phone_no", None)
        or getattr(user, "phone", None)
        or "N/A",
    }


def _get_or_create_employee_onboarding(user):
    onboarding, created = EmployeeOnboarding.objects.get_or_create(
        employee_email=user.email,
        defaults=_get_employee_defaults(user),
    )

    if not created:
        defaults = _get_employee_defaults(user)
        updated = False
        for field, value in defaults.items():
            if getattr(onboarding, field) != value:
                setattr(onboarding, field, value)
                updated = True
        if updated:
            onboarding.save()

    return onboarding


# ======================================================
# LOGIN (OTP ONLY)
# ======================================================


@ensure_csrf_cookie
@csrf_protect
def employee_login(request):
    # Clear all previous messages to avoid showing messages from other pages
    list(get_messages(request))

    if request.method == "POST":
        email = request.POST.get("email") or ""
        otp_code = request.POST.get("otp_code") or ""

        # Must submit OTP
        if not otp_code:
            messages.error(request, "Please enter the OTP.")
            return render(request, "users/employee_login.html")

        # Validate OTP
        if verify_otp(otp_code, OTPPurpose.LOGIN, email=email):
            try:
                user = User.objects.get(email=email)

                # Role check
                if user.role.upper() != "EMPLOYEE":
                    messages.error(request, "Unauthorized")
                    return render(request, "users/employee_login.html")

                login(request, user)
                return redirect("users:employee_home")

            except User.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            messages.error(request, "Invalid OTP.")

    return render(request, "users/employee_login.html")


# ======================================================
# REGISTRATION (OTP ONLY)
# ======================================================
@ensure_csrf_cookie
def employee_register(request):
    if request.method == "POST":
        email = request.POST.get("email") or ""
        otp_code = request.POST.get("otp_code") or ""

        # STEP 1 → Send OTP
        if not otp_code:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return redirect("users:employee_register")

            invalidate_existing_otps(OTPPurpose.SIGNUP, email=email)
            generate_otp(OTPPurpose.SIGNUP, email=email, deliver=True)

            return render(
                request,
                "users/employee_register.html",
                {"email": email, "otp_sent": True},
            )

        # STEP 2 → Verify OTP & Create User
        if verify_otp(otp_code, OTPPurpose.SIGNUP, email=email):

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return redirect("users:employee_register")

            # Username = email for unified login handling
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
            user = User(
                username=username,
                email=email,
                role="EMPLOYEE",
            )
            # important for OTP-only accounts
            user.set_unusable_password()
            user.save()

            # Keep behavior parallel to customer: auto-login after registration
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("users:employee_home")

        messages.error(request, "Invalid OTP.")
        return render(
            request,
            "users/employee_register.html",
            {"email": email, "otp_sent": True},
        )

    return render(request, "users/employee_register.html")


# ======================================================
# PROFILE
# ======================================================
@login_required
def employee_profile(request):
    profile = _get_or_create_employee_onboarding(request.user)

    if request.method == "POST":
        name_input = request.POST.get("name")
        phone_input = request.POST.get("phone_no")

        if name_input:
            profile.employee_name = name_input.strip()

        if phone_input:
            profile.employee_phone = phone_input.strip()

        profile.save()
        messages.success(request, "Profile updated successfully!")

    return render(request, "users/employee_profile.html", {"profile": profile})


# ======================================================
# HOME
# ======================================================
@ensure_csrf_cookie
@login_required
def employee_home(request):
    return render(request, "users/employee_home.html")


# ======================================================
# LOGOUT
# ======================================================
@csrf_protect
@require_POST
def employee_logout(request):
    from django.contrib.auth import logout

    logout(request)
    messages.success(request, "Logout successful!")
    return redirect("users:employee_login")


# ======================================================
# SEND OTP — AJAX
# ======================================================
@require_POST
def send_employee_otp(request):
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

    # LOGIN / RESET → validate role
    if purpose != "SIGNUP":
        try:
            validate_user_role(email, "employee")
        except ValueError as e:
            return JsonResponse({"success": False, "message": str(e)}, status=401)

    # SIGNUP → email must be new
    if purpose == "SIGNUP" and User.objects.filter(email=email).exists():
        return JsonResponse(
            {"success": False, "message": "Email already registered"}, status=400
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
