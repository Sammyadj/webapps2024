from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # path('transfer/', views.transfer, name='transfer'),
    path('list/', views.transaction_list, name='list'),
    path('send_and_receive/', views.send_and_receive, name='send_and_request_homepage'),
    path('send_and_receive/<str:tab>/', views.send_and_receive, name='send_and_receive'),
]
