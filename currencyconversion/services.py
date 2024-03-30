from decimal import Decimal
import requests
from django.conf import settings

# Static conversion rates
RATES = {
    'GBP_to_USD': Decimal('1.2640'),
    'GBP_to_EUR': Decimal('1.1578'),
    'EUR_to_USD': Decimal('1.0795'),
    'USD_to_GBP': Decimal('0.7914'),
    'EUR_to_GBP': Decimal('0.8641'),
    'USD_to_EUR': Decimal('0.9271')
}


def convert_currency(amount, from_currency, to_currency):
    conversion_key = f"{from_currency}_to_{to_currency}"
    rate = RATES.get(conversion_key)

    if rate is None:
        raise ValueError(f"No conversion rate from {from_currency} to {to_currency}.")

    return (Decimal(amount) * rate).quantize(Decimal('0.01'))


def get_conversion_rate(from_currency, to_currency):
    response = requests.get(
        f"https://api.exchangerate-api.com/v4/latest/{from_currency}",
        params={"apiKey": settings.EXCHANGE_RATE_API_KEY}
    )
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    data = response.json()
    rates = data['rates']
    return rates[to_currency]
