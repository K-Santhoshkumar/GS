import os
from django import forms
from users.models.brokerProfile import BrokerProfile, PRODUCT_CHOICES
from users.utils.widgets import SimpleFileInput


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
            "contact_email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "contact_phone": forms.TextInput(attrs={"placeholder": "+91 9876543210"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required = {"account_type", "contact_name", "contact_email", "contact_phone"}

        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-input")
            field.required = name in required


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

    def __init__(self, *args, **kwargs):
        inst = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        if inst and inst.products_allowed:
            self.initial["products_allowed"] = inst.products_allowed


class BrokerProfileStep3Form(forms.ModelForm):

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


class BrokerProfileStep4Form(forms.ModelForm):

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
            "agreement_document",
            "moa_aoa",
            "board_resolution",
            "partnership_deed",
            "gst_number",
            "gst_document",
            "auth_signatory_name",
            "auth_signatory_email",
            "auth_signatory_phone",
            "auth_signatory_pan",
            "auth_signatory_kyc",
            "notes",
        ]
        widgets = {
            "address_proof": SimpleFileInput(),
            "agreement_document": SimpleFileInput(),
            "moa_aoa": SimpleFileInput(),
            "board_resolution": SimpleFileInput(),
            "partnership_deed": SimpleFileInput(),
            "gst_document": SimpleFileInput(),
            "auth_signatory_kyc": SimpleFileInput(),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
