from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    将来的な拡張(電話番号、配送先デフォルト住所など)に備えて
    Djangoの標準Userを継承したカスタムユーザーモデル。
    """
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.username

class Address(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='addresses'
    )
    recipient_name = models.CharField('お届け先氏名', max_length=100)
    postal_code = models.CharField('郵便番号', max_length=8)
    prefecture = models.CharField('都道府県', max_length=20)
    city = models.CharField('市区町村・番地', max_length=200)
    building = models.CharField('建物名など', max_length=200, blank=True)
    phone_number = models.CharField('電話番号', max_length=20)
    is_default = models.BooleanField('デフォルトの配送先', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '配送先住所'
        verbose_name_plural = '配送先住所'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.recipient_name}({self.postal_code})"
