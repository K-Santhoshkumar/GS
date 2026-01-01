# users/views/broker_profile.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.core.files.storage import default_storage
from django.urls import reverse

from users.models.authSignatory import AuthorizedSignatory
from users.forms.broker_forms import (
    BrokerProfileStep1Form,
    BrokerProfileStep2Form,
    BrokerProfileStep3Form,
    BrokerProfileStep4Form,
    BrokerProfileStep5Form,
)
from users.models.brokerProfile import BrokerProfile
from config.decorators import broker_required


CORE_MANDATORY = ["account_type", "contact_name", "contact_email", "contact_phone"]

FORM_MAP = {
    1: BrokerProfileStep1Form,
    2: BrokerProfileStep2Form,
    3: BrokerProfileStep3Form,
    4: BrokerProfileStep4Form,
    5: BrokerProfileStep5Form,
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
]
# ============================================================
# MAIN PROFILE VIEW
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
    # FILE DELETE HANDLER
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

            # 🔁 Recalculate completion status
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

    if step not in [1, 2, 3, 4, 5, 6]:
        raise Http404()
    # Enforce Step-1 completion
    if step > 1:
        missing = [f for f in CORE_MANDATORY if not getattr(profile, f)]
        if missing:
            messages.info(request, "Complete Step 1 first.")
            return redirect("?step=1")
     # ========================================================
    # STEP 6 – AUTHORIZED SIGNATORIES
    # ========================================================
    if step == 6:
        return handle_auth_step(request, profile)

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

                # JSON field
                if "products_allowed" in form.cleaned_data:
                    inst.products_allowed = form.cleaned_data["products_allowed"]
                    inst.save(update_fields=["products_allowed"])

                # 🔁 Sync completion status
                sync_completion_status(inst)

            messages.success(request, "Saved successfully.")

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
    # GET
    # --------------------------------------------------------
    form = FormClass(instance=profile)
    return render_step(request, profile, form, step)
# ========================= STEP 6 =========================

def handle_auth_step(request, profile):

    signatories = profile.authorized_signatories.all()

    if request.method == "POST":
        action = request.POST.get("action", "save")

        names = request.POST.getlist("auth_signatory_name[]")
        emails = request.POST.getlist("auth_signatory_email[]")
        phones = request.POST.getlist("auth_signatory_phone[]")
        pans = request.POST.getlist("auth_signatory_pan[]")
        kycs = request.FILES.getlist("auth_signatory_kyc[]")

        # ✔ Allow finish without adding new if already exists
        if not names and signatories.exists():
            if action == "finish":
                sync_completion_status(profile)
                return redirect(reverse("users:broker:broker_home"))
            return redirect(reverse("users:broker:broker_profile") + "?step=6")

        # ❌ No existing and no new
        if not names and not signatories.exists():
            messages.error(request, "At least one authorized signatory is required.")
            return redirect(reverse("users:broker:broker_profile") + "?step=6")

        # ❌ Max limit check
        if signatories.count() + len(names) > 4:
            messages.error(request, "Maximum 4 authorized signatories allowed.")
            return redirect(reverse("users:broker:broker_profile") + "?step=6")

        # ✔ Save new signatories
        with transaction.atomic():
            for i in range(len(names)):
                AuthorizedSignatory.objects.create(
                    broker=profile,
                    auth_signatory_name=names[i],
                    auth_signatory_email=emails[i],
                    auth_signatory_phone=phones[i],
                    auth_signatory_pan=pans[i],
                    auth_signatory_kyc=kycs[i],
                )

        sync_completion_status(profile)

        if action == "finish":
            return redirect(reverse("users:broker:broker_home"))

        return redirect(reverse("users:broker:broker_profile") + "?step=6")

    # ---------- GET ----------
    return render(
        request,
        "users/broker_profile.html",
        {
            "step": 6,
            "profile": profile,
            "signatories": signatories,
            "percent_complete": calculate_progress(profile),

            # ✅ KEEP GREEN TICKS
            "step_done_s1": all(getattr(profile, f) for f in CORE_MANDATORY),
            "step_done_s2": bool(profile.arn_code or profile.aprn_code),
            "step_done_s3": bool(profile.pan_number or profile.bank_account_number),
            "step_done_s4": bool(profile.address_line1),
            "step_done_s5": bool(profile.agreement_document),
            "step_done_s6": bool(signatories),
        },
    )

