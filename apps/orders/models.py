from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.inventory.models import Product
import uuid

# Create your models here.

class Order(models.Model):
    STATUS = (
      ('PENDING', 'PENDING'),
      ("PARTIAL", 'PARTIAL'),
      ("FULFILLED", 'FULFILLED'),
    )
    CURRENCY = (
        ("GHC", "GHC ₵"),
    )

    placed_by = models.CharField(verbose_name=_("Buyer ID"), max_length=64)
    placed_to = models.CharField(verbose_name=_("Seller ID"), max_length=64)
    order_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Order Time"))
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS, default=STATUS[0][0])
    currency = models.CharField(max_length=50, choices=CURRENCY, default=CURRENCY[0][0])
    note = models.TextField(verbose_name=_("Note"), blank=True, null=True)



class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name="details", on_delete=models.CASCADE, verbose_name=_("Order ID"), default=0)
    item_code = models.ForeignKey(Product, on_delete=models.CASCADE, default=uuid.uuid4)
    quantity = models.IntegerField(default=0)
    subtotal = models.DecimalField(max_digits=25, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def product_name(self):
        return self.item_code.name

    @property
    def unit_price(self):
        return self.item_code.price