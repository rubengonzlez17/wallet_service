from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound, PermissionDenied

from wallets.models import Wallet
from transactions.models import Transaction


class TransactionService:
    @staticmethod
    def process_transaction(wallet_token,
                            transaction_type,
                            amount,
                            commerce=None):
        wallet = TransactionService.validate_transaction(wallet_token,
                                                         transaction_type,
                                                         amount,
                                                         commerce)

        return Transaction.process_transaction(
            wallet=wallet,
            transaction_type=transaction_type,
            amount=amount,
            commerce=commerce if transaction_type == 'CHARGE' else None
        )

    @staticmethod
    def validate_transaction(wallet_token,
                             transaction_type,
                             amount,
                             commerce=None):
        if not wallet_token or not transaction_type or amount is None:
            raise ValidationError(
                'Missing required fields: wallet, transaction_type, or amount')

        if transaction_type not in ['RECHARGE', 'CHARGE']:
            raise ValidationError(
                "Invalid transaction_type. Must be 'RECHARGE' or 'CHARGE'")

        amount = float(amount)
        if amount <= 0:
            raise ValidationError(
                'The transaction amount must be greater than zero')

        try:
            wallet = Wallet.objects.get(token=wallet_token)
        except Wallet.DoesNotExist:
            raise NotFound('Wallet not found')

        if transaction_type == 'RECHARGE':
            if wallet.user != commerce:
                raise PermissionDenied(
                    'You cannot recharge a wallet that is not yours')

        commerce_wallet = None
        if transaction_type == 'CHARGE':
            if commerce.user_type == 'CLIENT':
                raise ValidationError(
                    'Only commerces can initiate a charge transaction')

            commerce_wallet = Wallet.objects.filter(user=commerce).first()
            if not commerce_wallet:
                raise NotFound('Commerce wallet not found')

            if wallet_token == commerce_wallet.token:
                raise ValidationError(
                    "Cannot charge to the commerce's own wallet")

        return wallet

    @staticmethod
    def get_transactions(user, wallet_token=None):
        wallets = Wallet.objects.filter(user=user)
        if not wallets.exists():
            raise NotFound('No wallets found for the user')

        if wallet_token:
            transactions = Transaction.objects.filter(
                wallet__token=wallet_token).order_by('-created_at')
        else:
            transactions = Transaction.objects.filter(
                wallet__in=wallets).order_by('-created_at')

        if not transactions.exists():
            if wallet_token:
                raise NotFound('Wallet not found')

            raise NotFound('No transactions found')

        return transactions
