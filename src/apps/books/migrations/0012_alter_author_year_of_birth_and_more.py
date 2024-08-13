# Generated by Django 5.0.7 on 2024-08-13 05:52

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0011_alter_reservation_options"),
        ("users", "0003_make_user_email_unique"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="year_of_birth",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2024, message="Year of birth cannot be greater than current year")]
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="year_of_death",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2024, message="Year of birth cannot be greater than current year")]
            ),
        ),
        migrations.AlterField(
            model_name="book",
            name="author",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="books", to="books.author"),
        ),
        migrations.AlterField(
            model_name="book",
            name="publisher",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="books", to="books.publisher"),
        ),
        migrations.AlterField(
            model_name="order",
            name="book",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="books.book"),
        ),
        migrations.AlterField(
            model_name="order",
            name="member",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="users.member"),
        ),
    ]