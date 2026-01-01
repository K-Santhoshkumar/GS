from django import forms
from users.models.employeeProfile import EmployeeProfile
from users.validators.validators import mobile_validator


# =====================================================
# STEP 1 – BASIC DETAILS
# =====================================================
class EmployeeStep1Form(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = [
            "name",
            "employee_code",
            "contact_phone",
            "email",
            "designation",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "employee_code": forms.TextInput(attrs={"class": "form-input"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "designation": forms.TextInput(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required = {"name", "employee_code", "contact_phone", "email"}
        for name, field in self.fields.items():
            field.required = name in required


# =====================================================
# STEP 2 – ADDRESS DETAILS
# =====================================================
class EmployeeStep2Form(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ["address"]
        widgets = {
            "address": forms.Textarea(
                attrs={"class": "form-input", "rows": 3}
            )
        }

    def clean(self):
        data = super().clean()
        if not data.get("address"):
            self.add_error("address", "Address is required.")
        return data
