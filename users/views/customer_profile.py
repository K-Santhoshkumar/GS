from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.core.files.storage import default_storage
from django.urls import reverse

from config.decorators import customer_required
from users.forms.customer_forms import (
    CustomerStep1Form,
    CustomerStep2Form,
    CustomerStep3Form,
)
from users.models.customerProfile import CustomerProfile


# ============================================================
# CONFIG
# ============================================================

CORE_MANDATORY = ["name", "pan", "contact_phone"]

FORM_MAP = {
    1: CustomerStep1Form,
    2: CustomerStep2Form,
    3: CustomerStep3Form,
}

FILE_FIELDS = [
    "pan_copy",
    "address_proof",
]


# ============================================================
# MAIN PROFILE VIEW
# ============================================================
@login_required
@customer_required
def customer_profile(request):

    # --------------------------------------------------------
    # Load or create profile
    # --------------------------------------------------------
    profile, _ = CustomerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "name": request.user.get_full_name() or request.user.username,
            "email": request.user.email or "",
        },
    )
    # ======================================================
    # 🔐 ASSIGN BROKER / EMPLOYEE FROM QUERY PARAMS (ONCE)
    # ======================================================
    """ broker_id = request.GET.get("broker")
    employee_id = request.GET.get("employee")

    if (broker_id or employee_id) and not profile.broker and not profile.employee:
        from users.models.brokerProfile import BrokerProfile
        from users.models.employeeProfile import EmployeeProfile

        updated = False

        # ✅ Assign broker safely
        if broker_id and broker_id.isdigit():
            broker = BrokerProfile.objects.filter(id=broker_id, is_active=True).first()
            if broker:
                profile.broker = broker
                updated = True

        # ✅ Assign employee safely
        if employee_id and employee_id.isdigit():
            employee = EmployeeProfile.objects.filter(id=employee_id, is_active=True).first()
            if employee:
                profile.employee = employee
                updated = True

        if updated:
            profile.save(update_fields=["broker", "employee"]) """
    # --------------------------------------------------------
    # FILE DELETE HANDLER (AJAX)
    # --------------------------------------------------------
    if request.GET.get("delete_file") == "1":
        field = request.GET.get("field")

        if field not in FILE_FIELDS:
            return JsonResponse({"success": False, "error": "Invalid field"})

        file_obj = getattr(profile, field, None)
        if file_obj and file_obj.name:
            default_storage.delete(file_obj.name)
            setattr(profile, field, None)
            profile.save(update_fields=[field])

            sync_completion_status(profile)
            return JsonResponse({"success": True})

        return JsonResponse({"success": False})

    # --------------------------------------------------------
    # STEP VALIDATION
    # --------------------------------------------------------
    try:
        step = int(request.GET.get("step", 1))
    except ValueError:
        raise Http404()

    if step not in FORM_MAP:
        raise Http404()

    # Enforce Step-1 only (same as broker)
    if step > 1:
        missing = [f for f in CORE_MANDATORY if not getattr(profile, f)]
        if missing:
            messages.info(request, "Complete Step 1 first.")
            return redirect(
                reverse("users:customer:customer_profile") + "?step=1"
            )


    FormClass = FORM_MAP[step]

    # --------------------------------------------------------
    # FORM SUBMIT
    # --------------------------------------------------------
    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=profile)
        action = request.POST.get("action", "save")

        if form.is_valid():
            with transaction.atomic():
                inst = form.save(commit=False)
                inst.user = request.user
                inst.save()

                sync_completion_status(inst)

            messages.success(request, "Saved successfully.")

            if action == "prev":
                return redirect(
                    reverse("users:customer:customer_profile") + f"?step={step-1}"
                )

            if action == "next":
                return redirect(
                    reverse("users:customer:customer_profile") + f"?step={step+1}"
                )

            if action == "finish":
                return redirect(reverse("users:customer:customer_home"))

            return redirect(
                reverse("users:customer:customer_profile") + f"?step={step}"
            )

        messages.error(request, "Fix the errors below.")
        return render_step(request, profile, form, step)

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------
    form = FormClass(instance=profile)
    return render_step(request, profile, form, step)


# ============================================================
# FORM RENDERING + FILE PREVIEW + PROGRESS
# ============================================================
def render_step(request, profile, form, step):

    percent = calculate_progress(profile)

    uploaded = {}
    for f in FILE_FIELDS:
        val = getattr(profile, f, None)
        if val and getattr(val, "name", None):
            uploaded[f] = {
                "name": val.name.split("/")[-1],
                "url": val.url,
            }

    fields_list = [{"field": b, "uploaded": uploaded.get(b.name)} for b in form]

    return render(
        request,
        "users/customer_profile.html",
        {
            "step": step,
            "form": form,
            "profile": profile,
            "fields_list": fields_list,
            "percent_complete": percent,
            "step_done_s1": all(getattr(profile, f) for f in CORE_MANDATORY),
            "step_done_s2": bool(profile.address or profile.city or profile.state),
            "step_done_s3": bool(profile.pan_copy or profile.address_proof),
        },
    )


# ============================================================
# PROGRESS + COMPLETION HELPERS (BROKER STYLE)
# ============================================================
def calculate_progress(profile):

    required_fields = [
        "name",
        "pan",
        "contact_phone",
        "email",
        "address",
        "city",
        "state",
        "pincode",
        "pan_copy",
        "address_proof",
    ]

    filled = 0
    for field in required_fields:
        val = getattr(profile, field, None)

        if val:
            if hasattr(val, "name") and val.name:
                filled += 1
            elif str(val).strip():
                filled += 1

    return int((filled / len(required_fields)) * 100)


def sync_completion_status(profile):

    percent = calculate_progress(profile)

    if percent == 100 and not profile.is_profile_completed:
        profile.is_profile_completed = True
        profile.save(update_fields=["is_profile_completed"])

    elif percent < 100 and profile.is_profile_completed:
        profile.is_profile_completed = False
        profile.save(update_fields=["is_profile_completed"])
