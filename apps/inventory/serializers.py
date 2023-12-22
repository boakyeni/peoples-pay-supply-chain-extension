from rest_framework import serializers
from .models import (
    Product,
    ProductInventory,
    Brand,
    Store,
    Batch,
    Category,
    SalesZone,
    Customer,
    InventoryTransfer,
    InventoryScrap,
    ContactNumber,
)
from measurement.measures import *
from measurement.utils import guess


class MeasurementField(serializers.Field):
    def to_representation(self, obj):
        if obj:
            # Loop through possible units and find the one used
            for unit in obj.UNITS:
                if getattr(obj, unit) == obj.standard:
                    return {"value": getattr(obj, unit), "unit": unit}
            return None
        return None

    def to_internal_value(self, data):
        if not isinstance(data, dict) or "value" not in data or "unit" not in data:
            raise serializers.ValidationError(
                "Measurement must be a dictionary with 'value' and 'unit'"
            )

        value = data["value"]
        unit = data["unit"]
        try:
            measurement_class = guess(value, unit, measures=[Weight, Volume])
        except ValueError:
            raise serializers.ValidationError(f"Unknown unit: {unit}")

        try:
            print(measurement_class)
            return measurement_class
        except (TypeError, ValueError):
            raise serializers.ValidationError("Invalid measurement value")


class ProductSerializer(serializers.ModelSerializer):
    volume = MeasurementField()
    weight = MeasurementField()

    class Meta:
        model = Product
        fields = "__all__"


class AddProductToOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id",)


class ProductInventorySerializer(serializers.ModelSerializer):
    batches = serializers.SerializerMethodField()

    class Meta:
        model = ProductInventory
        fields = "__all__"

    def get_batches(self, obj):
        return [{"batch_number": batch.batch_number} for batch in obj.batches.all()]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class BatchSerializer(serializers.ModelSerializer):
    quantity_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = "__all__"

    def get_quantity_remaining(self, obj):
        return obj.quantity_remaining


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_parent(self, obj):
        if obj.parent:
            return obj.parent.name


class SalesZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesZone
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    contact_numbers = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = "__all__"

    def get_contact_numbers(self, obj):
        return [
            {"name": contact.name, "phone_number": str(contact.phone_number)}
            for contact in obj.contact_numbers.all()
        ]


class InventoryScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryScrap
        fields = "__all__"


class InventoryTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransfer
        fields = "__all__"


class ContactNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactNumber
        fields = "__all__"
