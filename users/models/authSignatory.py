# users/models/authSignatory.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.models.brokerProfile import BrokerProfile
from users.validators.validators import (
    pan_validator,
    mobile_validator,
    MigrationSafeFileValidators,
)

PDF_IMG_EXT = ["pdf", "png", "jpg", "jpeg", "gif"]



class AuthorizedSignatory(models.Model):

    broker = models.ForeignKey(
        BrokerProfile,
        on_delete=models.CASCADE,
        related_name="authorized_signatories",
    )

    auth_signatory_name = models.CharField(max_length=255, blank=True, null=True)
    auth_signatory_email = models.EmailField(blank=True, null=True)
    auth_signatory_phone = models.CharField(max_length=40, blank=True, null=True)
    auth_signatory_pan = models.CharField(max_length=20, blank=True, null=True)

    auth_signatory_kyc = models.FileField(
        upload_to="onboarding/signatory_kyc/",
        blank=True,
        null=True,
        validators=[MigrationSafeFileValidators(500, PDF_IMG_EXT)],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Authorized Signatory"
        verbose_name_plural = "Authorized Signatories"

    def clean(self):
        if self.broker.authorized_signatories.count() >= 4 and not self.pk:
            raise ValidationError(
                _("A broker can have a maximum of 4 authorized signatories.")
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.auth_signatory_name} ({self.broker.broker_code})"
