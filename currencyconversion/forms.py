from .models import CurrencyConversion
from django import forms


class CurrencyConversionForm(forms.ModelForm):
    class Meta:
        model = CurrencyConversion
        fields = ['amount', 'from_currency', 'to_currency']
