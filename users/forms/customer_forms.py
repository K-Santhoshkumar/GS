from django import forms
from users.models.customerProfile import CustomerProfile
from users.models.brokerProfile import BrokerProfile
from users.models.employeeProfile import EmployeeProfile
from users.utils.widgets import SimpleFileInput


# ---------------------------------------------------------
# STEP 1 — BASIC DETAILS
# ---------------------------------------------------------
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
            "contact_phone": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "9876543210"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-input", "autocomplete": "email"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = {"name", "pan", "contact_phone"}

        for name, field in self.fields.items():
            field.required = name in required_fields


# ---------------------------------------------------------
# STEP 2 — ADDRESS
# ---------------------------------------------------------
class CustomerStep2Form(forms.ModelForm):
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


# ---------------------------------------------------------
# STEP 3 — DOCUMENTS + ASSIGNMENT
# ---------------------------------------------------------
class CustomerStep3Form(forms.ModelForm):

    broker = forms.ModelChoiceField(
        queryset=BrokerProfile.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    employee = forms.ModelChoiceField(
        queryset=EmployeeProfile.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    class Meta:
        model = CustomerProfile
        fields = [
            "pan_copy",
            "address_proof",
            "broker",
            "employee",
        ]
        widgets = {
            "pan_copy": SimpleFileInput(),
            "address_proof": SimpleFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if not isinstance(field.widget, SimpleFileInput):
                field.widget.attrs.setdefault("class", "form-input")
