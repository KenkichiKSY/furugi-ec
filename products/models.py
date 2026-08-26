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