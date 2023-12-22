from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from django.db import transaction
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, serializers
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from .models import (
    Product,
    Category,
    Brand,
    ProductInventory,
    Batch,
    Customer,
    SalesZone,
    ContactNumber,
)
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ProductInventorySerializer,
    BatchSerializer,
    BrandSerializer,
    InventoryScrapSerializer,
    InventoryTransferSerializer,
    StoreSerializer,
    CustomerSerializer,
    ContactNumberSerializer,
    SalesZoneSerializer,
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
                serializer = CategorySerializer(data=data)
                serializer.is_valid(raise_exception=True)
                category = serializer.save()
                category.parent = parent_instance
                category.save()

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
        else:
            serializer = CategorySerializer(data=data)
            serializer.is_valid(raise_exception=True)
            category = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


"""PRODUCT VIEWS"""


class SearchProducts(generics.ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "categories__name"]

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

    data["product"] = product_instance.id

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
    product_instance = Product.objects.get(id=data["product_id"])
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

    product_serializer = ProductSerializer(
        instance=product_instance, partial=True, data=data
    )
    product_serializer.is_valid(raise_exception=True)
    product_serializer.save()

    inventory_serializer = ProductInventorySerializer(
        instance=inventory_instance, partial=True, data=data
    )
    inventory_serializer.is_valid(raise_exception=True)
    inventory_serializer.save()

    return Response(inventory_serializer.data, status=status.HTTP_200_OK)


"""BATCH VIEWS"""


class SearchBatch(generics.ListAPIView):
    serializer_class = BatchSerializer
    filter_backends = [SearchFilter]
    search_fields = ["batch_number", "product__product__name"]

    def get_queryset(self):
        deleted = self.request.query_params.get("deleted")
        if deleted is None:
            return Batch.objects.filter(deleted=False)
        return Batch.objects.all()


@api_view(["POST"])
@transaction.atomic
def create_batch(request):
    data = request.data
    product_inventory_instance = None
    try:
        product_inventory_instance = ProductInventory.objects.get(
            product__name=data["product"]
        )
    except ProductInventory.DoesNotExist:
        return Response(
            {
                "error": "Product does not Exist",
                "status": "failed",
                "message": "Product Does Not Exist",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    data["product"] = product_inventory_instance.id
    serializer = BatchSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@transaction.atomic
def edit_batch(request):
    data = request.data
    batch_instance = Batch.objects.get(batch_number=data["batch_number"])
    serializer = BatchSerializer(instance=batch_instance, partial=True, data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@transaction.atomic
def delete_batch(request):
    """IDK IF THIS SHOULD BE ALLOWED"""
    data = request.data
    batch_instance = Batch.objects.get(batch_number=data["batch_number"])
    if request.method == "DELETE":
        delete_operation = batch_instance.delete()
        data = {}
        if delete_operation:
            data["succes"] = "Deletion was successful"
        else:
            data["failure"] = "Deletion has failed"
        return Response(data=data)


"""REQUESTS"""


@api_view(["POST"])
@transaction.atomic
def create_request(request):
    """Approval is made in Pending State upon request"""
    data = request.data
    inventory_scrap_serializer = None
    inventory_transfer_serializer = None
    if data["type"].lower() == "inventory scrap":
        product_instance = Product.objects.get(name=data["product"])
        data["product"] = product_instance.id
        inventory_scrap_serializer = InventoryScrapSerializer(data=data)
        inventory_scrap_serializer.is_valid(raise_exception=True)
        inventory_scrap_serializer.save()
    if data["type"].lower() == "inventory transfer":
        inventory_transfer_serializer = InventoryTransferSerializer(data=data)
        inventory_transfer_serializer.is_valid(raise_exception=True)
        inventory_transfer_serializer.save()
    serializer = inventory_scrap_serializer or inventory_transfer_serializer
    return Response(serializer.data, status=status.HTTP_201_CREATED)


"""APPROVALS"""


@api_view(["POST"])
def update_approval(request):
    data = request.data


@api_view(["POST"])
def create_store(request):
    data = request.data
    serializer = StoreSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


"""CUSTOMER VIEWS"""


class SearchCustomer(generics.ListAPIView):
    serializer_class = CustomerSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "id"]

    def get_queryset(self):
        deleted = self.request.query_params.get("deleted")
        if deleted is None:
            return Customer.objects.filter(deleted=False)
        return Customer.objects.all()


@api_view(["POST"])
@transaction.atomic
def create_customer(request):
    data = request.data

    zone_name = data.pop("zone", None)
    zone_object = SalesZone.objects.filter(name=zone_name)
    zone = zone_object[0] if len(zone_object) > 0 else None
    data["zone"] = zone.id if zone else None

    customer_serializer = CustomerSerializer(data=data)
    customer_serializer.is_valid(raise_exception=True)
    customer_instance = customer_serializer.save()

    if "contact_numbers" in data:
        for contact in data["contact_numbers"]:
            contact["customer"] = customer_instance.id
            print(contact)
            contact_serializer = ContactNumberSerializer(data=contact)
            contact_serializer.is_valid(raise_exception=True)
            contact_serializer.save()

    return Response(customer_serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@transaction.atomic
def update_customer(request):
    data = request.data

    try:
        customer_instance = Customer.objects.get(id=data["id"])
    except Customer.DoesNotExist:
        return Response(
            {
                "error": "No customer with that id",
                "status": "failed",
                "message": "No customer with that id",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    # handle updating of Foreign Keys
    zone_name = data.pop("zone", None)
    zone_object = SalesZone.objects.filter(name=zone_name)
    zone = zone_object[0] if len(zone_object) > 0 else None
    data["zone"] = zone.id if zone else None

    contact_data = data.pop("contact_numbers", None)
    for contact in contact_data:
        contact_instance_set = ContactNumber.objects.filter(
            name=contact["name"], customer=customer_instance.id
        )
        if len(contact_instance_set) > 0:
            contact_instance_set[0].phone_number = contact["phone_number"]
            contact_instance_set[0].save()
        else:
            contact["customer"] = customer_instance.id
            contact_serializer = ContactNumberSerializer(data=contact)
            contact_serializer.is_valid(raise_exception=True)
            contact_serializer.save()

    serializer = CustomerSerializer(instance=customer_instance, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)


"""ZONE VIEWS"""


class SearchZones(generics.ListAPIView):
    serializer_class = SalesZoneSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "town", "district", "region"]

    def get_queryset(self):
        return SalesZone.objects.all()


@api_view(["POST"])
@transaction.atomic
def create_zone(request):
    data = request.data
    serializer = SalesZoneSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)
