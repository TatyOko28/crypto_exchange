# Generated by Django 5.1.3 on 2024-11-24 20:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "order_type",
                    models.CharField(
                        choices=[("BUY", "Buy"), ("SELL", "Sell")], max_length=4
                    ),
                ),
                ("cryptocurrency", models.CharField(max_length=10)),
                ("amount", models.DecimalField(decimal_places=8, max_digits=18)),
                ("price", models.DecimalField(decimal_places=2, max_digits=18)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ACTIVE", "Active"),
                            ("PENDING", "Pending"),
                            ("COMPLETED", "Completed"),
                            ("CANCELLED", "Cancelled"),
                            ("FAILED", "Failed"),
                        ],
                        default="ACTIVE",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("security_code_verified", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=8, max_digits=18)),
                ("price", models.DecimalField(decimal_places=2, max_digits=18)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("INITIATED", "Initiated"),
                            ("BUYER_CONFIRMED", "Buyer Confirmed"),
                            ("SELLER_CONFIRMED", "Seller Confirmed"),
                            ("COMPLETED", "Completed"),
                            ("FAILED", "Failed"),
                            ("DISPUTED", "Disputed"),
                        ],
                        default="INITIATED",
                        max_length=20,
                    ),
                ),
                ("buyer_security_confirmed", models.BooleanField(default=False)),
                ("seller_security_confirmed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "buyer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buying_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="market.order"
                    ),
                ),
                (
                    "seller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="selling_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]