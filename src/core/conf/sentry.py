from core.conf.environ import env

SENTRY_DSN = env("SENTRY_DSN", cast=str, default="")


if not env("DEBUG") and SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    def strip_user_data(event, hint):
        if event.get("user"):
            user = event["user"]
            event["user"] = {
                "id": user.get("id"),
            }
        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.8,
        send_default_pii=True,
        before_send=strip_user_data,
    )
