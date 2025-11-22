import os
import imghdr
from django.core.exceptions import ValidationError


# -----------------------
# Helper validators
# -----------------------
def file_size_validator(max_kb):

    def _validator(file_obj):
        if file_obj and file_obj.size > max_kb * 1024:
            raise ValidationError(f"File size must be <= {max_kb} KB")

    # --- FIX: give Django a stable name ---
    _validator.__name__ = f"file_size_validator_{max_kb}"

    return _validator


def file_extension_validator(allowed_exts):
    allowed_exts = [e.lower() for e in allowed_exts]

    def _validator(file_obj):
        if not file_obj:
            return
        name = file_obj.name.lower()
        ext = os.path.splitext(name)[1].lstrip(".").lower()
        if ext not in allowed_exts:
            raise ValidationError(f"Allowed file types: {', '.join(allowed_exts)}")

    # --- FIX: give Django a stable name ---
    ext_label = "_".join(allowed_exts)
    _validator.__name__ = f"file_extension_validator_{ext_label}"

    return _validator


# Small combined validator factory
def file_validators(max_kb, allowed_exts):
    return [
        file_size_validator(max_kb),
        file_extension_validator(allowed_exts),
    ]


# Allowed extensions common set
PDF_IMG_EXT = ["pdf", "png", "jpg", "jpeg", "gif"]
