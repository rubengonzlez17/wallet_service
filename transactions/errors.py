from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound


def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFound as e:
            return Response({'detail': str(e)},
                            status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'detail': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': f'Unexpected error: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper
