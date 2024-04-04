from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from register.models import User
from django.utils import timezone

class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    currency = models.CharField(max_length=3, choices=[
        ('GBP', 'British Pound'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
    ], default='GBP', help_text=_('Select your preferred currency.'))

    def __str__(self):
        return f"{self.user.username}'s Account"


class UserEmail(models.Model):
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_emails', on_delete=models.CASCADE)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_emails', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.to_user.username}: {self.subject}"

    def mark_as_read(self):
        self.read = True
        self.save()


# class UserNotification(models.Model):
#     recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
#     title = models.CharField(max_length=255)
#     message = models.TextField()
#     timestamp = models.DateTimeField(default=timezone.now)
#     read = models.BooleanField(default=False)
#
#     def __str__(self):
#         return f"Notification for {self.recipient.username}: {self.title}"
#
#     def mark_as_read(self):
#         self.read = True
#         self.save()