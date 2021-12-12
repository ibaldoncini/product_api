import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ecommerce_app.models import Product, Order, OrderDetail
from ecommerce_app.serializers import (
    ProductSerializer,
    OrderSerializer,
    OrderDetailSerializer
)


class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['patch'])
    def change_stock(self, request, pk=None):
        """
        Add / Substract to a product stock instead of replacing it entirely,
        like patch or put to /api/products/{pk}/ would do
        """
        product = self.get_object()
        serializer = self.get_serializer_class()

        if 'amount' in request.data:
            product.stock += request.data['amount']
            product.save()
            response = Response(
                serializer(product).data,
                status=status.HTTP_200_OK
            )
        else:
            response = Response(
                {'status': 'Bad request, "amount" field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return response


class OrderViewset(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']


class OrderDetailViewset(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        """
        Ensure no detail of that Product for the specified order exists,
        otherwise, return 400
        """
        payload = json.loads(request.data)
        product_id = payload['product']
        order_id = payload['order']

        product_detail = self.get_queryset().filter(
            product__id=product_id,
            order__id=order_id
        )
        if product_detail.exists():
            response = Response(
                {'status': 'Detail for product already exists in the order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            response = super().create(request, *args, **kwargs)

        return response
