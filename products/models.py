from django.conf import settings
from django.db import models
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField("カテゴリ名", max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "カテゴリ"
        verbose_name_plural = "カテゴリ"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Product(models.Model):
    CONDITION_CHOICES = [
        ("new", "新品"),
        ("s", "古着 - Sランク(未使用に近い)"),
        ("a", "古着 - Aランク(良好)"),
        ("b", "古着 - Bランク(使用感あり)"),
        ("c", "古着 - Cランク(ダメージあり)"),
    ]

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        related_name="products", verbose_name="カテゴリ"
    )
    name = models.CharField("商品名", max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField("商品説明", blank=True)
    price = models.PositiveIntegerField("価格(円)")
    condition = models.CharField(
        "状態", max_length=10, choices=CONDITION_CHOICES, default="new"
    )
    is_secondhand = models.BooleanField("古着フラグ", default=False)
    stock = models.PositiveIntegerField("在庫数", default=1)
    image = models.ImageField(
        "商品画像", upload_to="products/", blank=True, null=True
    )
    is_active = models.BooleanField("公開", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / len(reviews)


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'お気に入り'
        verbose_name_plural = 'お気に入り'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_favorite')
        ]

    def __str__(self):
        return f"{self.user} - {self.product}"


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField('評価', choices=RATING_CHOICES)
    comment = models.TextField('コメント', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'レビュー'
        verbose_name_plural = 'レビュー'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['product', 'user'], name='unique_review')
        ]

    def __str__(self):
        return f"{self.product} - {self.user}({self.rating})"
