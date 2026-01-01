from django import forms
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

from users.models.brokerProfile import BrokerProfile, PRODUCT_CHOICES
from users.utils.widgets import SimpleFileInput


# =====================================================
# COMMON VALIDATORS
# =====================================================

ifsc_validator = RegexValidator(
    regex=r"^[A-Z]{4}0[A-Z0-9]{6}$", message="Enter a valid IFSC code."
)

gst_validator = RegexValidator(
    regex=r"^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]{3}$", message="Enter a valid GST number."
)

pincode_validator = RegexValidator(
    regex=r"^\d{6}$", message="Enter a valid 6-digit pincode."
)

account_number_validator = RegexValidator(
    regex=r"^\d{9,18}$", message="Enter a valid bank account number."
)


# =====================================================
# STEP 1 – BASIC DETAILS
# =====================================================


class BrokerProfileStep1Form(forms.ModelForm):

    class Meta:
        model = BrokerProfile
        fields = [
            "account_type",
            "contact_name",
            "contact_email",
            "contact_phone",
            "official_designation",
        ]
        widgets = {
            "contact_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Full name",
                }
            ),
            "contact_email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "autocomplete": "email",
                    "placeholder": "Email address",
                }
            ),
            "contact_phone": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "+91 9876543210",
                }
            ),
            "official_designation": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Designation (optional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required = {"account_type", "contact_name", "contact_email", "contact_phone"}
        for name, field in self.fields.items():
            field.required = name in required


# =====================================================
# STEP 2 – ARN / APRN + PRODUCTS
# =====================================================


class BrokerProfileStep2Form(forms.ModelForm):

    products_allowed = forms.MultipleChoiceField(
        required=False,
        choices=PRODUCT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select allowed products.",
    )

    class Meta:
        model = BrokerProfile
        fields = [
            "arn_code",
            "arn_document",
            "arn_expiry_date",
            "aprn_code",
            "aprn_document",
            "aprn_expiry_date",
            "products_allowed",
        ]
        widgets = {
            "arn_document": SimpleFileInput(),
            "aprn_document": SimpleFileInput(),
            "arn_expiry_date": forms.DateInput(attrs={"type": "date"}),
            "aprn_expiry_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        data = super().clean()

        if data.get("arn_code") and not data.get("arn_document"):
            self.add_error(
                "arn_document", "ARN document is required if ARN code is provided."
            )

        for field in ("arn_expiry_date", "aprn_expiry_date"):
            d = data.get(field)
            if d and d < timezone.now().date():
                self.add_error(field, "Expiry date cannot be in the past.")

        return data


# =====================================================
# STEP 3 – PAN & BANK DETAILS
# =====================================================


class BrokerProfileStep3Form(forms.ModelForm):

    bank_account_number = forms.CharField(
        required=False, validators=[account_number_validator]
    )

    bank_ifsc = forms.CharField(required=False, validators=[ifsc_validator])

    class Meta:
        model = BrokerProfile
        fields = [
            "pan_number",
            "pan_document",
            "bank_name",
            "bank_account_number",
            "bank_ifsc",
            "cancelled_cheque",
        ]
        widgets = {
            "pan_document": SimpleFileInput(),
            "cancelled_cheque": SimpleFileInput(),
        }

    def clean(self):
        data = super().clean()

        if data.get("bank_account_number") and not data.get("bank_ifsc"):
            self.add_error(
                "bank_ifsc",
                "IFSC code is required when bank account number is provided.",
            )

        return data


# =====================================================
# STEP 4 – ADDRESS
# =====================================================


class BrokerProfileStep4Form(forms.ModelForm):

    pincode = forms.CharField(required=False, validators=[pincode_validator])

    class Meta:
        model = BrokerProfile
        fields = [
            "address_line1",
            "address_line2",
            "city",
            "state",
            "pincode",
            "country",
            "address_proof",
        ]
        widgets = {
            "address_line1": forms.TextInput(attrs={"class": "form-input"}),
            "address_line2": forms.TextInput(attrs={"class": "form-input"}),
            "city": forms.TextInput(attrs={"class": "form-input"}),
            "state": forms.TextInput(attrs={"class": "form-input"}),
            "address_proof": SimpleFileInput(),
        }


# =====================================================
# STEP 5 – ENTITY / GST DOCUMENTS (ACCOUNT-TYPE BASED)
# =====================================================


class BrokerProfileStep5Form(forms.ModelForm):

    gst_number = forms.CharField(required=False, validators=[gst_validator])

    class Meta:
        model = BrokerProfile
        fields = [
            "agreement_document",
            "moa_aoa",
            "board_resolution",
            "partnership_deed",
            "gst_number",
            "gst_document",
        ]
        widgets = {
            "agreement_document": SimpleFileInput(),
            "moa_aoa": SimpleFileInput(),
            "board_resolution": SimpleFileInput(),
            "partnership_deed": SimpleFileInput(),
            "gst_document": SimpleFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        account_type = self.instance.account_type

        # UI visibility
        if account_type != "pvt_ltd":
            self.fields["moa_aoa"].widget = forms.HiddenInput()
            self.fields["board_resolution"].widget = forms.HiddenInput()

        if account_type != "partnership":
            self.fields["partnership_deed"].widget = forms.HiddenInput()

    def clean(self):
        data = super().clean()
        account_type = self.instance.account_type

        # Backend enforcement
        if account_type == "pvt_ltd":
            if not data.get("moa_aoa"):
                self.add_error("moa_aoa", "MOA/AOA is required for company accounts.")
            if not data.get("board_resolution"):
                self.add_error(
                    "board_resolution",
                    "Board resolution is required for company accounts.",
                )

        if account_type == "partnership":
            if not data.get("partnership_deed"):
                self.add_error(
                    "partnership_deed",
                    "Partnership deed is required for partnership accounts.",
                )

        if data.get("gst_number") and not data.get("gst_document"):
            self.add_error(
                "gst_document", "GST document is required when GST number is provided."
            )

        return data