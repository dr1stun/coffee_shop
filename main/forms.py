from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'name_en', 'description', 'price', 'category', 'image', 'is_available']
        labels = {
            'name': 'Название товара',
            'name_en': 'Название товара (англ.)',
            'description': 'Описание',
            'price': 'Цена',
            'category': 'Категория',
            'image': 'Изображение товара',
            'is_available': 'Доступен',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }