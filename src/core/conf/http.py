from core.conf.environ import env

if not env("DEBUG"):
    ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(" ")
    CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS").split(" ")
    CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS").split(" ")
    print("CSRF_TRUSTED_ORIGINS", CSRF_TRUSTED_ORIGINS)
    print("CORS_ALLOWED_ORIGINS", CORS_ALLOWED_ORIGINS)
    print("ALLOWED_HOSTS", ALLOWED_HOSTS)
