from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from .controllers import HeartbeatController

def index(request: WSGIRequest) -> HttpResponseRedirect:
    """
    When the app root is called. Redirects to the heartbeat list.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the heartbeat list
    """
    return redirect('heartbeat_list')

def heartbeatList(request: WSGIRequest) -> HttpResponse:
    """
    When the heartbeat list is called. Renders the heartbeat list.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: heartbeat list
    """
    usedProducts = HeartbeatController.read()
    countMissing = HeartbeatController.getCountMissing(usedProducts)
    context = {
        'used_products' : usedProducts,
        'count_missing' : countMissing,
    }
    return render(request, 'heartbeat/list.html', context)
