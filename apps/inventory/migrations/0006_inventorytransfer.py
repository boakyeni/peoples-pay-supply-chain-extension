# Generated by Django 4.2.7 on 2023-11-17 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "inventory",
            "0005_alter_batch_options_alter_batchstorethrough_options_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="InventoryTransfer",
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
                ("reason", models.TextField(verbose_name="Reason for Scrap")),
                (
                    "approval",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.approval",
                    ),
                ),
            ],
        ),
    ]
