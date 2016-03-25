from django.db import models
from django.utils import timezone
from core.json_serializer import JSONSerializer
from django.utils.datetime_safe import strftime
from django.utils.timezone import localtime
from elec_site import settings

THUMB_SIZE = 200
IN_STOCK = 1
OUT_OF_STOCK = 0

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, blank=False, max_length=100, default='', unique=False,
                            verbose_name='Наименование')
    desc = models.TextField(null=False, blank=False, max_length=500, default='', unique=False,
                            verbose_name='Описание')
    cost = models.PositiveIntegerField(null=False, blank=False, verbose_name='Цена')
    left_in_stock = models.IntegerField(null=False, blank=False, unique=False,
                                        default=1, verbose_name='Осталось на складе')

    @property
    def in_stock(self):
        return self.left_in_stock > 0

    def __str__(self):
        return self.name

    @property
    def thumb_urls(self):
        qs = ProductImage.objects.filter(product=self.id)
        urls = []
        for i in qs:
            urls.append(i.thumb.url)

        return urls

    @property
    def thumbs(self):
        qs = ProductImage.objects.filter(product=self.id)
        thumbs = []
        for i in qs:
            thumbs.append({'id': i.id,'url': i.thumb.url, 'large': i.image.url})

        return thumbs

    @property
    def images(self):
        qs = ProductImage.objects.filter(product=self.id)
        urls = []
        for i in qs:
            urls.append(i.image.url)

        return urls

    def to_json(self):
        if not self.id:
            return {}

        return {
            'id':self.id,
            'name': self.name,
            'desc': self.desc,
            'cost': self.cost,
        }

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

    def get_large_image(self):
        return self.image.url

    def __str__(self):
        return self.thumb.url

    class Meta:
        db_table = 'product_image'
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.CharField(null=False, blank=False, max_length=100, default='', unique=False, verbose_name='Номер заказа')
    # user = models.ForeignKey(MyUser)
    # status = models.IntegerField(null=True, blank=True, default=0)
    total = models.PositiveIntegerField(null=False, blank=False, unique=False, default=0)
    user_phone = models.CharField(null=False, blank=False, max_length=100, default='', unique=False,
                                  verbose_name='Телефон')
    user_email = models.CharField(null=False, blank=False, max_length=100, default='', unique=False,
                                  verbose_name='Email')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s %s %s' % (self.number, self.user_email, self.user_phone)

    def to_json(self):
        if not self.id:
            return {}

        order_items = OrderItem.objects.filter(order_id=self.id)
        j = { 'items': [] }

        for oi in order_items:
            j['items'].append(oi.to_json())

        j['phone'] = self.user_phone
        j['number'] = self.number
        j['total'] = self.total
        j['email'] = self.user_email
        j['date'] = localtime(timezone.now()).strftime('%d.%m.%Y %H:%m')

        return j

class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', to_field='id', db_column='product_id',
                                unique=False, blank=False, null=False)
    order = models.ForeignKey('Order', to_field='id', db_column='order_id',
                                unique=False, blank=False, null=False)
    count = models.PositiveIntegerField(null=False, blank=False, unique=False, default=1)

    @property
    def price(self):
        return self.product.cost * self.count


    def to_json(self):
        return {
            'product': self.product.to_json(),
            'count': self.count,
            'price': self.price
        }

