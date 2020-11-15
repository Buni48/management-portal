from django.contrib import admin
from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    path('authentication/', views.authentication, name='authentication'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('logged-out/', views.loggedOut, name='logged_out'),
    path('settings/', views.settings, name='settings'),
]
