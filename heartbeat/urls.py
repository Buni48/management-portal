from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.heartbeat_list, name='heartbeat_list'),
]
