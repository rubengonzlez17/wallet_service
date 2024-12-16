import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from wallets.models import Wallet
from wallets.serializers import WalletSerializer

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='password123'
    )
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    return api_client, user


@pytest.fixture
def wallet(auth_client):
    _, user = auth_client
    return Wallet.objects.create(user=user,
                                 balance=100.0,
                                 token='test-wallet-token')


@pytest.mark.django_db
class TestWalletCreation:
    endpoint = '/api/wallets/create/'

    def test_create_wallet_successfully(self, auth_client):
        client, _ = auth_client

        data = {
            'balance': 1000.0
        }

        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert float(response.data['balance']) == 1000.00

    def test_create_wallet_without_authentication(self, api_client):
        data = {
            'balance': 1000.0
        }

        response = api_client.post(self.endpoint, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_wallet_with_negative_balance(self, auth_client):
        client, _ = auth_client

        data = {
            'balance': -100.0
        }

        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'balance' in response.data


@pytest.mark.django_db
class TestWalletStatus:
    endpoint = '/api/wallets/status/'

    def test_get_wallets_successfully(self, auth_client, wallet):
        client, user = auth_client
        additional_wallet = Wallet.objects.create(
            user=user, balance=500.0, token='another-token')

        response = client.get(self.endpoint, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        serialized_wallets = WalletSerializer(
            [wallet, additional_wallet], many=True).data
        assert response.data == serialized_wallets

    def test_get_wallets_not_authenticated(self, api_client):
        response = api_client.get(self.endpoint, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_wallets_no_wallets_found(self, auth_client):
        client, _ = auth_client

        response = client.get(self.endpoint, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'No wallets found for the user'
