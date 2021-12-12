from rest_framework import serializers
from rest_framework.serializers import ValidationError
from ecommerce_app.models import Product, Order, OrderDetail
from drf_writable_nested.serializers import WritableNestedModelSerializer


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
        value_exception = ValidationError(
            {'quantity': 'Negative/Zero quantity not allowed'}
        )

        quantity = attrs['quantity']
        if quantity < 1:
            raise value_exception

        if self.instance:
            current_quantity = self.instance.quantity
            product = self.instance.product
            if quantity > product.stock + current_quantity:
                raise stock_exception
        else:
            stock = attrs['product'].stock
            if quantity > stock:
                raise stock_exception

        return validated

    class Meta:
        model = OrderDetail
        fields = '__all__'


class NestedOrderDetailSerializer(OrderDetailSerializer):
    class Meta:
        model = OrderDetail
        exclude = ['order']


class OrderSerializer(WritableNestedModelSerializer):
    order_details = NestedOrderDetailSerializer(many=True)
    total = serializers.FloatField(source='get_total', read_only=True)
    total_usd = serializers.FloatField(source='get_total_usd', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
