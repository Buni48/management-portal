from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from heartbeat.controllers import HeartbeatController
from .controllers import UpdateController

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('updates_list')

def updatesList(request: WSGIRequest) -> HttpResponse:
    heartbeats   = HeartbeatController.read()
    usedProducts = UpdateController.read()
    context      = {
        'heartbeats'    : heartbeats,
        'used_products' : usedProducts,
    }
    return render(request, 'updates/list.html', context)
