from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from heartbeat.models import Heartbeat

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('licences_list')

def licencesList(request: WSGIRequest) -> HttpResponse:
    heartbeats = Heartbeat.getHeartbeatsMissing()
    context = {
        'heartbeats': heartbeats,
    }
    return render(request, 'licences/list.html', context)
