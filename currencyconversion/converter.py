import requests
from currencyconversion.models import ExchangeRate

apiKey = "fb9ae3b13f145341c09d2afe"
url = f"https://v6.exchangerate-api.com/v6/{apiKey}/latest/USD"

# dynamic conversion with API

def convert_currency(from_currency, to_currency):
    response = requests.get(
        f"https://v6.exchangerate-api.com/v6/fb9ae3b13f145341c09d2afe/latest/{from_currency}",
        params={"apiKey": apiKey})
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    data = response.json()
    rates = data['conversion_rates']
    return rates[to_currency]
