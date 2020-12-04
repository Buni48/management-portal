from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from heartbeat.controllers import HeartbeatController
from .controllers import LicenseController

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('licenses_list')

def licensesList(request: WSGIRequest) -> HttpResponse:
    heartbeats = HeartbeatController.read()
    licenses   = LicenseController.read()
    context = {
        'heartbeats': heartbeats,
        'licenses'  : licenses,
    }
    return render(request, 'licenses/list.html', context)
