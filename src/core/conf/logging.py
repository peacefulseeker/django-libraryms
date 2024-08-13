from core.conf.environ import env

if env("DB_LOGGING_ENABLED", cast=bool, default=False):
    LOGGING = {
        "version": 1,
        "handlers": {
            "console": {"class": "logging.StreamHandler"},
        },
        "loggers": {
            "django.db": {
                "handlers": ["console"],
                "level": "DEBUG",
            },
        },
    }
