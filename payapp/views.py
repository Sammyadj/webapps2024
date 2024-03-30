from django.shortcuts import render
from .models import Account


def home(request):
    if request.user.is_authenticated:
        # Fetch account details for authenticated users
        try:
            account = Account.objects.get(user=request.user)
        except Account.DoesNotExist:
            account = None  # Handle case where an account doesn't exist
        context = {
            'account': account,
            'is_authenticated': True,
        }
    else:
        # a different context for anonymous users
        context = {
            'is_authenticated': False,
        }
    return render(request, 'payapp/home.html', context)

# Example logic in your home view
# @login_required
# def home(request):
#     account, created = Account.objects.get_or_create(user=request.user, defaults={'balance': 0, 'currency': 'GBP'})
#     return render(request, 'payapp/home.html', {'account': account})
