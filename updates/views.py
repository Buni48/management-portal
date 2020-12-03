from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from heartbeat.models import Heartbeat
from licenses.models import UsedSoftwareProduct

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('updates_list')

def updatesList(request: WSGIRequest) -> HttpResponse:
    heartbeats   = Heartbeat.getHeartbeats()
    usedProducts = UsedSoftwareProduct.getUsedProducts()
    context      = {
        'heartbeats'    : heartbeats,
        'used_products' : usedProducts,
    }
    return render(request, 'updates/list.html', context)
