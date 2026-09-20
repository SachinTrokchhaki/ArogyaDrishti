"""Upload validation and optional antivirus scanning."""
import os
import shutil
import subprocess
import tempfile


MAX_REPORT_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAGIC_BYTES = {
    "pdf": (b"%PDF",),
    "png": (b"\x89PNG\r\n\x1a\n",),
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
}


def validate_upload(file_name, content_type, content):
    """Validate size, extension, MIME type, and file signature."""
    extension = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    if extension not in ALLOWED_EXTENSIONS:
        return False, "File type not supported. Allowed: PDF, PNG, JPG, JPEG"
    if len(content) == 0:
        return False, "The uploaded file is empty"
    if len(content) > MAX_REPORT_SIZE:
        return False, "File too large. Maximum size: 10MB"

    if not any(content.startswith(signature) for signature in MAGIC_BYTES[extension]):
        return False, "The file content does not match its extension"

    expected_types = {
        "pdf": {"application/pdf"},
        "png": {"image/png"},
        "jpg": {"image/jpeg", "image/jpg"},
        "jpeg": {"image/jpeg", "image/jpg"},
    }
    if content_type and content_type not in expected_types[extension]:
        return False, "The declared content type does not match the file"

    return True, None


def scan_for_malware(content):
    """Run ClamAV when explicitly enabled; otherwise return a safe result."""
    if os.getenv("CLAMAV_SCAN_ENABLED", "false").lower() != "true":
        return True, "antivirus_not_configured"

    scanner = shutil.which("clamdscan") or shutil.which("clamscan")
    if not scanner:
        return False, "ClamAV is enabled but no scanner is installed"

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".upload") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        result = subprocess.run(
            [scanner, "--no-summary", temp_path],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            return False, "The upload failed the malware scan"
        return True, "clean"
    except (OSError, subprocess.TimeoutExpired):
        return False, "The malware scan could not be completed"
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
