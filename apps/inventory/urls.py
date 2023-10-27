from django.urls import path
from .viewsets import ProductViewSet

router = routers.DefaultRouter()
router.register("", ProductViewSet, basename="products")

urlpatterns = [
    path("", include(router.urls)),
]
