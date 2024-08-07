# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
from core.conf.environ import env

LANGUAGE_CODE = "en-us"

TIME_ZONE = env("TIME_ZONE")

USE_I18N = True

USE_TZ = True
