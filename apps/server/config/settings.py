"""
Django settings for the Todo backend (project ``config``).

Tuned for BOTH local development and the production container image:

* Secrets / DEBUG / hosts come from environment variables.
* WhiteNoise serves the built React SPA same-origin when ``apps/server/spa``
  exists (the Dockerfile copies the client build there); locally that directory
  is absent, so Django only serves the API and Vite serves the UI on :5173.
* CORS is opened for the Vite dev origin only.

See https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: bool) -> bool:
    """Read a boolean from the environment (``"1/true/yes/on"`` → ``True``)."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-g1u7z$5^zm0ylp81dj43sax30zm5w-xp7)1+&y0179+0k$uqij",
)

# SECURITY WARNING: don't run with debug turned on in production!
# Defaults to False so the container is safe by default; enable locally via env.
DEBUG = _env_bool("DEBUG", False)

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "todos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise serves static assets and the SPA right after security.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# SQLite by default; path is configurable so it can live in the container
# working directory (which is writable). No extra drivers required.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DB_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Serve the built React SPA same-origin via WhiteNoise when present.
# The Dockerfile copies the client build into apps/server/spa/ (index.html +
# assets/...). Locally the directory is absent, so only the API is served and
# Vite handles the UI on :5173.
_SPA_DIR = BASE_DIR / "spa"
if _SPA_DIR.exists():  # pragma: no cover
    # This branch only runs in the production container image where the React
    # build has been copied into apps/server/spa/.  Testing it would require
    # mocking the filesystem at import time; the Docker CI run validates it end-
    # to-end instead.
    WHITENOISE_ROOT = str(_SPA_DIR)
    WHITENOISE_INDEX_FILE = True


# Django REST Framework — JSON only (no browsable API; no admin static needed).
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "EXCEPTION_HANDLER": "todos.exceptions.custom_exception_handler",
}


# CORS — local Vite dev origin only. In the container the SPA is same-origin,
# so CORS is not exercised there.
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Logging — structured console output; level driven by env so the container can
# be silent (WARNING) while local dev can be verbose (DEBUG).
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    # All loggers propagate to root by default, so only root needs a handler.
    # Per-logger entries are added here only when a different level or handler
    # is needed (e.g. silencing noisy third-party libraries).
    "root": {
        "handlers": ["console"],
        "level": _LOG_LEVEL,
    },
}
