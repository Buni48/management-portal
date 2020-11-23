from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from heartbeat.models import Heartbeat

def index(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

def home(request: WSGIRequest) -> HttpResponse:
    heartbeats = Heartbeat.getHeartbeatsMissing()
    context = {
        'heartbeats': heartbeats,
    }
    return render(request, 'home.html', context)

def login(request: WSGIRequest) -> HttpResponse:
    return redirect('user_management:login')

def logout(request: WSGIRequest) -> HttpResponse:
    return redirect('user_management:logout')
