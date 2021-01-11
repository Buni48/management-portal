from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from .controllers import HeartbeatController

def index(request: WSGIRequest) -> HttpResponseRedirect:
    """
    When the app root is called. Redirects to the heartbeat list.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the heartbeat list
    """
    return redirect('heartbeat_list')

def heartbeat_list(request: WSGIRequest) -> HttpResponse:
    """
    When the heartbeat list is called. Renders the heartbeat list.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: heartbeat list
    """
    used_products = HeartbeatController.read()
    count_missing = HeartbeatController.get_count_missing(used_products)
    context       = {
        'used_products' : used_products,
        'count_missing' : count_missing,
    }
    return render(request, 'heartbeat/list.html', context)
