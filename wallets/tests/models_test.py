import pytest
from decimal import Decimal
from users.models import CustomUser
from wallets.models import Wallet
import uuid


@pytest.mark.django_db
class TestWalletModel:

    def test_wallet_creation(self):
        user = CustomUser.objects.create(username='test_user')
        wallet = Wallet.objects.create(user=user)

        assert wallet.user == user
        assert wallet.balance == Decimal('0.00')
        assert wallet.token is not None
        assert len(wallet.token) == 32  # UUID4 token has 32 hexadecimal char
        assert isinstance(uuid.UUID(wallet.token, version=4), uuid.UUID)

    def test_wallet_custom_balance(self):
        user = CustomUser.objects.create(username='test_user')
        wallet = Wallet.objects.create(user=user, balance=Decimal('100.50'))

        assert wallet.balance == Decimal('100.50')

    def test_wallet_token_immutable(self):
        user = CustomUser.objects.create(username='test_user')
        wallet = Wallet.objects.create(user=user)
        original_token = wallet.token

        wallet.balance = Decimal('200.00')
        wallet.save()
        wallet.refresh_from_db()

        assert wallet.token == original_token
        assert wallet.balance == Decimal('200.00')

    def test_wallet_unique_token(self):
        user1 = CustomUser.objects.create(username='user1')
        user2 = CustomUser.objects.create(username='user2')

        wallet1 = Wallet.objects.create(user=user1)
        wallet2 = Wallet.objects.create(user=user2)

        assert wallet1.token != wallet2.token

    def test_wallet_created_at(self):
        user = CustomUser.objects.create(username='test_user')
        wallet = Wallet.objects.create(user=user)

        assert wallet.created_at is not None
