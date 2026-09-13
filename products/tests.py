import pytest
from django.urls import reverse

from .models import Category, Favorite, Product, Review


@pytest.mark.django_db
def test_product_slug_is_generated_from_name():
    category = Category.objects.create(name='トップス')
    product = Product.objects.create(
        category=category, name='ヴィンテージシャツ', price=3000,
    )
    assert product.slug == 'ヴィンテージシャツ'


@pytest.mark.django_db
def test_product_detail_url_resolves_with_japanese_slug(client, product):
    """日本語スラッグがURLで解決できない不具合の再発防止テスト。"""
    url = reverse('products:detail', args=[product.slug])
    response = client.get(url)
    assert response.status_code == 200
    assert product.name in response.content.decode('utf-8')


@pytest.mark.django_db
def test_product_list_hides_inactive_products(client, category):
    Product.objects.create(category=category, name='公開商品', price=1000, is_active=True)
    Product.objects.create(category=category, name='非公開商品', price=1000, is_active=False)

    response = client.get(reverse('products:list'))
    content = response.content.decode('utf-8')

    assert '公開商品' in content
    assert '非公開商品' not in content


@pytest.mark.django_db
def test_search_by_keyword_filters_results(client, category):
    Product.objects.create(category=category, name='デニムパンツ', price=4000, is_active=True)
    Product.objects.create(category=category, name='コットンシャツ', price=2000, is_active=True)

    response = client.get(reverse('products:list'), {'q': 'デニム'})
    content = response.content.decode('utf-8')

    assert 'デニムパンツ' in content
    assert 'コットンシャツ' not in content


@pytest.mark.django_db
def test_toggle_favorite_requires_login(client, product):
    url = reverse('products:toggle_favorite', args=[product.slug])
    response = client.post(url)
    assert response.status_code == 302
    assert '/accounts/login/' in response.url


@pytest.mark.django_db
def test_toggle_favorite_adds_and_removes(client, user, product):
    client.force_login(user)
    url = reverse('products:toggle_favorite', args=[product.slug])

    client.post(url)
    assert Favorite.objects.filter(user=user, product=product).exists()

    client.post(url)
    assert not Favorite.objects.filter(user=user, product=product).exists()


@pytest.mark.django_db
def test_review_requires_purchase(client, user, product):
    client.force_login(user)
    url = reverse('products:add_review', args=[product.slug])

    client.post(url, {'rating': 5, 'comment': 'とても良い'}, follow=True)

    assert not Review.objects.filter(product=product, user=user).exists()
