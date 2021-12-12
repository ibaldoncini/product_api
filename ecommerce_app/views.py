from django.db.utils import IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ecommerce_app.models import Product, Order
from ecommerce_app.serializers import (
    ProductSerializer,
    OrderSerializer
)


class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['patch'])
    def change_stock(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer_class()

        if 'amount' in request.data:
            product.stock += request.data['amount']
            product.save()
            response = Response(serializer(product).data, status=status.HTTP_200_OK)
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
    http_method_names = ['get', 'post', 'put', 'delete']

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
        except IntegrityError:
            response = Response(
                {'status': 'Bad request, detail for that product already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return response
