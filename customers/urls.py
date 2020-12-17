from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.customerList, name='customers_list'),
    path('<int:id>/', views.customer, name='customer'),
    path('<int:customer_id>/locations/create/', views.createLocation, name='locations_create'),
    path('<int:customer_id>/locations/edit/<int:id>/', views.editLocation, name='locations_edit'),
    path('save-location/', views.saveLocation, name='locations_save'),
    path('delete-location/', views.deleteLocation, name='locations_delete'),
    path('create/', views.create, name='customers_create'),
    path('edit/<int:id>/', views.edit, name = 'customers_edit'),
    path('save/', views.save, name='customers_save'),
    path('delete/<int:id>/', views.delete, name = 'customers_delete'),
]
