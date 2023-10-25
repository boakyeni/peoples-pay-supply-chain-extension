from django.urls import path
from .views import create_transaction, get_transaction

urlpatterns = [
    path("", views.get_transaction, name="get_transaction"),
    path("", views.create_transaction, name="create_transaction"),
]
