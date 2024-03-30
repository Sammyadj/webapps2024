from django.urls import path
from . import views

app_name = 'adminapp'

urlpatterns = [
    path('users/', views.view_users, name='view_users'),
    path('transactions/', views.view_transactions, name='view_transactions'),
    path('register-admin/', views.register_admin, name='register_admin'),
    path('users/<int:user_id>/', views.user_profile, name='user_profile'),
]
