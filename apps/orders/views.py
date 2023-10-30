from django.shortcuts import render
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderDetail
from .serializers import OrderSerializer
from apps.inventory.models import Product
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
# Create your views here.


class SearchOrder(generics.ListAPIView):
    # authentication_classes = [JWTStatelessUserAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['placed_by']

    def get_queryset(self):
        # merchant_id = self.request.auth.get("merchant_id")
        queryset = Order.objects.all()
        return queryset
        

@api_view(["POST"])
# @authentication_classes([JWTStatelessUserAuthentication])
# @permission_classes([IsAuthenticated])
def create_order(request):
    data = request.data
    user_identifier = request.auth['merchant_id']
    serializer = OrderSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PATCH"])
# @authentication_classes([JWTStatelessUserAuthentication])
# @permission_classes([IsAuthenticated])
def update_order(request):
    """
    Can update the entire order object,
    Can add additional products to an existing order,
    Or change quantity of product in existing order
    """
    data = request.data
    if 'add_products' in data:
        products = data['add_products']
    try:
        order_instance = Order.objects.get(id=data['order_id'])
    except Order.DoesNotExist:
        return Response({"message":"No order with that ID"})
    

    current_order_details = order_instance.details.all()
    product_set = set()
    # Create set to make sure products arent added twice
    for item in current_order_details:
        product_set.add(item.item_code)

    for product in products:
        product_instance = Product.objects.get(product_id=product['product_id'])
        if product_instance not in product_set:
            order_detail_instance = OrderDetail.objects.create(order=order_instance, item_code=product_instance, quantity=product['quantity'])
        
            # Tax should mostly be set depending on Product Category
            # For now we use the default tax
            total = float(product['quantity'] * product_instance.price)
            tax = total * float(order_detail_instance.tax)
            
            order_detail_instance.subtotal = total + tax
            order_detail_instance.save()
        else:
            order_detail_instance = OrderDetail.objects.get(order=order_instance, item_code=product_instance)
            order_detail_instance.quantity = product['quantity']
            total = float(product['quantity'] * product_instance.price)
            tax = total * float(order_detail_instance.tax)
            
            order_detail_instance.subtotal = total + tax
            order_detail_instance.save()
        

    if request.method == "PATCH":
        data = request.data
        serializer = OrderSerializer(instance=order_instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

@api_view(["DELETE"])
# @authentication_classes([JWTStatelessUserAuthentication])
# @permission_classes([IsAuthenticated])
def delete_order(request):
    data = request.data
    try:
        order_instance = Order.objects.get(id=data['order_id'])
    except Order.DoesNotExist:
        return Response({"message": "Order Already Deleted"}, status=status.HTTP_204_NO_CONTENT)
    
    if request.method == "DELETE":
        delete_operation = order_instance.delete()
        data = {}
        if delete_operation:
            data["message"] = "Deletion was successful"
        else:
            data["message"] = "Deletion has failed"
        return Response(data=data)




