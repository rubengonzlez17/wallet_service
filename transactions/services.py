from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound

from wallets.models import Wallet
from transactions.models import Transaction


class TransactionService:
    @staticmethod
    def validate_and_process_transaction(wallet_token, transaction_type, amount, commerce=None):
        if not wallet_token or not transaction_type or amount is None:
            raise ValidationError('Missing required fields: wallet, transaction_type, or amount.')

        if transaction_type not in ['RECHARGE', 'CHARGE']:
            raise ValidationError("Invalid transaction_type. Must be 'RECHARGE' or 'CHARGE'.")

        amount = float(amount)
        if amount <= 0:
            raise ValidationError('The transaction amount must be greater than zero.')

        try:
            wallet = Wallet.objects.get(token=wallet_token)
        except Wallet.DoesNotExist:
            raise NotFound('Wallet not found')

        commerce_wallet = None
        if transaction_type == 'CHARGE':
            # if commerce.user_type == 'CLIENT':
            #    raise ValidationError('Only commerces can initiate a charge transaction. Customers are not allowed to make charge transactions.')

            commerce_wallet = Wallet.objects.filter(user=commerce).first()
            if not commerce_wallet:
                raise NotFound('Commerce wallet not found')

            # if wallet_token == commerce_wallet.token:
            #    raise ValidationError("Cannot charge to the commerce's own wallet")

        return Transaction.process_transaction(
            wallet=wallet,
            transaction_type=transaction_type,
            amount=amount,
            commerce=commerce if transaction_type == 'CHARGE' else None
        )
