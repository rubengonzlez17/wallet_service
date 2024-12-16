import pytest
from decimal import Decimal
from users.models import CustomUser
from wallets.models import Wallet
from wallets.serializers import WalletSerializer
from rest_framework.exceptions import ValidationError


@pytest.fixture
def user_and_wallet(db):
    user = CustomUser.objects.create(username='test_user')
    wallet = Wallet.objects.create(user=user, balance=Decimal('100.00'))
    return user, wallet


@pytest.mark.django_db
class TestWalletSerializer:

    def test_wallet_serializer_valid_data(self, user_and_wallet):
        user, wallet = user_and_wallet

        serializer = WalletSerializer(wallet)
        data = serializer.data

        assert data['id'] == wallet.id
        assert data['balance'] == '100.00'
        assert data['token'] == wallet.token
        assert data['created_at'] is not None
        assert data['user'] == wallet.user.id

    def test_wallet_serializer_negative_balance(self):
        invalid_data = {'balance': Decimal('-50.00')}
        serializer = WalletSerializer(data=invalid_data)

        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)

        assert 'The balance cannot be negative.' in str(error.value)

    def test_wallet_serializer_partial_update_balance(self, user_and_wallet):
        user, wallet = user_and_wallet

        data = {'balance': Decimal('200.00')}
        serializer = WalletSerializer(wallet, data=data, partial=True)

        assert serializer.is_valid()
        updated_wallet = serializer.save()

        assert updated_wallet.balance == Decimal('200.00')

    def test_wallet_serializer_empty_data(self, user_and_wallet):
        user, _ = user_and_wallet
        serializer = WalletSerializer(data={})

        assert serializer.is_valid()
        wallet = serializer.save(user=user)

        assert wallet.balance == Decimal('0.00')
