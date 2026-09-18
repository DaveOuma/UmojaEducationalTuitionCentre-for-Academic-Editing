"""Development settings. Never used in production."""

from .base import *  # noqa: F401,F403
from .base import config

DEBUG = True

# Convenient local default; still overridable via ALLOWED_HOSTS env var.
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=lambda v: v.split(","))

INTERNAL_IPS = ["127.0.0.1"]

# Local/dev file storage until Phase 5 wires in real object storage.
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False