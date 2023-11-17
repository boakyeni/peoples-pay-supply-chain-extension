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
        data = request.data
        data['merchant_from'] = request.auth['merchant_name']
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            transaction_instance = serializer.save()
            # Get Peoples Pay token
            
            
            # Post Transaction to Peoples Pay
            transaction_response = requests.post('')
            transaction_response = transaction_response.json()

            key = transaction_response['transactionId']
            

            # Check status of transaction with transaction id from previous post
            status_response = requests.post(f'https://peoplespay.com.gh/peoplepay/hub/transactions/get/{key}')
            status_response = status_response.json()

            status = status_response['status']
            

            # Update the transaction instance with relevant data
            transaction_instance.key = key
            transaction_instance.status = status

            #Save

            transaction_instance.save()


            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
