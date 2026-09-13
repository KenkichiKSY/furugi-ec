import pytest
from django.contrib.auth import get_user_model

from products.models import Category, Product


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username='testuser', password='TestPass123!')


@pytest.fixture
def category(db):
    return Category.objects.create(name='トップス')


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        category=category, name='テストTシャツ', price=2000,
        condition='new', stock=5, is_active=True,
    )
