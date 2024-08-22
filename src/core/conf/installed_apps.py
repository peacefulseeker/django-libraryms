from core.conf.environ import env

# fmt: off
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "django_filters",
    "django_celery_results",
    "django_celery_beat",
    "rest_framework",
    "rest_framework_simplejwt",
    "simple_history",
    "import_export",

    "apps.users",
    "apps.books",

    "core",
]
# fmt: on
if env("DEBUG"):
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
