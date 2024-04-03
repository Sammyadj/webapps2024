from django.db import models
from django.conf import settings


currency_choices = [('GBP', 'British Pound'), ('USD', 'US Dollar'), ('EUR', 'Euro')]

class Transaction(models.Model):
    # Assuming sender and receiver are both users of your system
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_transactions',
                                 on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)  # Records the time when the transaction is created
    currency = models.CharField(max_length=3, choices=currency_choices)

    def __str__(self):
        return f"Transaction from {self.sender.username} to {self.receiver.username} of {self.amount} {self.currency}"

    class Meta:
        ordering = ['-timestamp']  # Orders the transactions with the most recent first


class MoneyRequest(models.Model):
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='money_requests_made',
        on_delete=models.CASCADE
    )
    requested_from = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='money_requests_received',
        on_delete=models.CASCADE
    )
    # amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=currency_choices)
    status = models.CharField(max_length=10,
                              choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('DECLINED', 'Declined')],
                              default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request from {self.requester} to {self.requested_from} for {self.amount_requested} {self.currency}"
