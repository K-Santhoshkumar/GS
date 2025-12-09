# users/validators/validators.py

import os
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.conf import settings


# ---------------------------------------------------------
# 🔥 FILE EXTENSION CONSTANTS (Shared Across All Models)
# ---------------------------------------------------------
PDF_EXT = ["pdf"]
IMAGE_EXT = ["png", "jpg", "jpeg"]
IMAGE_PDF_EXT = ["pdf", "png", "jpg", "jpeg", "gif"]

# Extendable master list
ALL_EXT = list(set(PDF_EXT + IMAGE_EXT))


# ---------------------------------------------------------
# 🔥 REGEX VALIDATORS (Reusable)
# ---------------------------------------------------------
pan_validator = RegexValidator(
    regex=r"^[A-Z]{5}[0-9]{4}[A-Z]$",
    message="Enter a valid PAN (e.g. ABCDE1234F). Use uppercase letters.",
)

mobile_validator = RegexValidator(
    regex=r"^[6-9]\d{9}$",
    message="Enter a valid 10-digit Indian mobile number starting with 6-9.",
)


# ---------------------------------------------------------
# 🔥 MIGRATION-SAFE FILE VALIDATOR
# ---------------------------------------------------------
class MigrationSafeFileValidators:
    """
    Safe validator for file extensions + size.
    Works even if file missing on disk (safe for migrations).
    """

    def __init__(self, max_kb, allowed_exts):
        self.max_kb = int(max_kb)
        self.allowed_exts = [ext.lower() for ext in allowed_exts]

    def __call__(self, file_obj):
        if not file_obj:
            return

        # --- Size check ---
        try:
            size = getattr(file_obj, "size", None)
            if size is None and hasattr(file_obj, "file"):
                file_obj.file.seek(0, os.SEEK_END)
                size = file_obj.file.tell()
                file_obj.file.seek(0)
        except Exception:
            size = None

        if size and size > self.max_kb * 1024:
            raise ValidationError(f"File size must be ≤ {self.max_kb} KB")

        # --- Extension check ---
        try:
            name = getattr(file_obj, "name", "")
            ext = os.path.splitext(name)[1].lstrip(".").lower()
            if ext and ext not in self.allowed_exts:
                raise ValidationError(
                    f"Allowed file types: {', '.join(self.allowed_exts)}"
                )
        except Exception:
            return

    def deconstruct(self):
        return (
            "users.validators.validators.MigrationSafeFileValidators",
            [self.max_kb, list(self.allowed_exts)],
            {},
        )


# ---------------------------------------------------------
# 🔥 AUTO-CREATE UPLOAD FOLDERS SAFELY
# ---------------------------------------------------------
def ensure_upload_folder(path: str):
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    directory = os.path.dirname(full_path)
    os.makedirs(directory, exist_ok=True)
    return path
