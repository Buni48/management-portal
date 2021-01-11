from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('list/', views.licenses_list, name = 'licenses_list'),
    path('create/', views.create, name = 'licenses_create'),
    path('edit/<int:id>/', views.edit, name = 'licenses_edit'),
    path('save/', views.save, name = 'licenses_save'),
    path('delete/<int:id>/', views.delete, name = 'licenses_delete'),
]
