from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.heartbeat, name='index'),
    path('list/', views.heartbeatList, name='heartbeat_list'),
]
