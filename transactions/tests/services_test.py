from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound, PermissionDenied

from wallets.models import Wallet
from transactions.models import Transaction
from users.models import CustomUser
from transactions.services import TransactionService


class TransactionServiceTest(TestCase):

    def setUp(self):
        self.user1 = CustomUser.objects.create(username='user1')
        self.user2 = CustomUser.objects.create(username='user2')
        self.commerce_user = CustomUser.objects.create(
            username='commerce_user', user_type='COMMERCE')

        self.wallet1 = Wallet.objects.create(user=self.user1, token='wallet1')
        self.wallet2 = Wallet.objects.create(user=self.user2, token='wallet2')
        self.commerce_wallet = Wallet.objects.create(
            user=self.commerce_user, token='commerce_wallet')

        self.transaction_data = {
            'wallet_token': 'wallet1',
            'transaction_type': 'RECHARGE',
            'amount': 100.0,
        }

    def test_missing_required_fields(self):
        with self.assertRaises(ValidationError):
            TransactionService.validate_transaction(
                wallet_token=None,
                transaction_type='RECHARGE',
                amount=100)

        with self.assertRaises(ValidationError):
            TransactionService.validate_transaction(
                wallet_token='wallet1',
                transaction_type=None,
                amount=100)

        with self.assertRaises(ValidationError):
            TransactionService.validate_transaction(
                wallet_token='wallet1',
                transaction_type='RECHARGE',
                amount=None)

    def test_invalid_transaction_type(self):
        with self.assertRaises(ValidationError):
            TransactionService.validate_transaction(
                wallet_token='wallet1',
                transaction_type='INVALID',
                amount=100)

    def test_invalid_amount(self):
        with self.assertRaises(ValidationError):
            TransactionService.validate_transaction(
                wallet_token='wallet1',
                transaction_type='RECHARGE',
                amount=-10)

        with self.assertRaises(ValidationError):
            TransactionService.validate_transaction(
                wallet_token='wallet1',
                transaction_type='RECHARGE',
                amount=0)

    def test_wallet_not_found(self):
        with self.assertRaises(NotFound):
            TransactionService.validate_transaction(
                wallet_token='non_existing_token',
                transaction_type='RECHARGE',
                amount=100)

    def test_commerce_wallet_not_found(self):
        commerce_user = CustomUser.objects.create(
            username='commerce_user_2', user_type='COMMERCE')
        with self.assertRaises(NotFound):
            TransactionService.validate_transaction(
                wallet_token='wallet1',
                transaction_type='CHARGE',
                amount=100,
                commerce=commerce_user)

    def test_recharge_wallet_not_belongs_to_commerce(self):
        with self.assertRaises(PermissionDenied):
            TransactionService.validate_transaction(
                wallet_token='wallet1',
                transaction_type='RECHARGE',
                amount=100,
                commerce=self.commerce_user)

    def test_charge_from_client_wallet(self):
        with self.assertRaises(ValidationError):
            TransactionService.validate_transaction(
                wallet_token='wallet1',
                transaction_type='CHARGE',
                amount=100,
                commerce=self.user1)

    def test_charge_to_own_commerce_wallet(self):
        with self.assertRaises(ValidationError):
            TransactionService.validate_transaction(
                wallet_token='commerce_wallet',
                transaction_type='CHARGE',
                amount=100,
                commerce=self.commerce_user)

    def test_get_transactions_no_wallets_for_user(self):
        user3 = CustomUser.objects.create(username='user3')
        with self.assertRaises(NotFound):
            TransactionService.get_transactions(user=user3)

    def test_get_transactions_no_wallets(self):
        with self.assertRaises(NotFound):
            TransactionService.get_transactions(user=self.user1)

    def test_get_transactions_no_transactions(self):
        self.wallet1.transactions.all().delete()
        with self.assertRaises(NotFound):
            TransactionService.get_transactions(
                user=self.user1, wallet_token='wallet1')

    def test_get_transactions_for_user(self):
        transaction = Transaction.objects.create(
            wallet=self.wallet1, transaction_type='RECHARGE', amount=100)
        transactions = TransactionService.get_transactions(user=self.user1)
        self.assertEqual(transactions.count(), 1)
        self.assertEqual(transactions.first(), transaction)

    def test_process_transaction(self):
        transaction = TransactionService.process_transaction(
                wallet_token='wallet1',
                transaction_type='RECHARGE',
                amount=100.0,
                commerce=self.user1
            )
        self.assertEqual(transaction.wallet.token, self.wallet1.token)
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.transaction_type, 'RECHARGE')
