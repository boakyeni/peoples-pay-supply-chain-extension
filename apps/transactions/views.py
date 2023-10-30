from django.shortcuts import render
import requests

# Create your views here.

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Transaction
from .serializers import TransactionSerializer


def get_peoples_pay_token(request):
    """
    Helper to get peoples pay token 
    """
    if 'operation' not in request:
        request['operation'] = "DEBIT"

    headers = {"Authorization": "Bearer MYREALLYLONGTOKENIGOT"}

    response = requests.post('https://peoplespay.com.gh/peoplepay/hub/token/get', data=request)

    response = response.json()

    if not response['success']:
        return None
    return response['data']


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

            transaction_instance = Transaction.objects.get(transactions_id=serializer.data['transactions_id'])
            # Post Transaction to Peoples Pay
            transaction_response = requests.post('')
            transaction_response = transaction_response.json()

            # Check status of transaction with transaction id from previous post
            status_response = requests.post('https://peoplespay.com.gh/peoplepay/hub/transactions/get/"KEY"')
            status_response = status_response.json()

            # Update the transaction instance with relevant data


            #Save

            


            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
