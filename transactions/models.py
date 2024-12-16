from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError

from wallets.models import Wallet
from users.models import CustomUser


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('RECHARGE', 'Recharge'),
        ('CHARGE', 'Charge'),
    ]
    STATUS_TYPE_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed')
    ]
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='transactions'
    )
    commerce = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='charges'
    )
    origin_wallet = models.ForeignKey(
        Wallet, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='outgoing_transactions'
    )
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPE_CHOICES
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=STATUS_TYPE_CHOICES, default='SUCCESS'
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def process_transaction(wallet, transaction_type, amount, commerce=None):
        with transaction.atomic():
            wallet.refresh_from_db()

            try:
                amount = Decimal(amount)
                if transaction_type == 'CHARGE':
                    return Transaction._handle_charge(wallet, amount, commerce)

                return Transaction._handle_recharge(wallet, amount)

            except ValidationError as e:
                return Transaction._log_failed_transaction(
                    wallet=wallet,
                    transaction_type=transaction_type,
                    amount=amount,
                    error_message=str(e.message),
                    commerce=commerce
                )

    @staticmethod
    def _handle_charge(wallet, amount, commerce):
        if wallet.balance < amount:
            raise ValidationError('Insufficient funds')

        wallet.balance -= amount
        wallet.save()

        commerce_wallet = Wallet.objects.get(user=commerce)
        commerce_wallet.balance += amount
        commerce_wallet.save()

        _ = Transaction._log_success_transaction(
            wallet=wallet,
            transaction_type='CHARGE',
            amount=-amount,
            commerce=commerce,
        )

        commerce_transaction = Transaction._log_success_transaction(
            wallet=commerce_wallet,
            transaction_type='CHARGE',
            amount=amount,
            origin_wallet=wallet
        )

        return commerce_transaction

    @staticmethod
    def _handle_recharge(wallet, amount):
        wallet.balance += amount
        wallet.save()

        return Transaction._log_success_transaction(
            wallet=wallet,
            transaction_type='RECHARGE',
            amount=amount,
        )

    @ staticmethod
    def _log_failed_transaction(wallet,
                                transaction_type,
                                amount,
                                error_message,
                                commerce=None):
        return Transaction.objects.create(
            wallet=wallet,
            transaction_type=transaction_type,
            amount=amount,
            status='FAILED',
            error_message=error_message,
            commerce=commerce
        )

    @ staticmethod
    def _log_success_transaction(wallet,
                                 transaction_type,
                                 amount,
                                 commerce=None,
                                 origin_wallet=None):
        return Transaction.objects.create(
            wallet=wallet,
            transaction_type=transaction_type,
            amount=amount,
            status='SUCCESS',
            commerce=commerce,
            origin_wallet=origin_wallet
        )
