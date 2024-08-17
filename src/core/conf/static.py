from core.conf.common import BASE_DIR
from core.conf.environ import env

STATIC_URL = env("STATIC_URL", default="static/")
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    "src/core/assets",
]
