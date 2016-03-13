from django.forms import ModelForm
from core import models

class ProductForm(ModelForm):
    class Meta:
        model = models.Product
        fields = ['name', 'cost', ]