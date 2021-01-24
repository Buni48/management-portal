from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('list/', views.licenses_list, name = 'licenses_list'),
    path('create/', views.create, name = 'licenses_create'),
    path('edit/<int:id>/', views.edit, name = 'licenses_edit'),
    path('<int:old_license_id>/create/', views.create_replace_license, name = 'licenses_create_replace'),
    path('<int:old_license_id>/edit/<int:id>', views.edit_replace_license, name = 'licenses_edit_replace'),
    path('save/', views.save, name = 'licenses_save'),
    path('delete/<int:id>/', views.delete, name = 'licenses_delete'),
    path('settings/', views.settings, name = 'licenses_settings'),
]
