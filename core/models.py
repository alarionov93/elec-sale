from django.db import models

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, blank=False, max_length=100, default='', unique=False, verbose_name='Наименование')
    cost = models.PositiveIntegerField(null=False, blank=False, verbose_name='Цена')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

class ProductImage():
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', to_field='id', db_column='product_id',
                                unique=False, blank=False, null=False)
    image = models.ImageField(upload_to='uploads/')

    class Meta:
        db_table = 'product_image'
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

