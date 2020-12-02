from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from heartbeat.models import Heartbeat
from .models import License

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('licenses_list')

def licensesList(request: WSGIRequest) -> HttpResponse:
    heartbeats = Heartbeat.getHeartbeatsMissing()
    licenses   = License.getLicenses()
    context = {
        'heartbeats': heartbeats,
        'licenses'  : licenses,
    }
    return render(request, 'licenses/list.html', context)
