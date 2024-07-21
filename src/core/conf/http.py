# TODO: specify hosts from environment variables in prod
ALLOWED_HOSTS = ["*"]

# cross-origin communication with requests coming from frontend
CORS_ALLOWED_ORIGINS = [
    # "http://localhost:6060",
]

# admin only potentially
# TODO: not exactly sure whether CSRF needed with http only JWT cookie
CSRF_TRUSTED_ORIGINS = [
    # "http://localhost:6060",
]
