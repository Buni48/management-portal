from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from heartbeat.controllers import HeartbeatController
from .controllers import UpdateController

def index(request: WSGIRequest) -> HttpResponseRedirect:
    """
    When the app root is called. Redirects to the update list.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the update list
    """
    return redirect('updates_list')

def updatesList(request: WSGIRequest) -> HttpResponse:
    """
    When the update list is called. Renders the update list.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: update list
    """
    heartbeats   = HeartbeatController.read()
    usedProducts = UpdateController.read()
    context      = {
        'heartbeats'    : heartbeats,
        'used_products' : usedProducts,
    }
    return render(request, 'updates/list.html', context)
