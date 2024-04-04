import requests
from decimal import Decimal

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


# dynamic conversion with API
apiKey = "fb9ae3b13f145341c09d2afe"  # exchangerate-api.com
url = f"https://v6.exchangerate-api.com/v6/{apiKey}/latest/USD"


def api_converter1(amount, from_currency, to_currency):  # from exchangerate-api.com
    response = requests.get(
        f"https://v6.exchangerate-api.com/v6/{apiKey}/latest/{from_currency}",
        params={"apiKey": apiKey}
    )
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    data = response.json()
    rates = data['conversion_rates']
    rate = rates[to_currency]
    converted_amount = Decimal(amount) * Decimal(rate)
    return converted_amount.quantize(Decimal('0.01'))


API_KEY = "fca_live_o3Jzv9ecthHunIQ2aONbN4OboAQIaTVcd632jIOP"  # freecurrencyapi.com


def api_converter2(amount, from_currency, to_currency):  # from freecurrencyapi.com
    response = requests.get(
        f"https://api.freecurrencyapi.com/v1/latest?apikey={API_KEY}&base_currency={from_currency}&currencies={to_currency}")
    data = response.json()
    rates = data['data']
    target_rate = rates[to_currency]
    converted_amount = Decimal(amount) * Decimal(target_rate)
    return converted_amount.quantize(Decimal('0.01'))


def get_conversion_rate(from_currency, to_currency):
    response = requests.get(
        f"https://api.freecurrencyapi.com/v1/latest?apikey={API_KEY}&base_currency={from_currency}&currencies={to_currency}")
    data = response.json()
    rates = data['data']
    target_rate = rates[to_currency]
    return target_rate
