from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse

def index(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

def home(request: WSGIRequest) -> HttpResponse:
    return render(request, 'home.html')

def login(request: WSGIRequest) -> HttpResponse:
    return redirect('user_management:login')

def logout(request: WSGIRequest) -> HttpResponse:
    return redirect('user_management:logout')
