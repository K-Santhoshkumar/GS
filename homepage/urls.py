# homepage/urls.py
from django.urls import path
from homepage.views import (
    home,
    get_in_touch,
    partner,
    mutual_funds,
    pms,
    pms_top,
    pms_compare,
    pms_whitelisted,
    pms_whitelisted_data,
    aif,
    aif_top,
    aif_compare,
)

app_name = "homepage"

urlpatterns = [
    # Home
    path("", home, name="home"),

    # Contact / Partner
    path("get-in-touch/", get_in_touch, name="get_in_touch"),
    path("partner/", partner, name="partner"),

    # Mutual Funds
    path("mutual-funds/", mutual_funds, name="mutual_funds"),

    # PMS
    path("pms/", pms, name="pms"),
    path("pms/top/", pms_top, name="pms_top"),
    path("pms/compare/", pms_compare, name="pms_compare"),
    path("pms/whitelisted/", pms_whitelisted, name="pms_whitelisted"),
    path("pms/whitelisted/data/", pms_whitelisted_data, name="pms_whitelisted_data"),

    # AIF
    path("aif/", aif, name="aif"),
    path("aif/top/", aif_top, name="aif_top"),
    path("aif/compare/", aif_compare, name="aif_compare"),
]
