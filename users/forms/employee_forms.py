# users/forms/employee_forms.py

from django import forms
from users.models.employeeProfile import EmployeeProfile


class EmployeeStep1Form(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ["name", "employee_code", "contact_phone", "email", "designation"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "employee_code": forms.TextInput(attrs={"class": "form-control"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "designation": forms.TextInput(attrs={"class": "form-control"}),
        }


class EmployeeStep2Form(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = [
            "address",
            "dummy1",
            "dummy2",
            "dummy3",
            "dummy4",
            "dummy5",
        ]
        widgets = {
            f: (
                forms.Textarea(attrs={"class": "form-control", "rows": 3})
                if f == "address"
                else forms.TextInput(attrs={"class": "form-control"})
            )
            for f in fields
        }
