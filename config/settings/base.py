"""
Base settings for the Umoja Academic & Scientific Editing platform.

Environment-specific settings (development.py, production.py) import
everything from this module and override only what needs to differ.
Nothing here should contain secrets: every credential is read from
the environment via python-decouple, with safe local-only defaults
where that makes sense (never for production credentials).
"""

from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Core security settings
# ---------------------------------------------------------------------------

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

# ---------------------------------------------------------------------------
# Business / branding configuration
#
# The business name and service brand must be configurable rather than
# hard-coded into templates (spec section 5). Templates should read these
# via the "umoja" context processor below, never hard-code the strings.
# ---------------------------------------------------------------------------

BUSINESS_NAME = config("BUSINESS_NAME", default="Umoja Educational Tuition Centre")
SERVICE_BRAND_NAME = config("SERVICE_BRAND_NAME", default="Umoja Academic & Scientific Editing")
SUPPORT_EMAIL = config("SUPPORT_EMAIL", default="support@example.com")

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    # Registered here as each phase introduces it, e.g. "rest_framework".
]

LOCAL_APPS = [
    "accounts",
    "profiles",
    "organizations",
    "website",
    "assignments",
    # "documents", "payments", "messaging" are added in later phases.
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.business_identity",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database
#
# PostgreSQL only. DATABASE_URL is required in every environment; there is
# no sqlite fallback, so development matches production behaviour.
# ---------------------------------------------------------------------------

import dj_database_url  # noqa: E402

DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL"),
        conn_max_age=600,
    )
}

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

# Email is the login identifier from day one (see accounts.models.User).
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:dashboard_redirect"
LOGOUT_REDIRECT_URL = "website:home"

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Email (transactional notifications — spec section 31)
# ---------------------------------------------------------------------------

EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=SUPPORT_EMAIL)

# ---------------------------------------------------------------------------
# Redis / Celery (spec section 48 — wired here, workers added in a later
# phase once there are tasks worth running asynchronously).
# ---------------------------------------------------------------------------

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# ---------------------------------------------------------------------------
# Session security defaults (tightened further in production.py)
# ---------------------------------------------------------------------------

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # HTMX needs to read this cookie to set the header
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days
X_FRAME_OPTIONS = "DENY"

# HTMX sends the CSRF token as a request header, not a form field.
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"