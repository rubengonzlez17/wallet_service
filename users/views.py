from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer


class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)

        return user, token

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        _, token = self.perform_create(serializer)

        return Response({
            'token': token.key,
            'message': 'User successfully registered.',
        }, status=status.HTTP_201_CREATED)
