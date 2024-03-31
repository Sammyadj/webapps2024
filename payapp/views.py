from register.models import User
from .forms import MoneyRequestForm
from .models import Account, UserNotification, UserEmail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

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
def request_money(request):
    context = {'active_tab': 'request_web'}
    if request.method == 'POST':
        money_request_form = MoneyRequestForm(request.POST)
        if money_request_form.is_valid():
            receiver_username = money_request_form.cleaned_data['receiver_username']
            amount = money_request_form.cleaned_data['amount']
            currency = money_request_form.cleaned_data['currency']
            # Assuming you have a way to get the User object from the username
            try:
                recipient = User.objects.get(username=receiver_username)
            except User.DoesNotExist:
                messages.error(request, "No user with this username found.")
                return render(request, 'transactions/send_and_receive.html', {'money_request_form': money_request_form})

            # Create the in-app email instance
            UserEmail.objects.create(
                to_user=recipient,
                subject='Money Request',
                body=f"{request.user.get_full_name()} sent you a money request. Amount requested: {amount} {currency}.",
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
    # Your logic to confirm the payment
    if request.method == 'POST':
        pass
    return redirect('payapp:mail_list')

@login_required
def decline_payment(request, email_id):
    # Your logic to decline the payment
    messages.success(request, "Payment declined.")
    return redirect('payapp:mail_list')

@login_required
def cancel_payment(request, email_id):
    # Your logic to cancel the payment
    return redirect('payapp:mail_list')
