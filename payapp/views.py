from decimal import Decimal
from currencyconversion.converter import api_converter2
from register.models import User
from transactions.models import Transaction
from .forms import MoneyRequestForm
from .models import Account, UserEmail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction as db_transaction
from django.http import HttpResponseNotAllowed


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


@login_required
def request_money_web(request):
    context = {'active_tab': 'request_web'}
    if request.method == 'POST':
        money_request_form = MoneyRequestForm(request.POST)
        if money_request_form.is_valid():
            receiver_username = money_request_form.cleaned_data['receiver_username']
            amount = money_request_form.cleaned_data['amount']
            currency_req = money_request_form.cleaned_data['currency']
            # Get the User object from the username
            try:
                recipient = User.objects.get(username=receiver_username)
                if recipient == request.user:  # User is trying to request money from themselves
                    messages.error(request, "You cannot request money from yourself.")
                    money_request_form = MoneyRequestForm()
                    context['money_request_form'] = money_request_form
                    return render(request, 'transactions/send_and_receive.html', context)
            except User.DoesNotExist:
                messages.error(request, "No user with this username found.")
                money_request_form = MoneyRequestForm()
                context['money_request_form'] = money_request_form
                return render(request, 'transactions/send_and_receive.html', context)

            sender_account = get_object_or_404(Account, user=request.user)
            if currency_req != sender_account.currency:  # User is trying to request money in a different currency
                messages.error(request, "The selected currency must be the same as your account's currency.")
                money_request_form = MoneyRequestForm()
                context['money_request_form'] = money_request_form
                return render(request, 'transactions/send_and_receive.html', context)

            # Create the in-app email instance
            request.session['transaction_data'] = {
                'recipient_id': recipient.id,
                'amount': str(amount),
                'currency_req': currency_req
            }

            UserEmail.objects.create(
                to_user=recipient,
                from_user=request.user,
                subject='Money Request',
                body=f"{request.user} sent you a money request. Amount requested: {amount} {currency_req}.",
                sent_at=timezone.now()
            )

            messages.success(request, 'Money request sent successfully.')
            return redirect('transactions:list')  # Update redirect as necessary
        else:
            messages.error(request, "Form is not valid.")
    else:
        money_request_form = MoneyRequestForm()

    context['money_request_form'] = money_request_form
    return render(request, 'transactions/send_and_receive.html', context)


@login_required
def mail_list(request):
    emails = UserEmail.objects.filter(to_user=request.user).order_by('-sent_at')
    return render(request, 'payapp/mail_list.html', {'emails': emails})


@login_required
def mail_detail(request, email_id):
    email = get_object_or_404(UserEmail, id=email_id, to_user=request.user)
    email.mark_as_read()
    return render(request, 'payapp/mail_detail.html', {'email': email})


@login_required
def confirm_payment(request, email_id):
    user_email = get_object_or_404(UserEmail, id=email_id, to_user=request.user)
    transaction_data = request.session.get('transaction_data')

    if not transaction_data or str(user_email.to_user.id) != transaction_data.get('recipient_id'):
        messages.error(request, 'There was a problem with your transaction data.')
        return redirect('payapp:mail_list')
    # Logic to confirm the payment
    if request.method == 'POST':
        with db_transaction.atomic():
            # payee is the requester (the original sender of the money request message)
            # payer is the recipient (the receiver of the money request message)
            payee = Account.objects.select_for_update().get(user=request.user)
            payer = User.objects.get(username=transaction_data['recipient'])
            amount = Decimal(transaction_data['amount'])
            currency_req = transaction_data['currency_req']
            payee_account = Account.objects.select_for_update().get(user=payee)

            # Convert the amount to the receiver's currency if different
            if payer.currency != payee_account.currency:
                amount = api_converter2(amount, payer.currency, payee_account.currency)

            # Create the transaction record
            Transaction.objects.create(
                sender=request.user,
                receiver=payee,
                amount=amount,
                currency=currency_req
            )

            # Update the sender's and receiver's account balances
            payer.balance -= amount  # Debit the payer's account with the amount
            payer.save()
            payee_account.balance += amount  # Credit the payee's account with the amount
            payee_account.save()
    # After confirming payment, delete session data related to this transaction
    del request.session['transaction_data']
    messages.success(request, "Payment confirmed.")
    return redirect('payapp:mail_list')


@login_required
def decline_payment(request, email_id):
    user_email = get_object_or_404(UserEmail, id=email_id, to_user=request.user)
    if request.method == 'POST':
        transaction_data = request.session.get('transaction_data')
        if not transaction_data:
            messages.error(request, 'No transaction data found. Session has either ended or does not exist.')
            return redirect('payapp:mail_list')

    # After declining payment, delete session data related to this transaction
        request.session.pop('transaction_data', None)
        messages.success(request, "Payment declined.")
        return redirect('payapp:mail_list')
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def cancel_payment(request, email_id):
    # Your logic to cancel the payment
    return redirect('payapp:mail_list')
