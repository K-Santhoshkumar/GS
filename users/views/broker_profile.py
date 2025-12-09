from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.core.files.storage import default_storage
from django.urls import reverse

from users.forms.broker_forms import (
    BrokerProfileStep1Form,
    BrokerProfileStep2Form,
    BrokerProfileStep3Form,
    BrokerProfileStep4Form,
)
from users.models.brokerProfile import BrokerProfile
from config.decorators import broker_required


CORE_MANDATORY = ["account_type", "contact_name", "contact_email", "contact_phone"]

FORM_MAP = {
    1: BrokerProfileStep1Form,
    2: BrokerProfileStep2Form,
    3: BrokerProfileStep3Form,
    4: BrokerProfileStep4Form,
}

FILE_FIELDS = [
    "arn_document",
    "aprn_document",
    "pan_document",
    "cancelled_cheque",
    "address_proof",
    "agreement_document",
    "moa_aoa",
    "board_resolution",
    "partnership_deed",
    "gst_document",
    "auth_signatory_kyc",
]


# ============================================================
# 📌 MAIN VIEW
# ============================================================
@login_required
@broker_required
def broker_profile(request):

    # --------------------------------------------------------
    # Load or create profile
    # --------------------------------------------------------
    profile, _ = BrokerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "contact_name": request.user.get_full_name() or request.user.username,
            "contact_email": request.user.email or "",
        },
    )

    # --------------------------------------------------------
    # 📌 FILE DELETE HANDLER (AJAX or GET)
    # --------------------------------------------------------
    if request.GET.get("delete_file") == "1":
        field = request.GET.get("field")

        if field not in FILE_FIELDS:
            return JsonResponse({"success": False, "error": "Invalid field"})

        file_obj = getattr(profile, field, None)

        if file_obj and file_obj.name:
            try:
                # delete file from filesystem
                default_storage.delete(file_obj.name)
            except Exception:
                pass

            # clear DB entry
            setattr(profile, field, None)
            profile.save(update_fields=[field])

            return JsonResponse({"success": True})

        return JsonResponse({"success": False})

    # --------------------------------------------------------
    # Step validation
    # --------------------------------------------------------
    try:
        step = int(request.GET.get("step", 1))
    except ValueError:
        raise Http404()

    if not 1 <= step <= 4:
        raise Http404()

    # enforce step rules
    if step > 1:
        missing = [f for f in CORE_MANDATORY if not getattr(profile, f)]
        if missing:
            messages.info(request, "Complete Step 1 first.")
            return redirect("?step=1")

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

                # Save JSON manually
                if "products_allowed" in form.cleaned_data:
                    inst.products_allowed = form.cleaned_data["products_allowed"]
                    inst.save(update_fields=["products_allowed"])

            messages.success(request, "Saved successfully.")

            # navigation
            if action == "prev":
                return redirect(
                    reverse("users:broker:broker_profile") + f"?step={step-1}"
                )

            if action == "next":
                return redirect(
                    reverse("users:broker:broker_profile") + f"?step={step+1}"
                )

            if action == "finish":
                return redirect(reverse("users:broker:broker_home"))

            return redirect(reverse("users:broker:broker_profile") + f"?step={step}")

        messages.error(request, "Fix the errors below.")
        return render_step(request, profile, form, step)

    # --------------------------------------------------------
    # GET — Load form
    # --------------------------------------------------------
    form = FormClass(instance=profile)
    return render_step(request, profile, form, step)


# ============================================================
# 📌 FORM RENDERING + FILE PREVIEW + PROGRESS CALCULATION
# ============================================================
def render_step(request, profile, form, step):

    # Collect all step fields
    all_forms = [
        BrokerProfileStep1Form(instance=profile),
        BrokerProfileStep2Form(instance=profile),
        BrokerProfileStep3Form(instance=profile),
        BrokerProfileStep4Form(instance=profile),
    ]

    all_fields = []
    for f in all_forms:
        for b in f:
            if b.name not in all_fields:
                all_fields.append(b.name)

    # Calculate progress %
    filled = 0
    for name in all_fields:
        val = getattr(profile, name, None)
        if val:
            if hasattr(val, "name") and val.name:
                filled += 1
            elif isinstance(val, (list, dict)) and len(val) > 0:
                filled += 1
            elif str(val).strip():
                filled += 1

    percent = int((filled / len(all_fields)) * 100)

    # Upload mapping
    uploaded = {}
    for f in FILE_FIELDS:
        val = getattr(profile, f, None)
        if val and getattr(val, "name", None):
            uploaded[f] = {"name": val.name, "url": val.url}

    # Build field list for template
    fields_list = []
    for b in form:
        fields_list.append({"field": b, "uploaded": uploaded.get(b.name)})

    return render(
        request,
        "users/broker_profile.html",
        {
            "step": step,
            "form": form,
            "profile": profile,
            "fields_list": fields_list,
            "percent_complete": percent,
            "step_done_s1": all(getattr(profile, f) for f in CORE_MANDATORY),
            "step_done_s2": bool(
                profile.arn_code or profile.aprn_code or profile.products_allowed
            ),
            "step_done_s3": bool(profile.pan_number or profile.bank_account_number),
            "step_done_s4": bool(profile.address_line1 or profile.moa_aoa),
        },
    )
