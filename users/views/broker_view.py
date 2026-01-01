# users/views/broker_view.py

import json
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from otps.services import generate_otp, verify_otp, invalidate_existing_otps
from otps.models import OTPPurpose

# ✅ Only mandatory imports now used for authorization & blocking
from config.permissions import is_broker
from config.decorators import broker_required, block_logged_in_for_role, dashboard_access_required
from users.models.brokerProfile import BrokerProfile
from users.models.customerProfile import CustomerProfile
from users.views.broker_profile import calculate_progress

User = get_user_model()


# ======================================================
# SEND OTP (Called from frontend via AJAX POST)
# ======================================================
@require_POST
def send_broker_otp(request):
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

        if not is_broker(user):  # ✅ Profile-based role check only
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


# ======================================================
# REGISTER (OTP must be sent using send_broker_otp first)
# ======================================================
@ensure_csrf_cookie
def broker_register(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        otp = request.POST.get("otp_code", "").strip()
        phone = request.POST.get("phone", "").strip()
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.", "error")
            return render(
                request, "users/broker_register.html", {"email": email}, status=400
            )
        if not verify_otp(otp, OTPPurpose.SIGNUP, email=email):
            messages.error(request, "Invalid OTP", "error")
            return render(
                request, "users/broker_register.html", {"email": email}, status=400
            )

        username = email.split("@")[0]
        base, i = username, 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{i}"
            i += 1

        try:
            with transaction.atomic():  # ✅ Best way: all-or-nothing DB commit
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    role="BROKER",
                )
                user.set_unusable_password()
                user.save()  # Signal runs here but inside atomic, so rollback works if needed
                profile = user.broker_profile
                profile.contact_phone = phone
                profile.save()
                login(request, user)

            return redirect("users:broker:broker_home")

        except Exception as e:
            messages.error(request, "Registration Failed", "error")
            print("Registration Error:", e)
            return render(
                request, "users/broker_register.html", {"email": email}, status=500
            )

    return render(request, "users/broker_register.html")


# ======================================================
# LOGIN (User must request OTP first, then submit it here)
# ======================================================
@ensure_csrf_cookie
@csrf_protect
def broker_login(request):

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        otp = request.POST.get("otp_code", "").strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found.", "error")
            return render(
                request, "users/broker_login.html", {"email": email}, status=400
            )

        if not verify_otp(otp, OTPPurpose.LOGIN, email=email):
            messages.error(request, "Invalid OTP.", "error")
            return render(
                request, "users/broker_login.html", {"email": email}, status=400
            )

        if not is_broker(user):  # ✅ Only mandatory permission check now
            return HttpResponseForbidden("Not allowed")

        login(request, user)
        return redirect("users:broker:broker_home")

    return render(request, "users/broker_login.html")


@login_required
@broker_required
def broker_home(request):
    profile = getattr(request.user, "broker_profile", None)

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
            return redirect("users:broker:broker_dashboard")

    return render(
        request,
        "users/broker_home.html",
        {
            "profile": profile,
            "percent_complete": percent,
            "profile_complete": profile_complete,
            "profile_active": profile_active,
        },
    )
# ======================================================
# BROKER DASHBOARD
# ======================================================
@login_required
@broker_required
@dashboard_access_required("broker")
def broker_dashboard(request):
    """
    Main broker dashboard
    Access allowed only if profile is completed & active
    """

    return render(
        request,
        "users/broker_dashboard.html",
        {
            "profile": request.user.broker_profile,
            "is_completed": True,
        },
    )


# ======================================================
# CUSTOMERS LIST (BROKER)
# ======================================================
@login_required
@broker_required
@dashboard_access_required("broker")
def customers_list(request):
    customers_qs = CustomerProfile.objects.filter(
        broker=request.user.broker_profile
    )

    paginator = Paginator(customers_qs, 6)  # 6 cards per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "users/broker_customers.html",
        {
            "customers": page_obj,
            "page_obj": page_obj,
        },
    )

# ======================================================
# CUSTOMER DETAIL (BROKER VIEW)
# ======================================================
@login_required
@broker_required
@dashboard_access_required("broker")
def customer_detail(request, customer_id):
    """
    View a single customer under this broker
    """

    customer = CustomerProfile.objects.filter(
        id=customer_id,
        broker=request.user.broker_profile
    ).first()

    if not customer:
        raise Http404("Customer not found")

    return render(
        request,
        "users/customer_detail.html",
        {
            "customer": customer,
        },
    )


# ======================================================
# BROKER LOGOUT
# ======================================================
@require_POST
@broker_required
def broker_logout(request):
    """
    Secure broker logout
    """

    # Clear queued messages
    list(messages.get_messages(request))

    logout(request)
    return redirect("users:broker:broker_login")