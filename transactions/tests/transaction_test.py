import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from wallets.models import Wallet
from transactions.models import Transaction

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    user = get_user_model().objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='password123'
    )
    api_client.force_authenticate(user)
    return api_client, user


@pytest.fixture
def wallet(auth_client):
    _, user = auth_client
    return Wallet.objects.create(user=user,
                                 balance=100.0,
                                 token='test-wallet-token')


@pytest.mark.django_db
class TestTransactionCreateView:
    endpoint = '/api/transactions/create/'

    def test_create_recharge_transaction_success(self, auth_client, wallet):
        client, _ = auth_client
        data = {
            'wallet': wallet.token,
            'transaction_type': 'RECHARGE',
            'amount': 50.0
        }
        response = client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['transaction_type'] == 'RECHARGE'
        assert float(response.data['amount']) == 50.0

    def test_create_charge_transaction_success(self, auth_client, wallet):
        client, _ = auth_client
        data = {
            'wallet': wallet.token,
            'transaction_type': 'CHARGE',
            'amount': 50.0
        }
        response = client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['transaction_type'] == 'CHARGE'
        assert float(response.data['amount']) == 50.0

    def test_create_charge_transaction_insufficient_funds(self,
                                                          auth_client,
                                                          wallet):
        client, _ = auth_client
        data = {
            'wallet': wallet.token,
            'transaction_type': 'CHARGE',
            'amount': 200.0  # Exceeds wallet balance (100 < 200)
        }
        response = client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'FAILED'
        assert response.data['error_message'] == 'Insufficient funds'

        transactions = Transaction.objects.filter(wallet=wallet,
                                                  status='FAILED')
        assert transactions.count() == 1
        assert transactions.first().error_message == 'Insufficient funds'

    def test_create_charge_transaction_fails_without_commerce_wallet(self,
                                                                     wallet):
        commerce_user = User.objects.create_user(username='commerce',
                                                 email='commerce@example.com',
                                                 password='password123')
        client = APIClient()
        client.force_authenticate(user=commerce_user)
        data = {
            'wallet': wallet.token,
            'transaction_type': 'CHARGE',
            'amount': 50.00
        }

        response = client.post(self.endpoint, data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'Commerce wallet not found'

    def test_create_charge_transaction_amount_must_be_positive(self,
                                                               auth_client,
                                                               wallet):
        client, _ = auth_client
        data = {
            'wallet': wallet.token,
            'transaction_type': 'CHARGE',
            'amount': -50.0
        }
        response = client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'amount' in response.data['detail']

    def test_create_transaction_invalid_data(self, auth_client, wallet):
        client, _ = auth_client
        data = {
            'wallet': wallet.token,
            'transaction_type': 'INVALID_TYPE',
            'amount': 50.0
        }
        response = client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'transaction_type' in response.data['detail']

    def test_create_transaction_missing_fields(self, auth_client, wallet):
        client, _ = auth_client
        data = {
            'wallet': wallet.token,
        }
        response = client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'transaction_type' in response.data['detail']
        assert 'amount' in response.data['detail']

    def test_create_transaction_not_authenticated(self, api_client):
        data = {
            'wallet': 'test-wallet-token',
            'transaction_type': 'RECHARGE',
            'amount': 50.0
        }
        response = api_client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_transaction_wallet_not_found(self, auth_client):
        client, _ = auth_client
        data = {
            'wallet': 'non-existent-token',
            'transaction_type': 'RECHARGE',
            'amount': 50.0
        }
        response = client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'Wallet not found'

    def test_create_transaction_unexpected_error(self,
                                                 mocker,
                                                 auth_client,
                                                 wallet):
        client, _ = auth_client

        mocker.patch(
            'transactions.services.TransactionService.validate_and_process_transaction',
            side_effect=Exception('Unexpected error')
        )

        data = {
            'wallet': wallet.token,
            'transaction_type': 'RECHARGE',
            'amount': 50.0
        }
        response = client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'Unexpected error' in response.data['detail']