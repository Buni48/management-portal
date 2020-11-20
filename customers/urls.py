from django.urls import path, include
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.customerList, name='customers_list'),
    path('customer/', views.customer, name='customer'),
]
