from django import forms
from users.models.authSignatory import AuthorizedSignatory
from users.validators.validators import pan_validator, mobile_validator
from users.utils.widgets import SimpleFileInput


class AuthorizedSignatoryForm(forms.ModelForm):

    class Meta:
        model = AuthorizedSignatory
        fields = [
            "auth_signatory_name",
            "auth_signatory_email",
            "auth_signatory_phone",
            "auth_signatory_pan",
            "auth_signatory_kyc",
        ]
        widgets = {
            "auth_signatory_name": forms.TextInput(attrs={"class": "form-input"}),
            "auth_signatory_email": forms.EmailInput(attrs={"class": "form-input"}),
            "auth_signatory_phone": forms.TextInput(attrs={"class": "form-input"}),
            "auth_signatory_pan": forms.TextInput(attrs={"class": "form-input"}),
            "auth_signatory_kyc": SimpleFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Make ALL fields required
        for field in self.fields.values():
            field.required = True
