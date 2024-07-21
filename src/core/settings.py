from split_settings.tools import include

from core.conf.environ import env

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
CI = env("CI")

# Application definition
include(
    "conf/api.py",
    "conf/auth.py",
    "conf/common.py",
    "conf/database.py",
    "conf/http.py",
    "conf/i18n.py",
    "conf/installed_apps.py",
    "conf/middleware.py",
    "conf/templates.py",
)
