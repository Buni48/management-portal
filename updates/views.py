from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from heartbeat.controllers import HeartbeatController
from .controllers import UpdateController

def index(request: WSGIRequest) -> HttpResponseRedirect:
    """
    When the app root is called. Redirects to the update list.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the update list
    """
    return redirect('updates_list')

def updates_list(request: WSGIRequest) -> HttpResponse:
    """
    When the update list is called. Renders the update list.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: update list
    """
    heartbeats    = HeartbeatController.read()
    used_products = UpdateController.read()
    context       = {
        'heartbeats'    : heartbeats,
        'used_products' : used_products,
    }
    return render(request, 'updates/list.html', context)
