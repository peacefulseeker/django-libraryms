from split_settings.tools import include

from core.conf.environ import env

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

# there's no that much field for reversion to be crucial at this point
SIMPLE_HISTORY_REVERT_DISABLED = True

# Application definition
include(
    "conf/api.py",
    "conf/auth.py",
    "conf/common.py",
    "conf/database.py",
    "conf/security.py",
    "conf/i18n.py",
    "conf/installed_apps.py",
    "conf/middleware.py",
    "conf/templates.py",
    "conf/static.py",
    "conf/media.py",
    "conf/storages.py",
)
