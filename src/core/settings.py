from split_settings.tools import include

from core.conf.environ import env

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
CI = env("CI")

ALLOWED_HOSTS = ["*"]

# Application definition
include(
    "conf/common.py",
    "conf/api.py",
    "conf/auth.py",
    "conf/database.py",
    "conf/installed_apps.py",
    "conf/middleware.py",
    "conf/templates.py",
    "conf/i18n.py",
)
