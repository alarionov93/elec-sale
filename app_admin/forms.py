from django.forms import ModelForm
from core import models

class ProductForm(ModelForm):

    # def __init__(self, *args, **kwargs):
    #     super(ProductForm, self).__init__(*args, **kwargs)
    #     product_id = kwargs.pop('pk', 0)
    #     if product_id > 0:
    #         images = models.Product.get(id=product_id).get_images()
    #         img_urls = []
    #         for i in images:
    #             img_urls.append(i.thumbnail.url)
    #         self.fields['images'].initial = img_urls

    class Meta:
        model = models.Product
        fields = ['name', 'cost', ]

#
# class ProductImageForm(ModelForm):
#     class Meta:
#         model = models.ProductImage
#         fields = ['product', 'image' ]


