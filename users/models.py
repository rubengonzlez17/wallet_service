from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('CLIENT', 'Client'),
        ('COMMERCE', 'Commerce'),
    ]
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default='CLIENT')

    def clean(self):
        if self.user_type not in dict(self.USER_TYPE_CHOICES):
            raise ValidationError(
                {'user_type': f'{self.user_type} is not a valid user type.'}
            )
