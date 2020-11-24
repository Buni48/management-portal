from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from heartbeat.models import Heartbeat
from .models import Licence

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('licences_list')

def licencesList(request: WSGIRequest) -> HttpResponse:
    heartbeats = Heartbeat.getHeartbeatsMissing()
    licences   = Licence.getLicences()
    context = {
        'heartbeats': heartbeats,
        'licences'  : licences,
    }
    return render(request, 'licences/list.html', context)
