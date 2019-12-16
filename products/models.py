from django.db import models

# Create your models here.
from django.db import models


class Product(models.Model):
    STORE_CHOICES = ((0, 'Amazon'), (1, 'eBay'), (2, 'buyitdirect'))

    keyword = models.CharField(max_length=128)
    name = models.CharField(max_length=256)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    store = models.IntegerField(choices=STORE_CHOICES)
    url = models.TextField()

    class Meta:
        ordering = ('price',)
