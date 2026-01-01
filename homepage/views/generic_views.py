# homepage/views.py
from django.shortcuts import render
from django.db.models import Case, When, Value, IntegerField

from homepage.models.providers import PMSProvider, AIFProvider
from homepage.models.schemes import PMSScheme, AIFScheme
from django.http import JsonResponse


# ======================================================
# HOME
# ======================================================
def home(request):
    return render(request, "homepage/home.html")


# ======================================================
# CONTACT
# ======================================================
def get_in_touch(request):
    return render(request, "homepage/get_in_touch.html")


# ======================================================
# PARTNER
# ======================================================
def partner(request):
    return render(request, "homepage/partner.html")


# homepage/views.py
def mutual_funds(request):
    return render(request, "homepage/mutual_funds.html")


# ======================================================
# PMS LANDING
# ======================================================
def pms(request):
    """
    PMS landing page (overview)
    """
    return render(request, "homepage/PMS.html")


# ======================================================
# AIF LANDING
# ======================================================
def aif(request):
    """
    AIF landing page (overview)
    """
    return render(request, "homepage/AIF.html")


# ======================================================
# PMS – WHITELISTED PROVIDERS
# ======================================================
def pms_whitelisted(request):
    """
    Whitelisted PMS providers page
    """
    providers = (
        PMSProvider.objects
        .filter(is_active=True, is_whitelisted=True)
        .order_by("priority", "name")
    )

    return render(
        request,
        "homepage/pms_whitelisted.html",
        {"providers": providers}
    )


# ======================================================
# PMS – WHITELISTED DATA (SCHEMES)
# ======================================================

def pms_whitelisted_data(request):
    schemes = (
        PMSScheme.objects
        .filter(
            is_active=True,
            open_for_investment=True,
            provider__is_whitelisted=True,
            provider__is_active=True,
        )
        .select_related("provider")
        .order_by("effective_priority")
    )

    data = [
        {
            "id": s.id,
            "name": s.ia_name,
            "provider": s.provider.name,
            "category": s.category,
            "one_year_return": s.one_year_return,
            "three_year_return": s.three_year_return,
            "min_inv": s.min_inv_amount,
        }
        for s in schemes
    ]

    return JsonResponse({"schemes": data})


# ======================================================
# PMS – TOP / FEATURED
# ======================================================
def pms_top(request):
    """
    Top PMS providers & schemes
    """

    providers = (
        PMSProvider.objects
        .filter(is_active=True, is_whitelisted=True)
        .order_by("priority", "name")
    )

    schemes = (
        PMSScheme.objects
        .filter(
            is_active=True,
            open_for_investment=True,
            provider__is_whitelisted=True,
            provider__is_active=True,
        )
        .select_related("provider")
        .order_by("effective_priority")
    )

    return render(
        request,
        "homepage/pms_top.html",
        {
            "providers": providers,
            "schemes": schemes,
        }
    )


# ======================================================
# PMS – COMPARE
# ======================================================
def pms_compare(request):
    """
    Compare all PMS schemes
    """
    schemes = (
        PMSScheme.objects
        .filter(is_active=True)
        .select_related("provider")
        .order_by(
            "provider__priority",
            "scheme_priority",
            "ia_name",
        )
    )

    return render(
        request,
        "homepage/pms_compare.html",
        {"schemes": schemes}
    )


# ======================================================
# AIF – TOP / SHORTLISTED
# ======================================================
def aif_top(request):
    """
    Top / shortlisted AIF schemes
    """

    schemes = (
        AIFScheme.objects
        .filter(
            is_active=True,
            open_for_investment=True,
            provider__is_active=True,
        )
        .select_related("provider")
        .annotate(
            sort_priority=Case(
                When(is_shortlisted=True, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by(
            "sort_priority",
            "provider__priority",
            "scheme_priority",
            "-created_at",
        )
    )

    return render(
        request,
        "homepage/aif_top.html",
        {"schemes": schemes}
    )


# ======================================================
# AIF – COMPARE
# ======================================================
def aif_compare(request):
    """
    Compare all active AIF schemes with active & whitelisted providers
    """

    schemes = (
        AIFScheme.objects
        .filter(
            is_active=True,
            provider__is_active=True,
            provider__is_whitelisted=True,
        )
        .select_related("provider")
        .order_by(
            "provider__priority",
            "scheme_priority",
            "ia_name",
        )
    )

    return render(
        request,
        "homepage/aif_compare.html",
        {
            "schemes": schemes,
            "total_schemes": schemes.count(),
        },
    )
