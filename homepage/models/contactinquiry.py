
from django.db import models

class ContactInquiry(models.Model):
    """
    Stores 'Get in touch' enquiries.
    Captures consent, source URL, and useful metadata for ops/analytics.
    """

    # Form fields
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    mobile = models.CharField(max_length=15)
    query = models.TextField(max_length=2000)

    # Checkboxes
    use_whatsapp = models.BooleanField(default=False)
    agree_tos = models.BooleanField(default=False)

    # Hidden source
    source_url = models.URLField(max_length=512, blank=True)

    # Ops / metadata
    status = models.CharField(
        max_length=20,
        choices=[("NEW", "New"), ("IN_PROGRESS", "In progress"), ("CLOSED", "Closed")],
        default="NEW",
        help_text="Internal handling status"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    consent_timestamp = models.DateTimeField(null=True, blank=True)

    # Useful request metadata (non-PII beyond UA/IP)
    user_agent = models.TextField(blank=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["mobile"]),
            models.Index(fields=["status", "submitted_at"]),
        ]

    def __str__(self):
        return f"{self.name} — {self.email} — {self.submitted_at:%Y-%m-%d %H:%M}"