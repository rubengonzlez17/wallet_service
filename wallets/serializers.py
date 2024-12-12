from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance', 'token', 'created_at']
        read_only_fields = ['user', 'token', 'created_at']

    def validate_balance(self, value):
        if value < 0:
            raise ValidationError('The balance cannot be negative.')
        return value
