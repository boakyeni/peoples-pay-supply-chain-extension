from django.contrib import admin
from .models import (
    Product,
    ProductInventory,
    Category,
    BatchStoreThrough,
    Store,
    Batch,
    InventoryScrap,
    Brand,
)

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_id", "name", "sku"]


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductInventory)
admin.site.register(Category)
admin.site.register(BatchStoreThrough)
admin.site.register(Store)
admin.site.register(Batch)
admin.site.register(InventoryScrap)
admin.site.register(Brand)
