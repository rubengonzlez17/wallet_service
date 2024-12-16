from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import TransactionSerializer
from .services import TransactionService
from .errors import handle_errors


class TransactionCreateView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    @handle_errors
    def create(self, request, *args, **kwargs):
        wallet_token = request.data.get('wallet')
        transaction_type = request.data.get('transaction_type')
        amount = request.data.get('amount')

        transaction = TransactionService.validate_and_process_transaction(
            wallet_token=wallet_token,
            transaction_type=transaction_type,
            amount=amount,
            commerce=request.user
        )

        return Response(TransactionSerializer(transaction).data,
                        status=status.HTTP_201_CREATED)


class WalletTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('wallet',
                              openapi.IN_QUERY,
                              description='Token of the wallet',
                              type=openapi.TYPE_STRING,
                              required=False)
        ]
    )
    @handle_errors
    def get(self, request):
        wallet_token = request.query_params.get('wallet')
        transactions = TransactionService.get_transactions(request.user,
                                                           wallet_token)

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
