import pytest
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
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
        password='password123',
        user_type='CLIENT'
    )
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    return api_client, user


@pytest.fixture
def auth_commerce(api_client):
    user = get_user_model().objects.create_user(
        username='testcommerce',
        email='testcommerce@example.com',
        password='password123',
        user_type='COMMERCE'
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


@pytest.fixture
def commerce_wallet(auth_commerce):
    _, user = auth_commerce
    return Wallet.objects.create(user=user,
                                 balance=200.0,
                                 token='commerce-wallet-token')


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

    def test_create_recharge_transaction_for_other_wallet(self,
                                                          commerce_wallet,
                                                          auth_client
                                                          ):
        client, user = auth_client
        data = {
            'wallet': commerce_wallet.token,
            'transaction_type': 'RECHARGE',
            'amount': 50.0
        }
        response = client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'You cannot recharge a wallet' in response.data['detail']

    def test_create_charge_transaction_success(self,
                                               wallet,
                                               auth_commerce,
                                               commerce_wallet):
        client, _ = auth_commerce
        data = {
            'wallet': wallet.token,
            'transaction_type': 'CHARGE',
            'amount': 50.0
        }
        response = client.post(self.endpoint, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['transaction_type'] == 'CHARGE'
        assert float(response.data['amount']) == 50.0

        customer_transaction = Transaction.objects.filter(
            wallet=wallet, transaction_type='CHARGE').first()
        commerce_transaction = Transaction.objects.filter(
            wallet=commerce_wallet, transaction_type='CHARGE').first()

        assert customer_transaction is not None
        assert commerce_transaction is not None

        assert float(customer_transaction.amount) == -50.0
        assert float(commerce_transaction.amount) == 50.0

        assert commerce_transaction.origin_wallet == wallet

    def test_create_charge_transaction_insufficient_funds(self,
                                                          wallet,
                                                          auth_commerce,
                                                          commerce_wallet):
        client, _ = auth_commerce
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

    def test_create_charge_transaction_invalid_user_type(self,
                                                         auth_client,
                                                         wallet):
        client, _ = auth_client
        data = {
            'wallet': wallet.token,
            'transaction_type': 'CHARGE',
            'amount': 50.00
        }

        response = client.post(self.endpoint, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Only commerces can' in response.data['detail']

    def test_create_charge_transaction_invalid_origin_wallet(self,
                                                             auth_commerce,
                                                             commerce_wallet):
        client, _ = auth_commerce
        data = {
            'wallet': commerce_wallet.token,
            'transaction_type': 'CHARGE',
            'amount': 50.00
        }

        response = client.post(self.endpoint, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Cannot charge to the commerce' in response.data['detail']

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
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

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

    def test_create_charge_transaction_fails_without_commerce_wallet(self,
                                                                     wallet,
                                                                     auth_commerce):
        client, _ = auth_commerce
        data = {
            'wallet': wallet.token,
            'transaction_type': 'CHARGE',
            'amount': 50.00
        }

        response = client.post(self.endpoint, data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'Commerce wallet not found'

    def test_create_transaction_unexpected_error(self,
                                                 mocker,
                                                 auth_client,
                                                 wallet):
        client, _ = auth_client

        mocker.patch(
            'transactions.services.TransactionService.process_transaction',
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


@pytest.mark.django_db
class TestWalletTransactionsView:
    url = '/api/transactions/'

    def test_get_wallet_transactions_successfully(self, auth_client, wallet):
        client, user = auth_client

        _ = Transaction.objects.create(
            wallet=wallet,
            transaction_type='CHARGE',
            amount=100.0
        )
        _ = Transaction.objects.create(
            wallet=wallet,
            transaction_type='CHARGE',
            amount=50.0
        )

        response = client.get(self.url,
                              {'wallet': wallet.token},
                              format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_get_wallet_transactions_without_wallet_param(self,
                                                          auth_client,
                                                          wallet):
        client, user = auth_client

        _ = Transaction.objects.create(
            wallet=wallet,
            transaction_type='CHARGE',
            amount=100.0
        )

        wallet2 = Wallet.objects.create(user=user,
                                        balance=1000.0,
                                        token='test-wallet-token-2')

        _ = Transaction.objects.create(
            wallet=wallet2,
            transaction_type='CHARGE',
            amount=100.0
        )

        response = client.get(self.url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_get_wallet_transactions_not_authenticated(self, api_client):
        response = api_client.get(
            self.url, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_wallet_transactions_not_belongs_to_user(self,
                                                         auth_client,
                                                         wallet):
        client, _ = auth_client

        other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='password456'
        )
        other_wallet = Wallet.objects.create(
            user=other_user, balance=500.0, token='other-wallet-token')

        response = client.get(
            self.url, {'wallet': other_wallet.token}, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'Wallet not found'

    def test_get_wallet_transactions_no_wallets_found(self, auth_client):
        client, _ = auth_client

        response = client.get(
            self.url, {'wallet': 'invalid-token'}, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'No wallets found for the user'

    def test_get_wallet_transactions_no_transactions(self,
                                                     auth_client,
                                                     wallet):
        client, _ = auth_client

        response = client.get(
            self.url, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'No transactions found'
