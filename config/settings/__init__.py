"""
Selects which settings module to load based on the DJANGO_ENV
environment variable. Defaults to "development" so a bare checkout
never accidentally boots with production assumptions, but any real
deployment must set DJANGO_ENV=production explicitly.
"""

import os

_env = os.environ.get("DJANGO_ENV", "development")

if _env == "production":
    from .production import *  # noqa: F401,F403
else:
    from .development import *  # noqa: F401,F403