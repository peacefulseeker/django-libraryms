# Generated by Django 5.1 on 2024-08-31 15:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0015_alter_reservation_options"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="reservation",
            name="term",
            field=models.DateField(blank=True, default=None, help_text="Reservation term", null=True, verbose_name="Due date"),
        ),
        migrations.CreateModel(
            name="ReservationExtension",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("status", models.CharField(choices=[("R", "Requested"), ("A", "Approved"), ("RF", "Refused"), ("X", "Cancelled")], default="R", max_length=2)),
                (
                    "processed_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL),
                ),
                ("reservation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="extensions", to="books.reservation")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
