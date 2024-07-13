import environ

from core.conf.common import BASE_DIR

env = environ.Env(
    SECRET_KEY=(str, "not-so-secret"),
    DEBUG=(bool, False),
    CI=(bool, False),
)

envpath = BASE_DIR / ".env"

if envpath.exists():
    env.read_env(envpath)
