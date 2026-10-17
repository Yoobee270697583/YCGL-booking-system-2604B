import os

# Throwaway values for local testing only. None of these are real secrets.
os.environ.setdefault("SECRET_KEY", "local-testing-only-not-a-secret")
os.environ.setdefault("ADMIN_URL", "local-admin")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1,.cloudshell.dev")
os.environ.setdefault("CSRF_TRUSTED_ORIGINS", "https://*.cloudshell.dev")

from .settings import *  # noqa: E402,F401,F403

# A local SQLite file instead of the real Cloud SQL database.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "local.sqlite3",
    }
}