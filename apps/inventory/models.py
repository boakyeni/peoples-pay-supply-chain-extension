from django.db import models

# Create your models here.

class Product(models.Model):
  product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100)
  weight = models.DecimalField(max_digits=5, decimal_places=2)
  sku = models.CharField(max_length=100)
  type = models.CharField(max_length=100)
  price = models.DecimalFieldField(max_digits=6, decimal_places=2)

  def __str__(self):
    return self.name