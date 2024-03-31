from django.db import models


class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length=3, help_text="Base currency code")
    target_currency = models.CharField(max_length=3, help_text="Target currency code")
    rate = models.DecimalField(max_digits=10, decimal_places=6, help_text="Exchange rate from base to target currency")
    last_updated = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    def __str__(self):
        return f"{self.base_currency} to {self.target_currency}: {self.rate}"


class CurrencyConversion(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount to convert")
    from_currency = models.CharField(max_length=3, help_text="Currency code to convert from")
    to_currency = models.CharField(max_length=3, help_text="Currency code to convert to")
    converted_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Converted amount")
    conversion_rate = models.DecimalField(max_digits=10, decimal_places=6, help_text="Conversion rate")
    conversion_date = models.DateTimeField(auto_now_add=True, help_text="Conversion date")

    def __str__(self):
        return f"{self.amount} {self.from_currency} to {self.converted_amount} {self.to_currency}"