import pytest
from decimal import Decimal
from transactions.models import Transaction
from wallets.models import Wallet
from users.models import CustomUser


@pytest.fixture
def setup_data(db):
    user1 = CustomUser.objects.create(username='user1')
    user2 = CustomUser.objects.create(username='user2')
    commerce_user = CustomUser.objects.create(
        username='commerce_user', user_type='COMMERCE')

    wallet1 = Wallet.objects.create(
        user=user1, balance=Decimal('100.00'), token='wallet1')
    wallet2 = Wallet.objects.create(
        user=user2, balance=Decimal('50.00'), token='wallet2')
    commerce_wallet = Wallet.objects.create(
        user=commerce_user, balance=Decimal('200.00'), token='commerce_wallet')

    return {
        'user1': user1,
        'user2': user2,
        'commerce_user': commerce_user,
        'wallet1': wallet1,
        'wallet2': wallet2,
        'commerce_wallet': commerce_wallet,
    }


def test_process_recharge_success(setup_data):
    wallet1 = setup_data['wallet1']
    transaction = Transaction.process_transaction(
        wallet=wallet1, transaction_type='RECHARGE', amount=Decimal('50.00'))

    wallet1.refresh_from_db()

    assert wallet1.balance == Decimal('150.00')
    assert transaction.transaction_type == 'RECHARGE'
    assert transaction.status == 'SUCCESS'
    assert transaction.amount == Decimal('50.00')


def test_process_charge_success(setup_data):
    wallet1 = setup_data['wallet1']
    commerce_user = setup_data['commerce_user']
    commerce_wallet = setup_data['commerce_wallet']
    initial_balance = commerce_wallet.balance

    transaction = Transaction.process_transaction(wallet=wallet1,
                                                  transaction_type='CHARGE',
                                                  amount=Decimal('50.00'),
                                                  commerce=commerce_user)

    wallet1.refresh_from_db()
    commerce_wallet.refresh_from_db()

    assert wallet1.balance == Decimal('50.00')
    assert commerce_wallet.balance == Decimal('250.00')

    assert transaction.wallet.balance == initial_balance + Decimal('50.00')
    assert transaction.transaction_type == 'CHARGE'
    assert transaction.amount == Decimal('50.00')
    assert transaction.status == 'SUCCESS'


def test_process_charge_fails_insufficient_funds(setup_data):
    wallet1 = setup_data['wallet1']
    commerce_user = setup_data['commerce_user']

    Transaction.process_transaction(wallet=wallet1,
                                    transaction_type='CHARGE',
                                    amount=Decimal('200.00'),
                                    commerce=commerce_user)

    failed_transaction = Transaction.objects.filter(status='FAILED').first()

    assert failed_transaction is not None
    assert failed_transaction.wallet == wallet1
    assert failed_transaction.transaction_type == 'CHARGE'
    assert failed_transaction.amount == Decimal('200.00')
    assert failed_transaction.status == 'FAILED'
    assert 'Insufficient funds' in failed_transaction.error_message


def test_successful_transaction_logging(setup_data):
    wallet1 = setup_data['wallet1']

    Transaction.process_transaction(
        wallet=wallet1, transaction_type='RECHARGE', amount=Decimal('50.00'))

    success_transaction = Transaction.objects.filter(status='SUCCESS').first()

    assert success_transaction is not None
    assert success_transaction.wallet == wallet1
    assert success_transaction.transaction_type == 'RECHARGE'
    assert success_transaction.amount == Decimal('50.00')
    assert success_transaction.status == 'SUCCESS'
