from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.customer_list, name='customers_list'),
    path('<int:id>/', views.customer, name='customer'),
    path('<int:customer_id>/locations/create/', views.create_location, name='locations_create'),
    path('<int:customer_id>/locations/edit/<int:id>/', views.edit_location, name='locations_edit'),
    path('save-location/', views.save_location, name='locations_save'),
    path('delete-location/', views.delete_location, name='locations_delete'),
    path('create/', views.create, name='customers_create'),
    path('edit/<int:id>/', views.edit, name = 'customers_edit'),
    path('save/', views.save, name='customers_save'),
    path('delete/<int:id>/', views.delete, name ='customers_delete'),
    path('contact-persons/', views.contact_persons, name ='contact_persons'),
    path('<int:customer_id>/locations/<int:location_id>/contact_persons/create', views.create_contact_person, name='contact_persons_create'),
    path('<int:customer_id>/locations/<int:location_id>/contact_persons/edit/<int:id>', views.edit_contact_person, name='contact_persons_edit'),
    path('save-contact-person/', views.save_contact_person, name='contact_persons_save'),
    path('delete-contact-person/', views.delete_contact_person, name='contact_persons_delete'),
]
