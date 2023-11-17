# Generated by Django 4.2.7 on 2023-11-15 15:20

from django.db import migrations, models
import django_measurement.models
import measurement.measures.volume
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0002_batch_brand_store_remove_product_price_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="category",
            field=mptt.fields.TreeManyToManyField(
                blank=True, null=True, to="inventory.category"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="volume",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.measures.volume.Volume,
                null=True,
                verbose_name="Total Batch Volume",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(
                max_length=100, unique=True, verbose_name="Category"
            ),
        ),
    ]
