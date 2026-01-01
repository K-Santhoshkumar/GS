# Register your models here.
from django.contrib import admin
from .models.providers import PMSProvider, AIFProvider
from .models.schemes import PMSScheme, AIFScheme


# =========================
# PROVIDERS
# =========================

@admin.register(PMSProvider)
class PMSProviderAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "shortname",
        "priority",
        "is_whitelisted",
        "is_active",
    )
    list_filter = ("is_whitelisted", "is_active")
    search_fields = ("name", "shortname")
    ordering = ("priority", "name")
    readonly_fields = ("shortname",)
    

@admin.register(AIFProvider)
class AIFProviderAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "shortname",
        "priority",
        "is_whitelisted",
        "is_active",
    )
    list_filter = ("is_whitelisted", "is_active")
    search_fields = ("name", "shortname")
    ordering = ("priority", "name")
    readonly_fields = ("shortname",)


# =========================
# SCHEMES
# =========================

@admin.register(PMSScheme)
class PMSSchemeAdmin(admin.ModelAdmin):
    list_display = (
        "ia_name",
        "provider",
        "scheme_priority",
        "is_shortlisted",
        "open_for_investment",
        "is_active",
    )
    list_filter = (
        "provider",
        "is_shortlisted",
        "open_for_investment",
        "is_active",
    )
    search_fields = (
        "ia_name",
        "strategy_name",
        "provider__name",
    )
    ordering = ("scheme_priority", "ia_name")
    autocomplete_fields = ("provider",)


@admin.register(AIFScheme)
class AIFSchemeAdmin(admin.ModelAdmin):
    list_display = (
        "ia_name",
        "provider",
        "aif_category",
        "scheme_priority",
        "is_shortlisted",
        "open_for_investment",
        "is_active",
    )
    list_filter = (
        "provider",
        "aif_category",
        "is_shortlisted",
        "open_for_investment",
        "is_active",
    )
    search_fields = (
        "ia_name",
        "strategy_name",
        "provider__name",
    )
    ordering = ("scheme_priority", "ia_name")
    autocomplete_fields = ("provider",)
