from rest_framework.routers import DefaultRouter
from ecommerce_app.views import (
    ProductViewset,
    OrderViewset,
    OrderDetailViewset
)


router = DefaultRouter()

router.register('products', ProductViewset, basename='products')
router.register('orders', OrderViewset, basename='orders')
router.register('order_details', OrderDetailViewset, basename='order_details')

urlpatterns = router.urls
