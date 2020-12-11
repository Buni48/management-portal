from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('list/', views.licensesList, name = 'licenses_list'),
    path('create/', views.create, name = 'licenses_create'),
    path('save/', views.save, name = 'licenses_save'),
]
