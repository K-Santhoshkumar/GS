from django import forms
from django.core.validators import RegexValidator

from users.models.customerProfile import CustomerProfile
from users.utils.widgets import SimpleFileInput
from users.validators.validators import pan_validator, mobile_validator


# =====================================================
# COMMON VALIDATORS
# =====================================================

pincode_validator = RegexValidator(
    regex=r"^\d{6}$",
    message="Enter a valid 6-digit pincode."
)


# =====================================================
# STEP 1 – BASIC DETAILS (MANDATORY)
# =====================================================
class CustomerStep1Form(forms.ModelForm):

    class Meta:
        model = CustomerProfile
        fields = [
            "name",
            "pan",
            "contact_phone",
            "email",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "pan": forms.TextInput(attrs={"class": "form-input"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Same rule as Broker Step-1
        required = {"name", "pan", "contact_phone", "email"}
        for name, field in self.fields.items():
            field.required = name in required


# =====================================================
# STEP 2 – ADDRESS (OPTIONAL – BROKER STYLE)
# =====================================================
class CustomerStep2Form(forms.ModelForm):

    pincode = forms.CharField(
        required=False,
        validators=[pincode_validator],
    )

    class Meta:
        model = CustomerProfile
        fields = [
            "address",
            "city",
            "state",
            "pincode",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3, "class": "form-input"}),
            "city": forms.TextInput(attrs={"class": "form-input"}),
            "state": forms.TextInput(attrs={"class": "form-input"}),
            "pincode": forms.TextInput(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔓 Allow skipping (exact broker behaviour)
        for field in self.fields.values():
            field.required = False


# =====================================================
# STEP 3 – DOCUMENTS (OPTIONAL – BROKER STYLE)
# =====================================================
class CustomerStep3Form(forms.ModelForm):

    class Meta:
        model = CustomerProfile
        fields = [
            "pan_copy",
            "address_proof",
        ]
        widgets = {
            "pan_copy": SimpleFileInput(),
            "address_proof": SimpleFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔓 Do NOT block navigation
        for field in self.fields.values():
            field.required = False
