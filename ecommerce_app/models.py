from django.db import models
from django.db.models import Sum, F
from django.core.validators import MinValueValidator
from cuid import cuid
from charidfield import CharIDField
from ecommerce_app.utils import get_blue_price


class Product(models.Model):
    id = CharIDField(
        default=cuid,
        max_length=30,
        prefix='prod_',
        primary_key=True
    )
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        total = 0
        details = self.order_details
        if details.exists():
            total += details.aggregate(
                sum=Sum(F('product__price') * F('quantity'))
            )['sum']

        return total

    def get_total_usd(self):
        ars_price = self.get_total()
        current_blue = get_blue_price()
        return round(ars_price / current_blue, 2)

    def delete_details(self):
        """
        order_details.all().delete() doesn't call delete method,
        so we call it manually to keep stock updated
        """
        for detail in self.order_details.all():
            detail.delete()

    def delete(self, *args, **kwargs):
        self.delete_details()
        return super().delete(*args, **kwargs)


class OrderDetail(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_details'
    )
    quantity = models.IntegerField(MinValueValidator(0))
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_details'
    )

    def save(self, *args, **kwargs):
        """
        Update Product stock on detail create/update
        """

        product = self.product

        if self.pk is not None:
            original = OrderDetail.objects.get(pk=self.pk)
            product.stock += original.quantity - self.quantity
        else:
            product.stock -= self.quantity

        product.save()
        super(OrderDetail, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Update Product stock on detail delete
        """

        product = self.product
        product.stock += self.quantity
        product.save()
        return super().delete(*args, **kwargs)

    class Meta:
        unique_together = ('product', 'order')
