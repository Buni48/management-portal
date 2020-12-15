from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.customerList, name='customers_list'),
    path('customer/<int:id>/', views.customer, name='customer'),
    path('create/', views.create, name='customers_create'),
    path('edit/<int:id>/', views.edit, name = 'customers_edit'),
    path('save/', views.save, name='customers_save'),
    path('delete/<int:id>/', views.delete, name = 'customers_delete'),
]
