from django.contrib import admin
from .models import Order, OrderDetail


class OrderDetailInlineAdmin(admin.TabularInline):
    model = OrderDetail

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderDetailInlineAdmin]

admin.site.register(Order, OrderAdmin)