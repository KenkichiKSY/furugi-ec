import pytest
from django.urls import reverse

from accounts.models import Address
from orders.models import Cart, Order
from orders.shipping import calculate_shipping_fee


def test_calculate_shipping_fee_below_threshold():
    assert calculate_shipping_fee(1000) == 500


def test_calculate_shipping_fee_free_above_threshold():
    assert calculate_shipping_fee(5000) == 0


@pytest.mark.django_db
def test_add_to_cart_creates_cart_item(client, user, product):
    client.force_login(user)
    client.post(reverse('orders:add_to_cart', args=[product.slug]))

    cart = Cart.objects.get(user=user)
    assert cart.items.count() == 1
    assert cart.items.first().product == product


@pytest.mark.django_db
def test_add_to_cart_twice_increments_quantity(client, user, product):
    client.force_login(user)
    url = reverse('orders:add_to_cart', args=[product.slug])

    client.post(url)
    client.post(url)

    cart = Cart.objects.get(user=user)
    assert cart.items.first().quantity == 2


@pytest.mark.django_db
def test_checkout_without_address_shows_error(client, user, product):
    client.force_login(user)
    client.post(reverse('orders:add_to_cart', args=[product.slug]))

    response = client.post(reverse('orders:checkout'), follow=True)

    messages = list(response.context['messages'])
    assert any('配送先' in str(m) for m in messages)
    assert not Order.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_checkout_with_insufficient_stock_blocks_order(client, user, product):
    product.stock = 0
    product.save()
    client.force_login(user)
    client.post(reverse('orders:add_to_cart', args=[product.slug]))

    address = Address.objects.create(
        user=user, recipient_name='テスト太郎', postal_code='1000001',
        prefecture='東京都', city='千代田区', phone_number='0000000000',
    )

    client.post(reverse('orders:checkout'), {'address_id': address.id}, follow=True)

    assert not Order.objects.filter(user=user).exists()
