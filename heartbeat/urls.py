from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.heartbeatList, name='heartbeat_list'),
    path('history/', views.history, name='heartbeat_history'),
]
