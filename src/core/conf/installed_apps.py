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
    "rest_framework",
    "rest_framework_simplejwt",
    "simple_history",
    "import_export",

    "apps.users",
    "apps.books",

    "core",
]
# fmt: on
