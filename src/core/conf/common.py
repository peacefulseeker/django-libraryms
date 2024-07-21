from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = "core.urls"

WSGI_APPLICATION = "core.wsgi.application"

STATIC_URL = "static/"
