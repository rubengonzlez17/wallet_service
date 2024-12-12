from django.db import models
import uuid

from users.models import CustomUser


class Wallet(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='wallets')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    token = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        super().save(*args, **kwargs)
