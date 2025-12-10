import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent

# -- Basic security / runtime config (use env vars in production) --
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# -- Installed apps --
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "corsheaders",

    # Your apps
    "apps.kyc",
]

# -- Middleware --
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be high so CORS headers are added
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kyc_project.urls"

# -- Templates --
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # add project-level templates path here if you use one
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "kyc_project.wsgi.application"

# -- Database (sqlite for dev; configure env var for production) --
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DJANGO_DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DJANGO_DB_NAME", BASE_DIR / "db.sqlite3"),
        # For Postgres in production you can set DJANGO_DB_ENGINE and other vars
    }
}

# -- Internationalization / timezone --
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -- Static & Media --
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# If you want extra static folders during dev:
STATICFILES_DIRS = [
    BASE_DIR / "static",  # optionally create a top level static folder
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -- CORS (for local frontend dev) --
CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "True").lower() in ("1", "true", "yes")
# If you prefer to list origins explicitly:
# CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")

# -- Django REST Framework defaults --
REST_FRAMEWORK = {
    # Default permission class: change to IsAuthenticated for production
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    # Parse/renderer settings can be added if needed
    # "DEFAULT_AUTHENTICATION_CLASSES": [
    #     "rest_framework.authentication.SessionAuthentication",
    #     "rest_framework.authentication.TokenAuthentication",
    # ],
    # Optionally add throttling, pagination here
}

# -- File upload limits (bytes). Tune these values to your needs --
# These are safety defaults to avoid very large uploads in dev
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("DATA_UPLOAD_MAX_MEMORY_SIZE", 10 * 1024 * 1024))  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("FILE_UPLOAD_MAX_MEMORY_SIZE", 5 * 1024 * 1024))   # 5 MB
# Note: Django will use disk-based temporary files above these sizes.

# -- Simple logging for dev/debugging --
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
}

# -- Celery settings (optional, used if you add async OCR later) --
# Default broker/result point to Redis; change via env vars
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
# Celery task serialization configs (optional)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# -- Security defaults you should enable in production (not active here) --
# SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", 0))
# SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "False") == "True"
# CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")

# -- Default auto field --
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
