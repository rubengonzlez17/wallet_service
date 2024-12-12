import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_create_wallet(client):
    user = get_user_model().objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='password123'
    )

    token = Token.objects.create(user=user)

    url = '/api/wallets/create/'

    data = {
        'balance': 1000.0
    }

    response = client.post(url, data, format='json',
                           HTTP_AUTHORIZATION=f'Token {token.key}')

    assert response.status_code == status.HTTP_201_CREATED
    assert 'id' in response.data
    assert float(response.data['balance']) == 1000.00


@pytest.mark.django_db
def test_create_wallet_without_authentication(client):
    url = '/api/wallets/create/'
    data = {
        'balance': 1000.0
    }

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == \
        'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_create_wallet_with_negative_balance(client):
    user = get_user_model().objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='password123'
    )

    token = Token.objects.create(user=user)

    url = '/api/wallets/create/'

    data = {
        'balance': -100.0
    }

    response = client.post(url, data, format='json',
                           HTTP_AUTHORIZATION=f'Token {token.key}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'balance' in response.data
