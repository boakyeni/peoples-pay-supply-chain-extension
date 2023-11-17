from django.urls import path, include
from . import views
from rest_framework import routers


urlpatterns = [
    path("category/", views.SearchCategories.as_view(), name="category"),
    path("create-category/", views.CreateCategory.as_view(), name="create_category"),
    path("products/", views.SearchProducts.as_view(), name="search-products"),
    path(
        "create-product/",
        views.create_product,
        name="create_product",
    ),
    path("create-batch/", views.create_batch, name="create_batch"),
    path("edit-product/", views.update_product, name="edit-product"),
]
