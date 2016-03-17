from django.db import models
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from elec_site import settings

THUMB_SIZE = 200
IN_STOCK = 1
OUT_OF_STOCK = 0

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, blank=False, max_length=100, default='', unique=False, verbose_name='Наименование')
    cost = models.PositiveIntegerField(null=False, blank=False, verbose_name='Цена')
    in_stock = models.IntegerField(null=False, blank=False, unique=False, default=IN_STOCK)

    def __str__(self):
        return self.name

    @property
    def thumbs(self):
        qs = ProductImage.objects.filter(product=self.id)
        urls = []
        for i in qs:
            urls.append(i.thumb.url)

        return urls

    @property
    def images(self):
        qs = ProductImage.objects.filter(product=self.id)
        urls = []
        for i in qs:
            urls.append(i.image.url)

        return urls

    class Meta:
        db_table = 'products'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', to_field='id', db_column='product_id',
                                unique=False, blank=False, null=False)
    date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='uploads/')
    thumb = models.ImageField(blank=True, null=True, default='')

    def __str__(self):
        return self.thumb.url

    class Meta:
        db_table = 'product_image'
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    # user = models.ForeignKey(MyUser)
    # status = models.IntegerField(null=True, blank=True, default=0)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', to_field='id', db_column='product_id',
                                unique=False, blank=False, null=False)
    order = models.ForeignKey('Order', to_field='id', db_column='order_id',
                                unique=False, blank=False, null=False)