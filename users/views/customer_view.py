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
from config.decorators import customer_required, block_logged_in_for_role, dashboard_access_required
from users.models.customerProfile import CustomerProfile
from users.views.customer_profile import calculate_progress
from users.utils.dummy_relations import get_default_broker, get_default_employee
from users.models.brokerProfile import BrokerProfile
from users.models.employeeProfile import EmployeeProfile
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
def customer_register(request):

    # -------------------------
    # GET → render form
    # -------------------------
    if request.method == "GET":
        return render(
            request,
            "users/customer_register.html",
            {
                "broker": request.GET.get("broker", ""),
                "employee": request.GET.get("employee", ""),
            },
        )

    # -------------------------
    # POST → process form
    # -------------------------
    email = request.POST.get("email", "").strip()
    otp = request.POST.get("otp_code", "").strip()
    phone = request.POST.get("phone", "").strip()

    # 🚨 THIS IS THE CRITICAL FIX
    broker_code = request.POST.get("broker")
    employee_id = request.POST.get("employee")

    if not verify_otp(otp, OTPPurpose.SIGNUP, email=email):
        messages.error(request, "Invalid OTP.")
        return redirect(request.path)

    with transaction.atomic():
        user = User.objects.create_user(
            username=email.split("@")[0],
            email=email,
            role="CUSTOMER",
        )
        user.set_unusable_password()
        user.save()

        profile = user.customer_profile
        profile.contact_phone = phone

        # -------------------------
        # RESOLVE BROKER
        # -------------------------
        broker = None
        if broker_code:
            broker = BrokerProfile.objects.filter(
                broker_code=broker_code,
                is_active=True,
            ).first()

        if broker is None:
            broker = get_default_broker()

        # -------------------------
        # RESOLVE EMPLOYEE
        # -------------------------
        employee = None
        if employee_id:
            employee = EmployeeProfile.objects.filter(
                employee_code=employee_id,   # ✅ CORRECT
                is_active=True,
            ).first()


        if employee is None:
            employee = get_default_employee()

        # -------------------------
        # ASSIGN (ALWAYS)
        # -------------------------
        profile.broker = broker
        profile.employee = employee
        profile.save()

        login(request, user)
        return redirect("users:customer:customer_home")

@ensure_csrf_cookie
@csrf_protect
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
        return redirect("users:customer:customer_home")

    return render(request, "users/customer_login.html")

@login_required
@customer_required
def customer_home(request):
    profile = getattr(request.user, "customer_profile", None)

    percent = 0
    profile_complete = False
    profile_active = False

    if profile:
        percent = calculate_progress(profile)
        profile_complete = profile.is_profile_completed
        profile_active = profile.is_active

        # ✅ completed & active → dashboard
        if (
            request.path.endswith("/home/")
            and profile_complete
            and profile_active
        ):
            return redirect("users:customer:customer_dashboard")

    return render(
        request,
        "users/customer_home.html",
        {
            "profile": profile,
            "percent_complete": percent,
            "profile_complete": profile_complete,
            "profile_active": profile_active,
        },
    )


# ======================================================
# CUSTOMER DASHBOARD
# ======================================================
@login_required
@customer_required
@dashboard_access_required("customer")
def customer_dashboard(request):
    """
    Main customer dashboard
    Access allowed only if profile is completed & active
    """

    return render(
        request,
        "users/customer_dashboard.html",
        {
            "profile": request.user.customer_profile,
            "is_completed": True,
            "active_page": "dashboard",
        },
    )

@login_required
@customer_required
def customer_investments(request):
    return render(
        request,
        "users/customer_investments.html",
        {
            "profile": request.user.customer_profile,
            "active_page": "investments",
        },
    )


@require_POST
@customer_required
def customer_logout(request):
    list(messages.get_messages(request))
    logout(request)
    return redirect("users:customer:customer_login")
