from core.conf.environ import env

STORAGES = {
    "default": {
        "BACKEND": env("DEFAULT_FILE_STORAGE", cast=str, default="django.core.files.storage.FileSystemStorage"),
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
if not env("DEBUG"):
    STORAGES["default"]["staticfiles"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"
