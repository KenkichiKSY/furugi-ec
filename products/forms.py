from django import forms

from .models import Category, Product


class ProductSearchForm(forms.Form):
    SORT_CHOICES = [
        ('-created_at', '新着順'),
        ('price', '価格が安い順'),
        ('-price', '価格が高い順'),
    ]

    q = forms.CharField(label='キーワード', required=False)
    category = forms.ModelChoiceField(
        label='カテゴリ', queryset=Category.objects.all(),
        required=False, empty_label='すべてのカテゴリ'
    )
    condition = forms.ChoiceField(
        label='状態', choices=[('', 'すべて')] + list(Product.CONDITION_CHOICES),
        required=False
    )
    min_price = forms.IntegerField(label='価格(下限)', required=False, min_value=0)
    max_price = forms.IntegerField(label='価格(上限)', required=False, min_value=0)
    sort = forms.ChoiceField(label='並び替え', choices=SORT_CHOICES, required=False)
