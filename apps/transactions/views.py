from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Transaction
from .serializers import TransactionSerializer

@api_view(["GET"])
def get_transaction(request, pk):
    if request.method == "GET":
        if pk is not None:
            try:
                Transaction = Transaction.objects.get(pk=pk)
                serializer = TransactionSerializer(Transaction)
                return Response(serializer.data)
            except Transaction.Does.NotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        else:
            Transaction = Transaction.objects.all()
            serializer = TransactionSerializer(Transaction, many=True)
            return Response(serializer.data)


@api_view(["POST"])
def create_transaction(request):
    if request.method == "POST":
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
