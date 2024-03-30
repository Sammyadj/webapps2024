from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from register.models import User


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    currency = models.CharField(max_length=3, choices=[
        ('GBP', 'British Pound'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
    ], default='GBP', help_text=_('Select your preferred currency.'))

    def __str__(self):
        return f"{self.user.username}'s Account"
