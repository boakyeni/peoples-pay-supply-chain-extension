from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from django.db import transaction
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, serializers
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from .models import Product, Category, Brand, ProductInventory
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ProductInventorySerializer,
    BatchSerializer,
    BrandSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, pk):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


"""CATEGORY VIEWS"""


class SearchCategories(generics.ListAPIView):
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset


class CreateCategory(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        if "parent" in data:
            try:
                parent_instance = Category.objects.get(name=data["parent"])

            except Category.DoesNotExist:
                custom_response_data = {
                    # customize your response format here
                    "errors": "Category not found",
                    "status": "failed",
                    "message": "Category of the name requested as parent category does not exist",
                }
                return Response(
                    custom_response_data, status=status.HTTP_400_BAD_REQUEST
                )

        serializer = CategorySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        category.parent = parent_instance
        category.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


"""PRODUCT VIEWS"""


class SearchProducts(generics.ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "category__name"]

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset


@api_view(["POST"])
@transaction.atomic
def create_product(request):
    data = request.data

    categories = data["categories"]
    # Categories must be pre made in this case
    category_instances = [
        Category.objects.get(name=category).id for category in categories
    ]
    data["categories"] = category_instances

    product_serializer = ProductSerializer(data=data)
    product_serializer.is_valid(raise_exception=True)
    product_instance = product_serializer.save()

    data["product"] = product_instance.product_id

    brand = data["brand"]
    brand_instance = None
    try:
        brand_instance = Brand.objects.get(name=brand)
    except Brand.DoesNotExist:
        brand_data = {"name": brand}
        brand_serializer = BrandSerializer(data=brand_data)
        brand_serializer.is_valid(raise_exception=True)
        brand_instance = brand_serializer.save()

    data["brand"] = brand_instance.id

    inventory_serializer = ProductInventorySerializer(data=data)
    inventory_serializer.is_valid(raise_exception=True)
    inventory_instance = inventory_serializer.save()

    return Response(inventory_serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@transaction.atomic
def update_product(request):
    """Categories and Brands must already exist in the system"""
    data = request.data
    product_instance = Product.objects.get(product_id=data["product_id"])
    inventory_instance = ProductInventory.objects.get(product=data["product_id"])
    if "add_categories" in data:
        categories = data["add_categories"]
        category_instances = [
            Category.objects.get(name=category).id for category in categories
        ]
        for category in category_instances:
            product_instance.categories.add(category)
        product_instance.save()
        data.pop("add_categories")
    if "brand":
        try:
            brand_instance = Brand.objects.get(name=data["brand"])
        except Brand.DoesNotExist:
            return Response(
                {"message": "Please ensure brand name is in system"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data["brand"] = brand_instance.id

    product_serializer = ProductSerializer(instance=product_instance, data=data)
    product_serializer.is_valid(raise_exception=True)
    product_serializer.save()

    inventory_serializer = ProductInventorySerializer(
        instance=inventory_instance, data=data
    )
    inventory_serializer.is_valid(raise_exception=True)
    inventory_serializer.save()

    return Response(inventory_serializer.data, status=status.HTTP_200_OK)


"""BATCH VIEWS"""


@api_view(["POST"])
@transaction.atomic
def create_batch(request):
    data = request.data
    product_instance = None
    try:
        product_instance = ProductInventory.objects.get(product__name=data["product"])
    except ProductInventory.DoesNotExist:
        raise serializers.ValidationError("Product does not exist")
    data["product"] = product_instance.id
    serializer = BatchSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)
