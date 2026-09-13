import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Address

User = get_user_model()


@pytest.mark.django_db
def test_signup_creates_user_and_logs_in(client):
    client.post(reverse('accounts:signup'), {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'StrongPass123!',
        'password2': 'StrongPass123!',
    })

    assert User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_login_with_wrong_password_fails(client, user):
    response = client.post(reverse('login'), {
        'username': user.username,
        'password': 'wrong-password',
    })

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_address_list_requires_login(client):
    response = client.get(reverse('accounts:address_list'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_address_list_only_shows_own_addresses(client, django_user_model):
    user1 = django_user_model.objects.create_user(username='user1', password='pass12345')
    user2 = django_user_model.objects.create_user(username='user2', password='pass12345')
    Address.objects.create(
        user=user1, recipient_name='ユーザー1', postal_code='1000001',
        prefecture='東京都', city='千代田区', phone_number='0000000000',
    )
    Address.objects.create(
        user=user2, recipient_name='ユーザー2', postal_code='1000002',
        prefecture='大阪府', city='大阪市', phone_number='0000000001',
    )

    client.force_login(user1)
    response = client.get(reverse('accounts:address_list'))
    content = response.content.decode('utf-8')

    assert 'ユーザー1' in content
    assert 'ユーザー2' not in content
