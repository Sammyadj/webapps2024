from django.db import models


class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length=3, help_text="Base currency code")
    target_currency = models.CharField(max_length=3, help_text="Target currency code")
    rate = models.DecimalField(max_digits=10, decimal_places=6, help_text="Exchange rate from base to target currency")
    last_updated = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    def __str__(self):
        return f"{self.base_currency} to {self.target_currency}: {self.rate}"
