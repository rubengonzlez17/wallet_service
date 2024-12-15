from django.urls import path
from .views import TransactionCreateView, WalletTransactionsView

urlpatterns = [
    path('create/', TransactionCreateView.as_view(), name='create_tx'),
    path('', WalletTransactionsView.as_view(), name='get_wallet_transactions'),
]
