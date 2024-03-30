from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from payapp.models import Account

User = get_user_model()

currency_choices = [
    ('GBP', 'British Pound'),
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'), ]


class TransferForm(forms.Form):
    receiver = forms.CharField(max_length=150, label=_('Receiver'),
                               help_text=_('Enter the username of the user to transfer money to.'))
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label=_('Amount'))
    currency = forms.ChoiceField(choices=currency_choices, label=_('Currency'))

    def clean_receiver(self):
        username = self.cleaned_data['receiver']
        try:
            receiver = User.objects.get(username=username)
            return receiver
        except User.DoesNotExist:
            raise ValidationError(_('User with this username does not exist. Please enter a valid username.'))

    def clean_amount(self):
        # validation for amount here
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError(_('The amount must be greater than zero.'))
        return amount

    def clean(self):
        # Call the base class's clean method to ensure any validation logic in parent classes is maintained
        cleaned_data = super().clean()

        # Perform additional validations only if the earlier field-specific validations have passed
        if 'receiver' in cleaned_data and 'amount' in cleaned_data:
            receiver = cleaned_data.get('receiver')
            amount = cleaned_data.get('amount')
            user = self.initial.get('user')  # Pass the user from the view when initializing the form
            if not user:
                raise forms.ValidationError("User is not provided.")

            # Fetch the sender's account with a lock to prevent race conditions
            sender_account = Account.objects.select_for_update().get(user=user)

            # Perform the balance check and raise an error if the sender does not have enough funds
            if sender_account.balance < amount:
                raise forms.ValidationError(_('Insufficient balance in your account to complete the transfer.'))

        # return the full collection of cleaned data
        return cleaned_data


class RequestForm(forms.Form):
    # Add the necessary fields for requesting money
    requester = forms.CharField(max_length=150, label=_('Requester'), required=False)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label=_('Amount'))
    currency = forms.ChoiceField(choices=currency_choices, label=_('Currency'))
    # Add any additional fields and methods needed
