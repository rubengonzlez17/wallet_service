from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound, PermissionDenied


def handle_errors(func):
    exception_to_status = {
        PermissionDenied: status.HTTP_403_FORBIDDEN,
        NotFound: status.HTTP_404_NOT_FOUND,
        ValidationError: status.HTTP_400_BAD_REQUEST
    }

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            status_code = exception_to_status.get(
                type(e),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            return Response({'detail': str(e)}, status=status_code)

    return wrapper
