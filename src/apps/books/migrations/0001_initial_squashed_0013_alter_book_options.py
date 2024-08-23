# Generated by Django 5.0.8 on 2024-08-23 16:29

import django.core.validators
import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    replaces = [
        ("books", "0001_initial"),
        ("books", "0002_add_book_reservation_order_models"),
        ("books", "0003_alter_reservation_term"),
        ("books", "0004_order_change_reason_order_last_modified_by_and_more"),
        ("books", "0005_book_cover_alter_book_isbn"),
        ("books", "0006_alter_author_year_of_birth_and_more"),
        ("books", "0007_historicalorder_reservation_order_reservation"),
        ("books", "0008_alter_book_pages_description_and_more"),
        ("books", "0009_alter_reservation_options"),
        ("books", "0010_historicalorder_member_notified_and_more"),
        ("books", "0011_alter_reservation_options"),
        ("books", "0012_alter_author_year_of_birth_and_more"),
        ("books", "0013_alter_book_options"),
    ]

    dependencies = [
        ("users", "0002_user_is_librarian_user_is_member"),
        ("users", "0003_make_user_email_unique"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("year_of_birth", models.PositiveSmallIntegerField(null=True)),
                ("year_of_death", models.PositiveSmallIntegerField(null=True)),
            ],
            options={
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("title", models.CharField(max_length=200, unique=True)),
                (
                    "language",
                    models.CharField(
                        choices=[("lv", "Latvian"), ("en", "English"), ("ru", "Russian"), ("de", "German"), ("es", "Spanish"), ("fr", "French")], max_length=2
                    ),
                ),
                ("published_at", models.PositiveSmallIntegerField(verbose_name="Year of publishing")),
                ("pages", models.PositiveSmallIntegerField(verbose_name="Number of pages")),
                ("pages_description", models.CharField(max_length=100, null=True, verbose_name="Extra description for pages")),
                ("isbn", models.CharField(max_length=13, verbose_name="ISBN")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Publisher",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("city", models.CharField(max_length=100, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddConstraint(
            model_name="author",
            constraint=models.UniqueConstraint(fields=("first_name", "last_name"), name="unique_author_name"),
        ),
        migrations.AddField(
            model_name="book",
            name="author",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="books.author"),
        ),
        migrations.AddField(
            model_name="book",
            name="publisher",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="books.publisher"),
        ),
        migrations.AlterModelOptions(
            name="book",
            options={"ordering": ["-modified_at"]},
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("R", "Reserved"), ("I", "Issued"), ("C", "Completed"), ("RF", "Refused"), ("X", "Cancelled")], default="R", max_length=2
                    ),
                ),
                (
                    "term",
                    models.DateField(
                        blank=True, default=None, help_text="Date when reservation expires, 14 days by default", null=True, verbose_name="Due date"
                    ),
                ),
                ("member", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="users.member")),
            ],
            options={
                "ordering": [models.OrderBy(models.F("modified_at"), descending=True, nulls_last=True)],
            },
        ),
        migrations.AddField(
            model_name="book",
            name="reservation",
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="books.reservation"),
        ),
        migrations.AddField(
            model_name="book",
            name="cover",
            field=models.ImageField(blank=True, help_text="The cover image of book", upload_to="books/covers/", verbose_name="Cover image"),
        ),
        migrations.AlterField(
            model_name="book",
            name="isbn",
            field=models.CharField(max_length=13, unique=True, verbose_name="ISBN"),
        ),
        migrations.AlterField(
            model_name="book",
            name="pages_description",
            field=models.CharField(blank=True, default="", max_length=100, verbose_name="Extra description for pages"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="publisher",
            name="city",
            field=models.CharField(blank=True, default="", max_length=100),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="HistoricalOrder",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[("U", "Unprocessed"), ("R", "Refused"), ("Q", "In Queue"), ("MC", "Member Cancelled"), ("P", "Processed")],
                        default="U",
                        max_length=2,
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                (
                    "book",
                    models.ForeignKey(
                        blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name="+", to="books.book"
                    ),
                ),
                ("history_user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL)),
                (
                    "last_modified_by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name="+", to="users.member"
                    ),
                ),
                (
                    "reservation",
                    models.ForeignKey(
                        blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name="+", to="books.reservation"
                    ),
                ),
                ("member_notified", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "historical order",
                "verbose_name_plural": "historical orders",
                "db_table": "books_order_history",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
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
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("U", "Unprocessed"), ("R", "Refused"), ("Q", "In Queue"), ("MC", "Member Cancelled"), ("P", "Processed")],
                        default="U",
                        max_length=2,
                    ),
                ),
                ("book", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="books.book")),
                ("member", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="users.member")),
                ("change_reason", models.CharField(blank=True, max_length=100, verbose_name="Optional comment or change reason")),
                (
                    "last_modified_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL),
                ),
                ("reservation", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="books.reservation")),
                ("member_notified", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AlterModelOptions(
            name="book",
            options={"ordering": [models.OrderBy(models.F("modified_at"), descending=True, nulls_last=True)]},
        ),
    ]
