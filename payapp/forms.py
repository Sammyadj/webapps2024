from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# Assuming 'CURRENCY_CHOICES' is defined somewhere in your code,
# if not, you would need to define it. For now, I'm going to create a sample.

CURRENCY_CHOICES = [
    ('GBP', 'British Pound'),
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'), ]


class MoneyRequestForm(forms.Form):
    receiver_username = forms.CharField(
        max_length=150,
        label=_('Receiver Username'),
        help_text=_('Enter the username of the user to request money from.')
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label=_('Amount'),
        help_text=_('Enter the amount you want to request.')
    )
    currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        label=_('Currency'),
        help_text=_('Select the currency for the requested amount.')
    )

    def clean_receiver_username(self):
        username = self.cleaned_data.get('receiver_username')
        if not User.objects.filter(username=username).exists():
            raise ValidationError(_('The username entered does not exist.'))
        return username

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError(_('The amount must be greater than zero.'))
        return amount

# This form can now be used in your view to validate the data and create a MoneyRequest.
