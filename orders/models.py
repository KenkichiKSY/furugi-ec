from django.conf import settings
from django.db import models

from products.models import Product


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}のカート"

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product')
        ]

    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '注文受付'),
        ('paid', '支払い済み'),
        ('shipped', '発送済み'),
        ('cancelled', 'キャンセル'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders'
    )
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.PositiveIntegerField('合計金額')

    shipping_recipient_name = models.CharField('お届け先氏名', max_length=100, default='')
    shipping_postal_code = models.CharField('郵便番号', max_length=8, default='')
    shipping_prefecture = models.CharField('都道府県', max_length=20, default='')
    shipping_city = models.CharField('市区町村・番地', max_length=200, default='')
    shipping_building = models.CharField('建物名など', max_length=200, blank=True, default='')
    shipping_phone_number = models.CharField('電話番号', max_length=20, default='')
    shipping_fee = models.PositiveIntegerField('送料', default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"注文#{self.pk}({self.user})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField('商品名', max_length=200)
    price = models.PositiveIntegerField('購入時単価')
    quantity = models.PositiveIntegerField('数量')

    def subtotal(self):
        return self.price * self.quantity
