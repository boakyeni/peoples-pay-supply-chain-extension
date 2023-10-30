import uuid
from django.db import models


# Create your models here.
class Transaction(models.Model):
    transactions_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    peoples_pay_transaction_id = models.CharField(max_length=100)
    merchant_from = models.CharField(max_length=100)
    merchant_to = models.CharField(max_length=100)
    key = models.CharField(max_length=512)
    reference = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    method = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    date = models.DateTimeField()

    def __str__(self):
        return str(self.transactions_id)