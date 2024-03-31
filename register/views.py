from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from currencyconversion.services import convert_currency
from payapp.models import Account
from .forms import RegisterForm
from django.contrib import messages
from decimal import Decimal
from django.urls import reverse


def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            selected_currency = form.cleaned_data['currency']

            # Assume GBP is the base currency with an initial balance of 1000
            initial_balance = Decimal('1000')
            if selected_currency != 'GBP':
                # Convert initial balance to the selected currency
                initial_balance = convert_currency(initial_balance, 'GBP', selected_currency)

            user.save()  # save the User instance

            # Create the user's Account with the converted balance
            Account.objects.create(user=user, balance=initial_balance, currency=selected_currency)

            messages.success(request, 'Registration Successful!')
            return redirect('login')
        else:
            messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = RegisterForm()
    return render(request, 'register/register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            # if user is not None:
            #     login(request, user)
            #     return redirect('home')
            if user is not None and user.is_active:
                login(request, user)
                next_url = request.GET.get('next', reverse('home'))  # Default to 'home' if no next parameter
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'register/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('home')  # Redirect to the login page after logout
