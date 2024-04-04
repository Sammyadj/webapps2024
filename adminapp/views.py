from register.models import User
from django.shortcuts import render, redirect, get_object_or_404
from transactions.models import Transaction
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required, user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib import messages



# a custom decorator to check if the user is an admin (superuser) before allowing access to the view:
def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@staff_member_required
def view_users(request):
    users = User.objects.all()
    return render(request, 'adminapp/view_users.html', {'users': users})


@staff_member_required()
def view_transactions(request):
    transactions = Transaction.objects.all()
    return render(request, 'adminapp/view_transactions.html', {'transactions': transactions})


@staff_member_required()
def register_admin(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_admin = form.save(commit=False)
            new_admin.is_staff = True
            new_admin.is_superuser = True  # or use is_staff if you want a staff member that's not a superuser
            new_admin.save()
            messages.success(request, 'New admin registered successfully.')
            return redirect('adminapp:view_users')
        else:
            messages.error(request, 'Error registering new admin.')
    else:
        form = UserCreationForm()

    return render(request, 'adminapp/register_admin.html', {'form': form})


@login_required
def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # Allow any logged-in staff member to make another user an admin
    if 'make_admin' in request.POST:
        user.is_staff = True
        user.save()
        messages.success(request, f"{user.username} has been made an admin.")
        user.refresh_from_db()
        return redirect('adminapp:user_profile', user_id=user_id)

    # Only superusers can remove admin rights, and cannot remove their own rights
    if 'remove_admin' in request.POST and request.user.is_superuser and user != request.user:
        user.is_staff = False
        user.is_superuser = False
        user.save()
        messages.success(request, f"Admin rights removed from {user.username}.")
        user.refresh_from_db()
        return redirect('adminapp:user_profile', user_id=user_id)

    return render(request, 'adminapp/user_profile.html', {'profile_user': user})


# This method is only accessible by superusers
@admin_required
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, pk=user_id)
    # Prevent an admin from deleting themselves
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('view_users')

    user_to_delete.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('adminapp:view_users')
