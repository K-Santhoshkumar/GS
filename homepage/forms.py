# homepage/forms.py
from django import forms
from django.core.validators import RegexValidator

MOBILE_VALIDATOR = RegexValidator(
    regex=r"^[0-9+\-\s]{8,15}$",
    message="Enter a valid mobile number (8–15 digits, +, - and spaces allowed)."
)

class ContactForm(forms.Form):
    name = forms.CharField(
        label="Name", max_length=100, strip=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Your full name", "autocomplete": "name", "class": "input", "maxlength": "100"
        }),
    )
    email = forms.EmailField(
        label="Email", max_length=254,
        widget=forms.EmailInput(attrs={
            "placeholder": "you@example.com", "autocomplete": "email", "class": "input", "maxlength": "254"
        }),
    )
    mobile = forms.CharField(
        label="Mobile", max_length=15, validators=[MOBILE_VALIDATOR], strip=True,
        widget=forms.TextInput(attrs={
            "placeholder": "e.g. +91 98xxxxxx", "autocomplete": "tel", "class": "input", "maxlength": "15"
        }),
    )
    query = forms.CharField(
        label="Your query", max_length=2000, strip=True,
        widget=forms.Textarea(attrs={
            "rows": 6, "placeholder": "How can we help?", "class": "textarea", "maxlength": "2000"
        }),
    )

    # ✅ pre-selected
    use_whatsapp = forms.BooleanField(
        required=False,
        initial=True,
        label="Use WhatsApp for communication and marketing",
        widget=forms.CheckboxInput(attrs={"class": "checkbox"})
    )
    agree_tos = forms.BooleanField(
    required=True,
    label="I agree to the Terms of Service",
    widget=forms.CheckboxInput(attrs={"class": "checkbox"}),
    error_messages={
        "required": "You must agree to the Terms of Service to continue."
    },
)


    source_url = forms.CharField(required=False, widget=forms.HiddenInput(), max_length=512)

    def clean_name(self): return " ".join(self.cleaned_data["name"].strip().split())
    def clean_mobile(self): return " ".join(self.cleaned_data["mobile"].strip().split())
    def clean_query(self): return self.cleaned_data["query"].strip()
    def clean_source_url(self):
        src = (self.cleaned_data.get("source_url") or "").strip()
        return src[:512]