from django.urls import path
from .views import WalletCreateView

urlpatterns = [
    path('create/', WalletCreateView.as_view(), name='create_wallet'),
]
