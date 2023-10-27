from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class AddProductToOrderSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Product
        fields = ("product_id",)