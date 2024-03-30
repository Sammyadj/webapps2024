from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TransferForm, RequestForm, User
from .models import Transaction, MoneyRequest
from django.db.models import Q
from payapp.models import Account
from currencyconversion.services import convert_currency
from django.db import transaction as db_transaction
from django.contrib import messages

@login_required
def request_money(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            receiver_email = form.cleaned_data['receiver_email']
            amount = form.cleaned_data['amount']
            currency = form.cleaned_data['currency']
            # Assuming you have a method to get the user object from the email
            requested_from = User.objects.get(email=receiver_email)
            # Create the money request instance
            money_request = MoneyRequest.objects.create(
                requester=request.user,
                requested_from=requested_from,
                amount_requested=amount,
                currency=currency
            )
            # Logic to send email to the receiver with the request link goes here
            # ...
            messages.success(request, 'Money request sent successfully.')
            return redirect('transactions:list')
    else:
        form = RequestForm()
    context = {'form': form, 'active_tab': 'request'}
    return render(request, 'transactions/send_and_receive.html', context)

def send_money(request):
    if request.method == 'POST':
        form = TransferForm(request.POST, initial={'user': request.user})
        if form.is_valid():
            receiver = form.cleaned_data['receiver']
            amount = form.cleaned_data['amount']
            currency = form.cleaned_data['currency']

            # Ensure that the receiver is not the same as the sender
            if receiver == request.user:
                messages.error(request, "You cannot transfer money to yourself.")
                return render(request, 'transactions/transfer.html', {'form': form})

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
        form = TransferForm(initial={'user': request.user})

    context = {'form': form, 'active_tab': 'send'} # Pass the form to the context

    return render(request, 'transactions/send_and_receive.html', context)

@login_required
def send_and_receive(request, tab="send"):
    context = {'active_tab': tab}
    if tab == "send":
        return send_money(request)
    elif tab == "request":
        return request_money(request)
    else:
        # If an invalid tab is provided, redirect to the default 'send' tab
        return redirect('transactions:send_and_receive', tab='send')

@login_required
def transaction_list(request):
    # Get all transactions where the user is either the sender or the receiver
    transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')
    return render(request, 'transactions/transactions.html', {'transactions': transactions})