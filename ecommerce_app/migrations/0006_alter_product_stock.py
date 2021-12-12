# Generated by Django 3.2.9 on 2021-12-05 17:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_app', '0005_auto_20211202_0333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]