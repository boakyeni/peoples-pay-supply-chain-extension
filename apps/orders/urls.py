from django.urls import path
from . import views

urlpatterns = [
    path("create-order/", views.create_order, name="create_order"),
    path("", views.SearchOrder.as_view(), name="search_order"),
    path("delete-order/", views.delete_order, name="delete_order"),
    path("update-order/", views.update_order, name="update_order"),

]