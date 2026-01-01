from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.http import Http404
from django.urls import reverse

from config.decorators import employee_required
from users.forms.employee_forms import EmployeeStep1Form, EmployeeStep2Form
from users.models.employeeProfile import EmployeeProfile


# =====================================================
# CONFIG (BROKER STYLE)
# =====================================================
CORE_MANDATORY = ["name", "employee_code", "contact_phone", "email"]

FORM_MAP = {
    1: EmployeeStep1Form,
    2: EmployeeStep2Form,
}


# =====================================================
# EMPLOYEE PROFILE (MULTI STEP)
# =====================================================
@login_required
@employee_required
def employee_profile(request):

    profile, _ = EmployeeProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "name": request.user.get_full_name() or request.user.username,
            "email": request.user.email or "",
        },
    )

    # -------------------------------------------------
    # STEP READ
    # -------------------------------------------------
    try:
        step = int(request.GET.get("step", 1))
    except ValueError:
        raise Http404()

    if step not in FORM_MAP:
        raise Http404()

    # -------------------------------------------------
    # STEP ENFORCEMENT (same as broker/customer)
    # -------------------------------------------------
    if step > 1:
        missing = [f for f in CORE_MANDATORY if not getattr(profile, f)]
        if missing:
            messages.info(request, "Complete Step 1 first.")
            return redirect(
                reverse("users:employee:employee_profile") + "?step=1"
            )

    FormClass = FORM_MAP[step]

    # -------------------------------------------------
    # POST
    # -------------------------------------------------
    if request.method == "POST":
        action = request.POST.get("action", "save")
        form = FormClass(request.POST, instance=profile)

        if form.is_valid():
            with transaction.atomic():
                inst = form.save(commit=False)
                inst.user = request.user
                inst.save()

                sync_completion_status(inst)

            messages.success(request, "Saved successfully.")

            if action == "prev":
                return redirect(
                    reverse("users:employee:employee_profile") + f"?step={step-1}"
                )

            if action == "next":
                return redirect(
                    reverse("users:employee:employee_profile") + f"?step={step+1}"
                )

            if action == "finish":
                return redirect(reverse("users:employee:employee_home"))

            return redirect(
                reverse("users:employee:employee_profile") + f"?step={step}"
            )

        messages.error(request, "Fix the errors below.")

    else:
        form = FormClass(instance=profile)

    return render_step(request, profile, form, step)


# =====================================================
# RENDER + PROGRESS
# =====================================================
def render_step(request, profile, form, step):

    percent = calculate_progress(profile)

    # 🔥 REQUIRED FOR TEMPLATE
    fields_list = [{"field": field} for field in form]

    return render(
        request,
        "users/employee_profile.html",
        {
            "step": step,
            "form": form,
            "profile": profile,
            "fields_list": fields_list,   # ✅ FIX
            "percent_complete": percent,
            "step_done_s1": all(getattr(profile, f) for f in CORE_MANDATORY),
            "step_done_s2": bool(profile.address),
        },
    )


# =====================================================
# PROGRESS + COMPLETION (BROKER STYLE)
# =====================================================
def calculate_progress(profile):

    required_fields = [
        "name",
        "employee_code",
        "contact_phone",
        "email",
        "designation",
        "address",
    ]

    filled = 0
    for field in required_fields:
        val = getattr(profile, field, None)
        if val and str(val).strip():
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
