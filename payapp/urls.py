from django.urls import path
from . import views

app_name = 'payapp'

urlpatterns = [
    path('mail/', views.mail_list, name='mail_list'),
    path('mail/<int:email_id>/', views.mail_detail, name='mail_detail'),
    path('mail/<int:email_id>/confirm', views.confirm_payment, name='confirm_payment'),
    path('mail/<int:email_id>/decline', views.decline_payment, name='decline_payment'),
    path('mail/<int:email_id>/cancel', views.cancel_payment, name='cancel_payment'),
    # ... your other URLs ...
]
