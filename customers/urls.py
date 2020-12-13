from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.customerList, name='customers_list'),
    path('customer/<int:id>/', views.customer, name='customer'),
    path('create/', views.addCustomer, name='createCustomer'),
    path('save/', views.saveCustomer, name='saveCustomer'),
]
