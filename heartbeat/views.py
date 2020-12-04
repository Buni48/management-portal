from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from .controllers import HeartbeatController

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('heartbeat_list')

def heartbeatList(request: WSGIRequest) -> HttpResponse:
    usedProducts = HeartbeatController.read()
    countMissing = HeartbeatController.getCountMissing(usedProducts)
    context = {
        'used_products' : usedProducts,
        'count_missing' : countMissing,
    }
    return render(request, 'heartbeat/list.html', context)
