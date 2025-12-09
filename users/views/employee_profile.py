from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.http import Http404
from django.urls import reverse

from config.decorators import employee_required
from users.forms.employee_forms import EmployeeStep1Form, EmployeeStep2Form
from users.models.employeeProfile import EmployeeProfile

# Required fields to unlock Step 2
CORE_MANDATORY = ["name", "employee_code", "contact_phone"]

FORM_MAP = {
    1: EmployeeStep1Form,
    2: EmployeeStep2Form,
}


@login_required
@employee_required
def employee_profile(request):

    # Load profile
    profile, _ = EmployeeProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "name": request.user.get_full_name() or request.user.username,
            "email": request.user.email or "",
        },
    )

    # Read step
    try:
        step = int(request.GET.get("step", 1))
    except:
        raise Http404()

    if not 1 <= step <= 2:
        raise Http404()

    # Don't allow Step 2 without Step 1
    if step == 2:
        missing = [f for f in CORE_MANDATORY if not getattr(profile, f)]
        if missing:
            messages.info(request, "Please complete Step 1 first.")
            return redirect(reverse("users:employee:employee_profile") + "?step=1")

    FormClass = FORM_MAP[step]

    # POST submission
    if request.method == "POST":
        action = request.POST.get("action", "save")
        form = FormClass(request.POST, instance=profile)

        if form.is_valid():
            with transaction.atomic():
                inst = form.save(commit=False)
                inst.user = request.user
                inst.save()

            # Navigation
            if action == "prev":
                return redirect(reverse("users:employee:employee_profile") + "?step=1")

            if action == "next":
                return redirect(reverse("users:employee:employee_profile") + "?step=2")

            if action == "finish":
                return redirect(reverse("users:employee:employee_home"))

            return redirect(
                reverse("users:employee:employee_profile") + f"?step={step}"
            )

        messages.error(request, "Fix the errors below.")
    else:
        form = FormClass(instance=profile)

    return render_step(request, profile, form, step)


def render_step(request, profile, form, step):

    # Progress calculation
    all_fields = list(EmployeeStep1Form().fields.keys()) + list(
        EmployeeStep2Form().fields.keys()
    )

    filled = sum(1 for f in all_fields if getattr(profile, f, None))
    percent = int((filled / len(all_fields)) * 100)

    fields_list = [{"field": b, "uploaded": None} for b in form]

    return render(
        request,
        "users/employee_profile.html",
        {
            "step": step,
            "form": form,
            "fields_list": fields_list,
            "percent_complete": percent,
            "step_done_s1": all(getattr(profile, f) for f in CORE_MANDATORY),
            "step_done_s2": bool(profile.address),
        },
    )
