from rest_framework import serializers, status

from rest_framework.response import Response

from .models import Order, OrderDetail
from apps.inventory.models import Product
from apps.inventory.serializers import ProductSerializer, AddProductToOrderSerializer


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    order_details = serializers.SerializerMethodField()
    products = serializers.ListField(write_only=True)

    class Meta:
        model = Order
        fields = "__all__"

    def create(self, validated_data):
        if "products" in validated_data:
            products = validated_data.pop("products")

        # merchant id, customer data, note
        order_instance = Order.objects.create(**validated_data)
        for product in products:
            product_instance = Product.objects.get(product_id=product["product_id"])

            total = float(product["quantity"] * product_instance.inventory.store_price)

            order_detail_instance = OrderDetail.objects.create(
                order=order_instance,
                item_code=product_instance,
                quantity=product["quantity"],
            )
            # Tax should mostly be set depending on Product Category
            # For now we use the default tax
            tax = total * order_detail_instance.tax

            order_detail_instance.subtotal = total + tax
            order_detail_instance.save()
        return order_instance

    def get_order_details(self, obj):
        return OrderDetailSerializer(obj.details.all(), many=True).data
