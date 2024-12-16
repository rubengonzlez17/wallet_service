from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'wallet', 'transaction_type', 'amount', 'status',
                  'error_message', 'commerce', 'origin_wallet', 'created_at']
        read_only_fields = ['status', 'created_at']
