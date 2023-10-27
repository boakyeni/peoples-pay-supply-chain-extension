from django.contrib import admin
from .models import Transaction


# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["transactions_id", "merchant_from", "merchant_to"]


admin.site.register(Transaction, TransactionAdmin)
