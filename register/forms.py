from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import User  # Assuming this is the path to your custom User model

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    currency = forms.ChoiceField(choices=User.CURRENCY_CHOICES, required=True,
                                 help_text=_('Select your preferred currency.'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'currency')
