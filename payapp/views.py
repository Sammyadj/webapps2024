from decimal import Decimal
from currencyconversion.converter import api_converter2
from register.models import User
from transactions.models import Transaction, MoneyRequest
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

            # Create the in-app object
            money_req = MoneyRequest.objects.create(
                requester=request.user,
                requested_from=recipient,
                amount_requested=amount,
                currency=currency_req,
                status='PENDING'
            )

            UserEmail.objects.create(
                to_user=recipient,
                from_user=request.user,
                subject='Money Request',
                body=f"{request.user} sent you a money request. Amount requested: {amount} {currency_req}.",
                sent_at=timezone.now(),
                money_request=money_req
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
    # Ensure the email object has a linked money request
    money_request_id = email.money_request.id if email.money_request else None
    email.mark_as_read()
    return render(request, 'payapp/mail_detail.html', {'email': email, 'money_request_id': money_request_id})


@login_required
def confirm_payment(request, money_request_id):
    money_request = get_object_or_404(MoneyRequest, id=money_request_id, requested_from=request.user)

    # Ensure that the money request is still pending
    if money_request.status != 'PENDING':
        messages.error(request, 'This money request has already been processed.')
        return redirect('payapp:mail_list')

    if request.method == 'POST':
        # Assume a form submission has taken place with the action being "confirm"
        with db_transaction.atomic():
            # The payee (requester) account is credited, and the payer (requested_from) is debited
            payee_account = Account.objects.select_for_update().get(user=money_request.requester)
            payer_account = Account.objects.select_for_update().get(user=request.user)

            # Perform currency conversion if necessary
            if payee_account.currency != payer_account.currency:
                converted_amount = api_converter2(money_request.amount_requested, payer_account.currency, payee_account.currency)
            else:
                converted_amount = money_request.amount_requested

            # Perform the transaction logic here
            payer_account.balance -= converted_amount
            payer_account.save()

            payee_account.balance += converted_amount
            payee_account.save()

            # Update the status of the MoneyRequest
            money_request.status = 'PAID'
            money_request.save()

            # Additional logic for sending a confirmation message or email could be added here

        messages.success(request, 'Payment confirmed successfully.')
        # Redirect to a confirmation page or the money request list
        return redirect('payapp:mail_list')

    # If it's a GET request, you could display a confirmation page with details about the money request
    return HttpResponseNotAllowed(['POST'])


@login_required
def decline_payment(request, money_request_id):
    # user_email = get_object_or_404(UserEmail, id=money_request_id, to_user=request.user)
    # if request.method == 'POST':
    #     transaction_data = request.session.get('transaction_data')
    #     if not transaction_data:
    #         messages.error(request, 'No transaction data found. Session has either ended or does not exist.')
    #         return redirect('payapp:mail_list')
    #
    # # After declining payment, delete session data related to this transaction
    #     request.session.pop('transaction_data', None)
    #     messages.success(request, "Payment declined.")
    #     return redirect('payapp:mail_list')
    # else:
    #     return HttpResponseNotAllowed(['POST'])
    pass


@login_required
def cancel_payment(request, email_id):
    # Your logic to cancel the payment
    return redirect('payapp:mail_list')
