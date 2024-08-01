from core.conf.common import BASE_DIR
from core.conf.environ import env

STATIC_URL = env("STATIC_URL", default="static/")
STATIC_ROOT = BASE_DIR / "staticfiles"

if not env("DEBUG"):
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
