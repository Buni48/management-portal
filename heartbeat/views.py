from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from .models import Heartbeat

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('heartbeat_list')

def heartbeatList(request: WSGIRequest) -> HttpResponse:
    heartbeats = Heartbeat.getHeartbeats()
    context = {
        'heartbeats'    : heartbeats,
        'count_missing' : Heartbeat.getCountMissing(heartbeats),
    }
    return render(request, 'heartbeat/list.html', context)
