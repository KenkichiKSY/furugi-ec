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
