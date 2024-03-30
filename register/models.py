from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    # Define currency choices
    CURRENCY_CHOICES = [
        ('GBP', 'British Pound'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
    ]
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)

    # Add a currency field to the user model
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='GBP',
        help_text=_('Select your preferred currency.'),
    )

    def __str__(self):
        return self.username

    # Add any additional fields if needed