# ========================= COMMON RENDER =========================
# ============================================================
# FORM RENDERING + FILE PREVIEW + PROGRESS
# ============================================================
def render_step(request, profile, form, step):

    percent = calculate_progress(profile)

    uploaded = {}
    for f in FILE_FIELDS:
        val = getattr(profile, f, None)
        if val and getattr(val, "name", None):
            uploaded[f] = {"name": val.name.split("/")[-1], "url": val.url}

    fields_list = [{"field": b, "uploaded": uploaded.get(b.name)} for b in form]

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
            "step_done_s2": bool(profile.arn_code or profile.aprn_code),
            "step_done_s3": bool(profile.pan_number or profile.bank_account_number),
            "step_done_s4": bool(profile.address_line1),
            "step_done_s5": bool(
                profile.moa_aoa or profile.partnership_deed or profile.gst_number
            ),
            "step_done_s6": profile.authorized_signatories.exists(),
        },
    )

# ========================= PROGRESS =========================
def calculate_progress(profile):
    """
    Field-based progress calculation
    - Every required field counts as 1 unit
    - Authorized signatories scale by number of forms × fields
    """

    total_required = 0
    filled = 0

    # ================= STEP 1 =================
    step1_fields = [
        "account_type",
        "contact_name",
        "contact_email",
        "contact_phone",
        "official_designation",
    ]

    # ================= STEP 2 =================
    step2_fields = [
        "arn_code",
        "arn_document",
        "products_allowed",
    ]

    # ================= STEP 3 =================
    step3_fields = [
        "pan_number",
        "pan_document",
        "bank_name",
        "bank_account_number",
        "bank_ifsc",
        "cancelled_cheque",
    ]

    # ================= STEP 4 =================
    step4_fields = [
        "address_line1",
        "city",
        "state",
        "pincode",
        "address_proof",
    ]

    # ================= STEP 5 =================
    step5_fields = [
        "agreement_document",
    ]

    # Conditional documents
    if profile.account_type in ["pvt_ltd", "llp"]:
        step5_fields += ["moa_aoa", "board_resolution"]

    if profile.account_type == "partnership":
        step5_fields.append("partnership_deed")

    all_profile_fields = (
        step1_fields
        + step2_fields
        + step3_fields
        + step4_fields
        + step5_fields
    )

    # ---------- Count broker profile fields ----------
    for field in all_profile_fields:
        total_required += 1
        val = getattr(profile, field, None)

        if val:
            if hasattr(val, "name"):  # FileField
                if val.name:
                    filled += 1
            elif isinstance(val, (list, dict)):  # JSONField
                if len(val) > 0:
                    filled += 1
            elif str(val).strip():
                filled += 1

    # ================= STEP 6 =================
    signatories = profile.authorized_signatories.all()

    SIGNATORY_FIELDS = [
        "auth_signatory_name",
        "auth_signatory_email",
        "auth_signatory_phone",
        "auth_signatory_pan",
        "auth_signatory_kyc",
    ]

    # At least ONE signatory is mandatory
    if not signatories.exists():
        total_required += len(SIGNATORY_FIELDS)
    else:
        for s in signatories:
            for field in SIGNATORY_FIELDS:
                total_required += 1
                val = getattr(s, field, None)
                if val:
                    if hasattr(val, "name"):
                        if val.name:
                            filled += 1
                    elif str(val).strip():
                        filled += 1

    # ================= FINAL =================
    if total_required == 0:
        return 0

    percent = int((filled / total_required) * 100)
    return min(percent, 100)

# ========================= COMPLETION STATUS =========================

def sync_completion_status(profile):
    """
    STRICT sync:
    - progress == 100 → completed
    - progress < 100 → NOT completed
    """
    percent = calculate_progress(profile)

    if percent == 100 and not profile.is_profile_completed:
        profile.is_profile_completed = True
        profile.save(update_fields=["is_profile_completed"])

    elif percent < 100 and profile.is_profile_completed:
        profile.is_profile_completed = False
        profile.save(update_fields=["is_profile_completed"])
