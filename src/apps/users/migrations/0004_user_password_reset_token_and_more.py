# Generated by Django 5.0.8 on 2024-08-27 09:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_make_user_email_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="password_reset_token",
            field=models.UUIDField(blank=True, editable=False, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="user",
            name="password_reset_token_created_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
