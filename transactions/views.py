from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import TransferForm, RequestForm, User, PaymentConfirmationForm
from .models import Transaction, MoneyRequest
from django.db.models import Q
from payapp.models import Account
from currencyconversion.converter import convert_currency, api_converter1, api_converter2, get_conversion_rate
from django.db import transaction as db_transaction
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from payapp.views import request_money_web
from django.http import HttpResponseNotAllowed


@login_required
def handle_payment(request, money_request_id):
    money_request = get_object_or_404(MoneyRequest, id=money_request_id)

    # Check if the logged-in user is the requested_from user
    if request.user != money_request.requested_from:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('transactions:list')

    if request.method == 'POST':
        # If you're using the Django form
        form = PaymentConfirmationForm(request.POST)
        if form.is_valid():
            # Process payment here
            money_request.status = 'PAID'
            money_request.save()
            messages.success(request, "Payment successful.")
            return redirect('transactions:list')
        # Else, for a simple HTML form
        money_request.status = 'PAID'
        money_request.save()
        messages.success(request, "Payment successful.")
        return redirect('transactions:list')
    else:
        form = PaymentConfirmationForm()
        return render(request, 'transactions/handle_payment.html', {'form': form, 'money_request': money_request})


@login_required
def decline_payment(request, money_request_id):
    money_request = get_object_or_404(MoneyRequest, id=money_request_id)

    # Check if the logged-in user is the requested_from user
    if request.user != money_request.requested_from:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('transactions:list')

    # Update the MoneyRequest status to "DECLINED"
    money_request.status = 'DECLINED'
    money_request.save()
    messages.success(request, "Payment declined.")
    return redirect('transactions:list')


@login_required
def request_money_email(request):
    # EMAIL_BACKEND has been set to console to send email content to console
    context = {'active_tab': 'request_email'}
    if request.method == 'POST':
        request_form = RequestForm(request.POST)
        if request_form.is_valid():
            receiver_email = request_form.cleaned_data['receiver_email']
            amount = request_form.cleaned_data['amount']
            currency = request_form.cleaned_data['currency']

            # Retrieve the user object for the given email, if exists
            try:
                requested_from = User.objects.get(email=receiver_email)

            except User.DoesNotExist:
                messages.error(request, "No user with this email found.")
                return render(request, 'transactions/send_and_receive.html', {'form': request_form})

            # Create the money request instance
            money_request = MoneyRequest.objects.create(
                requester=request.user,
                requested_from=requested_from,
                amount_requested=amount,
                currency=currency
            )

            # Email the receiver with django's send_email module
            send_mail(
                'Money Request',
                f"You have received a money request from {request.user.get_full_name()}.",
                None,
                [requested_from.email],
                fail_silently=False,
                html_message=f"""<p>{request.user.get_full_name()} sent you a money request.</p>
                                 <p><strong>Amount requested:</strong> {amount} {currency}</p>
                                 <a href="{request.build_absolute_uri(reverse('transactions:handle_payment', args=[money_request.id]))}">Pay Now</a>
                                 <p>or</p>
                                 <a href="{request.build_absolute_uri(reverse('transactions:decline_payment', args=[money_request.id]))}">Decline</a>""",
            )
            messages.success(request, 'Money request sent successfully.')
            return redirect('transactions:list')
    else:
        request_form = RequestForm()
        context['request_form'] = request_form

    # context = {'request_form': request_form, 'active_tab': 'request'}
    return render(request, 'transactions/send_and_receive.html', context)


def send_money(request):
    context = {'active_tab': 'send'}
    if request.method == 'POST':
        send_form = TransferForm(request.POST, initial={'user': request.user})
        if send_form.is_valid():
            receiver_username = send_form.cleaned_data['receiver']
            amount = str(send_form.cleaned_data['amount'])
            selected_currency = send_form.cleaned_data['currency']

            # Retrieve accounts
            sender_account = get_object_or_404(Account, user=request.user)
            receiver_account = get_object_or_404(Account, user__username=receiver_username)

            if receiver_account == sender_account:  # Ensure that the receiver is not the same as the sender
                messages.error(request, "You cannot transfer money to yourself.")
                send_form = TransferForm()
                context['send_form'] = send_form
                return render(request, 'transactions/send_and_receive.html', context)

            if selected_currency != receiver_account.currency:
                messages.error(request, "The selected currency must be the same as the receiver's currency.")
                send_form = TransferForm()
                context['send_form'] = send_form
                return render(request, 'transactions/send_and_receive.html', context)

            request.session['transaction_data'] = {
                'amount': amount,
                'recipient': receiver_account.user.username,
                'recipient_currency': receiver_account.currency,
                'sender_currency': sender_account.currency
                # Using session for conversion rate as it may change before the user confirms the transaction
            }
            return redirect('transactions:transaction_summary')
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        send_form = TransferForm()
        context['send_form'] = send_form
    return render(request, 'transactions/send_and_receive.html', context)


@login_required
def send_and_receive(request, tab="send"):
    # context = {'active_tab': tab}
    if tab == "send":
        return send_money(request)
    elif tab == "request_email":
        return request_money_email(request)
    elif tab == "request_web":
        return request_money_web(request)


@login_required
def transaction_summary(request):
    transaction_data = request.session.get('transaction_data')
    if not transaction_data:
        messages.error(request, 'Transaction data is missing.')
        return redirect('transactions:send_money')

    conversion_rate = get_conversion_rate(transaction_data['sender_currency'], transaction_data['recipient_currency'])
    converted_amount = api_converter2(Decimal(transaction_data['amount']), transaction_data['sender_currency'], transaction_data['recipient_currency'])

    context = {
        'amount': transaction_data['amount'],
        'recipient': transaction_data['recipient'],
        'recipient_currency': transaction_data['recipient_currency'],
        'sender_currency': transaction_data['sender_currency'],
        'conversion_rate': conversion_rate,
        'converted_amount': converted_amount
    }
    return render(request, 'transactions/transaction_summary.html', context)


@login_required
def confirm_transaction(request):
    if request.method == 'POST':
        transaction_data = request.session.get('transaction_data')
        if not transaction_data:
            messages.error(request, 'No transaction data found.')
            return redirect('transactions:send_money')

        with db_transaction.atomic():
            sender_account = Account.objects.select_for_update().get(user=request.user)
            receiver = User.objects.get(username=transaction_data['recipient'])
            amount = Decimal(transaction_data['amount'])
            currency = transaction_data['recipient_currency']
            receiver_account = Account.objects.select_for_update().get(user=receiver)

            # Convert the amount to the receiver's currency if different
            if sender_account.currency != receiver_account.currency:
                amount = api_converter2(amount, sender_account.currency, receiver_account.currency)

            # Create the transaction record
            Transaction.objects.create(
                sender=request.user,
                receiver=receiver,
                amount=amount,
                currency=currency
            )

            # Update the sender's and receiver's account balances
            sender_account.balance -= amount  # Deduct the amount entered from the sender's balance
            sender_account.save()
            receiver_account.balance += amount  # Add the converted amount to the receiver's balance
            receiver_account.save()

            del request.session['transaction_data']
            messages.success(request, "Transfer successful.")
            return redirect('transactions:list')  # redirect to a success page
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def transaction_list(request):
    # Get all transactions where the user is either the sender or the receiver
    transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)).order_by('-timestamp')  # order it by timestamp
    moneyrequest = MoneyRequest.objects.filter( Q(requester=request.user) | Q(requested_from=request.user)).order_by('-created_at')
    return render(request, 'transactions/transactions.html', {'transactions': transactions, 'moneyRequest': moneyrequest})
