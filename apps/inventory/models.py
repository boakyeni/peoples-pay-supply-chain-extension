from django.db import models
import uuid
from autoslug import AutoSlugField
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField
from django.core.validators import MinValueValidator
from decimal import Decimal
from measurement.measures import Volume, Weight
from django_measurement.models import MeasurementField

# Create your models here.


class Category(MPTTModel):
    """
    Inventory Category Table
    """

    name = models.CharField(
        max_length=100,
        verbose_name=_("Category"),
        unique=True,
    )

    slug = AutoSlugField(populate_from="name", unique=True)
    is_active = models.BooleanField(default=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="children",
        null=True,
        blank=True,
        verbose_name=_("Parent of Category"),
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = _("product category")
        verbose_name_plural = _("product categories")

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Product Brand Table"""

    name = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("Brand Name"),
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.UUIDField(
        verbose_name=_("Internal ID of Product"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    name = models.CharField(max_length=100)
    categories = TreeManyToManyField(Category, blank=True)
    description = models.TextField(blank=True, null=True)
    weight = MeasurementField(measurement=Weight, blank=True, null=True)
    volume = MeasurementField(
        measurement=Volume, blank=True, null=True, verbose_name=_("Total Batch Volume")
    )
    sku = models.CharField(max_length=100)
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("date product last created"),
        help_text=_("format: Y-m-d H:M:S"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_("date product last updated"),
        help_text=_("format: Y-m-d H:M:S"),
    )

    def __str__(self):
        return self.name


class ProductInventory(models.Model):
    """Master Inventory Table"""

    product = models.ForeignKey(
        Product,
        blank=True,
        null=True,
        related_name="inventory",
        on_delete=models.PROTECT,
    )

    brand = models.ForeignKey(
        Brand,
        verbose_name=_("Brand"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="products",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("product visibility"),
        help_text=_("format: true=product visible"),
    )
    retail_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name=_("Recommend Retail Price"),
    )
    store_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_("Regular Store Price"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("date product last created"),
        help_text=_("format: Y-m-d H:M:S"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_("date product last updated"),
        help_text=_("format: Y-m-d H:M:S"),
    )

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = _("Product Inventory")
        verbose_name_plural = _("Product Inventory")


class Customers(models.Model):
    """
    Store Customers
    """

    pass


class SalesZone(models.Model):
    """
    Sales Zone
    """

    pass


class Store(models.Model):
    """Distributer Van"""

    sale_zones = models.ManyToManyField(SalesZone, blank=True)
    customers = models.ManyToManyField(
        Customers,
        blank=True,
    )


class Batch(models.Model):
    batch_number = models.CharField(unique=True, max_length=250, default="n/a")
    product_inventory = models.ForeignKey(
        ProductInventory,
        verbose_name=_("Product"),
        related_name="batch",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    last_checked = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("inventory stock check date"),
        help_text=_("format: Y-m-d H:M:S, null-true, blank-true"),
    )
    quantity = models.IntegerField(
        default=0,
        verbose_name=_("Quantity of Product in Batch"),
        help_text=_("format: required, default-0"),
    )
    quantity_sold = models.IntegerField(
        default=0,
        verbose_name=_("Quantity Sold to Date"),
        help_text=_("format: required, default-0"),
    )
    # batch_weight = MeasurementField(
    #     measurement=Weight, blank=True, null=True, verbose_name=_("Total Batch Weight")
    # )
    # batch_volume = MeasurementField(
    #     measurement=Volume, blank=True, null=True, verbose_name=_("Total Batch Volume")
    # )
    expiry_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name_plural = _("Batches")


class BatchStoreThrough(models.Model):
    """
    Through model that holds the amount of units of a product that a van is carrying
    """

    batch = models.ForeignKey(
        Batch,
        verbose_name=_("Products"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="stores",
    )
    store = models.ForeignKey(
        Store,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Van or Store"),
        related_name="batches",
    )
    quantity = models.IntegerField(verbose_name=_("quantity sent to this store"))

    class Meta:
        verbose_name = _("Manufacter->Van")
        verbose_name_plural = _("Manufacter->Van")


class Approval(models.Model):
    class Status(models.TextChoices):
        APPROVED = "APPROVED", _("APPROVED")
        PENDING = "PENDING", _("PENDING")
        DECLINED = "DECLINED", _("DECLINED")

    approved = models.CharField(
        choices=Status.choices, max_length=20, default=Status.PENDING
    )
    issued_by = models.CharField(blank=True, null=True, max_length=100)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
    )


class InventoryScrap(models.Model):
    reason = models.TextField(verbose_name=_("Reason for Scrap"))
    approval = models.ForeignKey(
        Approval, blank=True, null=True, on_delete=models.PROTECT
    )
    van = models.ForeignKey(
        Store,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="scrap_requests",
    )
    date_of_request = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        ProductInventory, blank=True, null=True, on_delete=models.CASCADE
    )
    # cost_per_unit_scraped =


class InventoryTransfer(models.Model):
    reason = models.TextField(verbose_name=_("Reason for Scrap"))
    approval = models.ForeignKey(
        Approval, blank=True, null=True, on_delete=models.PROTECT
    )
