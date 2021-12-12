from rest_framework.routers import DefaultRouter
from ecommerce_app.views import (
    ProductViewset,
    OrderViewset
)

router = DefaultRouter()
router.register('products', ProductViewset, basename='products')
router.register('orders', OrderViewset, basename='orders')

urlpatterns = router.urls
