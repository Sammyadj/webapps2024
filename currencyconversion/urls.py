from django.urls import path
from . import views

app_name = 'currencyconversion'

urlpatterns = [
    path('exchange_rate/', views.exchange_rate, name='exchange_rate'),
]