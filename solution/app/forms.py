from django import forms
from .models import FridgeItem

class FridgeItemForm(forms.ModelForm):
    class Meta:
        model = FridgeItem
        fields = ['name', 'category', 'quantity', 'expiry_date', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название продукта'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Количество (по желанию)'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Заметки (по желанию)',
                'rows': 3
            }),
        }
        labels = {
            'name': 'Название продукта',
            'category': 'Категория',
            'quantity': 'Количество',
            'expiry_date': 'Срок годности',
            'notes': 'Заметки',
        }