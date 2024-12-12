from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import WalletSerializer


class WalletCreateView(generics.CreateAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        wallet = serializer.save(user=self.request.user)
        return WalletSerializer(wallet)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        wallet = self.perform_create(serializer)

        return Response(wallet.data, status=status.HTTP_201_CREATED)
