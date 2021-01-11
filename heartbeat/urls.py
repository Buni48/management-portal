from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.heartbeat, name='index'),
    path('list/', views.heartbeat_list, name='heartbeat_list'),
]
