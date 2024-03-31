from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import TransferForm, RequestForm, User, PaymentConfirmationForm
from .models import Transaction, MoneyRequest
from django.db.models import Q
from payapp.models import Account
from currencyconversion.services import convert_currency
from django.db import transaction as db_transaction
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from payapp.views import request_money as request_money_web


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
        # If you're using the Django form
        form = PaymentConfirmationForm()  # Uncomment if using the Django form approach
        return render(request, 'transactions/handle_payment.html', {'form': form, 'money_request': money_request})
        # return render(request, 'transactions/handle_payment.html', {'money_request': money_request})


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
def request_money(request):
    context = {'active_tab': 'request'}
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

            # Email the receiver
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
            receiver = send_form.cleaned_data['receiver']
            amount = send_form.cleaned_data['amount']
            currency = send_form.cleaned_data['currency']

            # Ensure that the receiver is not the same as the sender
            if receiver == request.user:
                messages.error(request, "You cannot transfer money to yourself.")
                return render(request, 'transactions/send_and_receive.html', {'form': send_form})

            # Start a database transaction
            with db_transaction.atomic():
                sender_account = Account.objects.select_for_update().get(
                    user=request.user)  # ensures that the rows are locked until the end of the transaction block.
                receiver_account = Account.objects.select_for_update().get(user=receiver)

                # Convert the amount to the receiver's currency if different
                if sender_account.currency != receiver_account.currency:
                    amount = convert_currency(amount, sender_account.currency, receiver_account.currency)

                # Create the transaction record
                Transaction.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    amount=amount,
                    currency=currency
                )

                # Update the sender's and receiver's account balances
                sender_account.balance -= amount
                sender_account.save()

                receiver_account.balance += amount
                receiver_account.save()
            messages.success(request, "Transfer successful.")
            return redirect('transactions:list')
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        send_form = TransferForm(initial={'user': request.user})
        context['send_form'] = send_form

    # context = {'form': form, 'active_tab': 'send'} # Pass the form to the context

    return render(request, 'transactions/send_and_receive.html', context)


@login_required
def send_and_receive(request, tab="send"):
    # context = {'active_tab': tab}
    if tab == "send":
        return send_money(request)
    elif tab == "request":
        return request_money(request)
    elif tab == "request_web":
        return request_money_web(request)


@login_required
def transaction_list(request):
    # Get all transactions where the user is either the sender or the receiver
    transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')
    return render(request, 'transactions/transactions.html', {'transactions': transactions})
