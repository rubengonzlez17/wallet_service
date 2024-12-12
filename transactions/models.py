from django.db import models
from wallets.models import Wallet


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    ]
    STATUS_TYPE_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed')
    ]
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=STATUS_TYPE_CHOICES, default='SUCCESS')
    created_at = models.DateTimeField(auto_now_add=True)
