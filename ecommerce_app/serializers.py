from rest_framework import serializers
from rest_framework.serializers import ValidationError
from ecommerce_app.models import Product, Order, OrderDetail
from drf_writable_nested.serializers import WritableNestedModelSerializer
from django.db.models import Sum


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'stock': {'min_value': 0}
        }


class OrderDetailSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        validated = super().validate(attrs)
        stock_exception = ValidationError({'quantity': 'Not enough stock'})
        negative_exception = ValidationError({'quantity': 'Negative/Zero quantity not allowed'})

        if attrs['quantity'] < 1:
            raise negative_exception

        if self.instance:
            current_quantity = self.instance.quantity
            product = self.instance.product
            if attrs['quantity'] > product.stock + current_quantity:
                raise stock_exception
        else:
            order = self.context['view'].get_object()
            product = attrs['product']
            stock = product.stock
            if order:
                details = order.order_details.filter(product=product)
                if details.exists():
                    stock += details.aggregate(sum=Sum('quantity'))['sum']

            if attrs['quantity'] > stock:
                raise stock_exception

        return validated

    class Meta:
        model = OrderDetail
        fields = ['product', 'quantity', 'id']


class OrderSerializer(WritableNestedModelSerializer):
    order_details = OrderDetailSerializer(many=True)
    total = serializers.FloatField(source='get_total', read_only=True)
    total_usd = serializers.FloatField(source='get_total_usd', read_only=True)

    def update(self, instance, validated_data):
        remaining = [detail['product'] for detail in validated_data['order_details']]
        deleted = instance.order_details.exclude(product__in=remaining)
        for detail in deleted:
            detail.delete()

        return super().update(instance, validated_data)

    class Meta:
        model = Order
        fields = '__all__'
