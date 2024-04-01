from django.shortcuts import render
from .converter import convert_currency
from .forms import CurrencyConversionForm
from django.contrib import messages

# Create an exhange_rate view to display the exchange rate between two currencies
def exchange_rate(request):
    if request.method == 'POST':
        forms = CurrencyConversionForm(request.POST)
        if forms.is_valid():
            amount = forms.cleaned_data['amount']
            from_currency = forms.cleaned_data['from_currency']
            to_currency = forms.cleaned_data['to_currency']
            results = convert_currency(amount, from_currency, to_currency)
            return render(request, 'currencyconversion/exchange_rate.html', {'forms': forms, 'results': results})
        else:
            messages.error(request, 'Invalid form')
    else:
        forms = CurrencyConversionForm()
    return render(request, 'currencyconversion/exchange_rate.html', {'forms': forms})