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


CORE_MANDATORY = ["name", "pan", "contact_phone"]

FORM_MAP = {
    1: CustomerStep1Form,
    2: CustomerStep2Form,
    3: CustomerStep3Form,
}

FILE_FIELDS = ["pan_copy", "address_proof"]


# ============================================================
# 📌 MAIN VIEW
# ============================================================
@login_required
@customer_required
def customer_profile(request):

    # Load or create profile
    profile, _ = CustomerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "name": request.user.get_full_name() or request.user.username,
            "email": request.user.email or "",
        },
    )

    # --------------------------------------------------------
    # 📌 FILE DELETE HANDLER (AJAX)
    # --------------------------------------------------------
    if request.GET.get("delete_file") == "1":
        field = request.GET.get("field")

        if field not in FILE_FIELDS:
            return JsonResponse({"success": False, "error": "Invalid field"})

        file_obj = getattr(profile, field, None)

        if file_obj and file_obj.name:
            try:
                default_storage.delete(file_obj.name)
            except:
                pass

            setattr(profile, field, None)
            profile.save(update_fields=[field])
            return JsonResponse({"success": True})

        return JsonResponse({"success": False})

    # --------------------------------------------------------
    # Step handling
    # --------------------------------------------------------
    try:
        step = int(request.GET.get("step", 1))
    except ValueError:
        raise Http404()

    if not 1 <= step <= 3:
        raise Http404()

    # Prevent skipping Step 1
    if step > 1:
        missing = [f for f in CORE_MANDATORY if not getattr(profile, f)]
        if missing:
            messages.info(request, "Please complete Step 1 first.")
            return redirect(reverse("users:customer:customer_profile") + "?step=1")

    FormClass = FORM_MAP[step]

    # --------------------------------------------------------
    # 📌 FORM SUBMISSION
    # --------------------------------------------------------
    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=profile)
        action = request.POST.get("action", "save")

        if form.is_valid():
            with transaction.atomic():
                inst = form.save(commit=False)
                inst.user = request.user
                inst.save()

            messages.success(request, "Saved successfully.")

            # -------------------------
            # 📌 YOUR NAVIGATION BLOCK
            # -------------------------
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

    # GET
    form = FormClass(instance=profile)
    return render_step(request, profile, form, step)


# ============================================================
# 📌 RENDER STEP
# ============================================================
def render_step(request, profile, form, step):

    # Collect all fields (like broker)
    all_forms = [
        CustomerStep1Form(instance=profile),
        CustomerStep2Form(instance=profile),
        CustomerStep3Form(instance=profile),
    ]

    all_fields = []
    for f in all_forms:
        for b in f:
            if b.name not in all_fields:
                all_fields.append(b.name)

    # Progress
    filled = 0
    for name in all_fields:
        val = getattr(profile, name, None)
        if val:
            if hasattr(val, "name") and val.name:
                filled += 1
            elif str(val).strip():
                filled += 1

    percent = int((filled / len(all_fields)) * 100)

    # Uploaded file preview
    uploaded = {}
    for f in FILE_FIELDS:
        val = getattr(profile, f, None)
        if val and val.name:
            uploaded[f] = {"name": val.name, "url": val.url}

    # Field items for template
    fields_list = []
    for b in form:
        fields_list.append({"field": b, "uploaded": uploaded.get(b.name)})

    return render(
        request,
        "users/customer_profile.html",
        {
            "step": step,
            "form": form,
            "fields_list": fields_list,
            "percent_complete": percent,
            "step_done_s1": all(getattr(profile, f) for f in CORE_MANDATORY),
            "step_done_s2": bool(profile.address or profile.city),
            "step_done_s3": bool(profile.pan_copy or profile.address_proof),
        },
    )
