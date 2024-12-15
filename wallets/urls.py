from django.urls import path
from .views import WalletCreateView, WalletStatusView

urlpatterns = [
    path('create/', WalletCreateView.as_view(), name='create_wallet'),
    path('status/', WalletStatusView.as_view(), name='get_status_wallet'),
]
