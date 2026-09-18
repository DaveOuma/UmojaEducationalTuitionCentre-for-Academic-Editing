"""
Production settings.

Every value that matters for security is required from the environment
(no defaults that silently degrade safety) — the process should fail to
start rather than run insecurely misconfigured.
"""

from .base import *  # noqa: F401,F403
from .base import config

DEBUG = False

# No default: a production deploy with no ALLOWED_HOSTS set should fail
# loudly rather than accidentally accept Host headers from anywhere.
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=lambda v: v.split(","))

# ---------------------------------------------------------------------------
# HTTPS / transport security
# ---------------------------------------------------------------------------

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

# ---------------------------------------------------------------------------
# Object storage — private, not the application filesystem (spec section 13)
#
# Configured for S3-compatible storage. Wired fully in Phase 5; present
# here so production never falls back to local disk for client manuscripts.
# ---------------------------------------------------------------------------

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL", default=None)
AWS_DEFAULT_ACL = None  # private by default — spec section 12/13
AWS_QUERYSTRING_EXPIRE = config("AWS_QUERYSTRING_EXPIRE", default=300, cast=int)

# ---------------------------------------------------------------------------
# Logging — access/download logging feeds the AuditLog model (Phase 5+);
# this baseline ensures errors are never silently swallowed in production.
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}